#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TeaLearning 校验脚本：提交前跑一遍，配合 `mkdocs build --strict` 使用。

`mkdocs build --strict` 能抓到坏的**文件**链接，但抓不到下面这些问题，
所以本脚本补上四项检查：

  1. **锚点检查**：所有指向 `xxx.md#anchor` 的站内链接，目标文件里必须真的有
     `<a id="anchor">` 或同名标题（思考题跳转、术语表跳转全靠这个）。
  2. **绝对路径检查**：仓库内禁止出现绝对路径（会泄漏用户名/机器目录布局）。
  3. **孤立答案检查**：每个 `docs/qa/*.md` 里的 q1..qN 锚点，是否都被某一章引用到。
  4. **出处提醒**（warning，不阻塞）：出现百分比数字的章节，是否在同段落附近提到
     出处关键词（GB/T、教科书简称、"经验值"、"典型区间"）。

用法：
    python scripts/check_book.py            # 全量检查，有 error 则退出码 1
    python scripts/check_book.py --quiet    # 只报 error，不报 warning
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from urllib.parse import unquote

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("check_book")

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"

# [文字](路径#锚点) —— 只关心站内 .md 链接
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+\.md)(#[^)\s]+)?\)")
# 外部链接前缀：这些不是站内文件，即使以 .md 结尾也要跳过
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "//")
# 显式 HTML 锚点 <a id="xxx"></a>
ANCHOR_RE = re.compile(r'<a\s+id="([^"]+)"')
# Markdown 标题（用于 toc 自动锚点的兜底判断）
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
# 绝对路径：以 home / Users / root / volume / mnt / data / opt / tmp 打头的 POSIX 路径，
# 以及 Windows 盘符路径。首段后必须紧跟字母数字，避免匹配到本文件里的占位写法。
ABS_PATH_RE = re.compile(
    r"(?<![\w`/])(?:/(?:home|Users|root|volume|mnt|data|opt|tmp)/[\w-][\w./-]{2,}"
    r"|[A-Za-z]:\\\\?[\w\\.-]+)"
)
# 出处关键词
SOURCE_HINTS = ("GB/T", "GB ", "教科书", "经验值", "典型区间", "典型在", "standards.md",
                "《茶叶生物化学》", "《制茶学》", "《茶叶审评与检验》", "《中国茶经》",
                "不同资料", "各教材")
PERCENT_RE = re.compile(r"\d+(?:\.\d+)?%")

errors: list[str] = []
warnings: list[str] = []


def slugify(heading: str) -> str:
    """粗略模拟 MkDocs/GitHub 的标题 → 锚点转换（够用即可，只做兜底）。"""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\u4e00-\u9fff\s-]", "", s)
    return re.sub(r"\s+", "-", s).strip("-")


def anchors_of(md: Path) -> set[str]:
    text = md.read_text(encoding="utf-8")
    found = set(ANCHOR_RE.findall(text))
    found |= {slugify(h) for h in HEADING_RE.findall(text)}
    return found


def check_links(md_files: list[Path], anchor_cache: dict[Path, set[str]]) -> None:
    """检查站内 .md 链接的目标文件与锚点都存在。"""
    for md in md_files:
        for target, frag in LINK_RE.findall(md.read_text(encoding="utf-8")):
            if target.startswith(EXTERNAL_PREFIXES):
                continue        # 外部 URL 交给 mkdocs / 人工检查，不在此校验
            dest = (md.parent / unquote(target)).resolve()
            rel = md.relative_to(REPO_ROOT)
            if not dest.exists():
                errors.append(f"{rel}: 链接目标不存在 -> {target}")
                continue
            if frag:
                anchor = unquote(frag[1:])
                if anchor not in anchor_cache.setdefault(dest, anchors_of(dest)):
                    errors.append(
                        f"{rel}: 锚点不存在 -> {target}#{anchor}"
                        f"（目标文件里没有 <a id=\"{anchor}\"> 也没有同名标题）"
                    )


def check_abs_paths(all_files: list[Path]) -> None:
    """仓库内禁止绝对路径。"""
    for f in all_files:
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            m = ABS_PATH_RE.search(line)
            if m:
                errors.append(
                    f"{f.relative_to(REPO_ROOT)}:{lineno}: 出现绝对路径 "
                    f"`{m.group(0)}` —— 仓库内只允许相对路径"
                )


def check_orphan_answers(md_files: list[Path]) -> None:
    """qa/ 里的每个 qN 锚点都应被某一章引用。"""
    referenced: set[tuple[str, str]] = set()
    for md in md_files:
        for target, frag in LINK_RE.findall(md.read_text(encoding="utf-8")):
            if frag and "qa/" in target:
                referenced.add(((md.parent / target).resolve().name, frag[1:]))

    for qa in sorted((DOCS / "qa").glob("*.md")):
        for anchor in ANCHOR_RE.findall(qa.read_text(encoding="utf-8")):
            if anchor.startswith("q") and (qa.name, anchor) not in referenced:
                warnings.append(
                    f"{qa.relative_to(REPO_ROOT)}: 答案 #{anchor} 没有任何章节链接过来"
                )


def check_sources(md_files: list[Path]) -> None:
    """出现百分比的章节，附近应有出处线索（仅提醒）。"""
    for md in md_files:
        if md.parent.name == "qa" or md.name in ("standards.md", "glossary.md"):
            continue
        text = md.read_text(encoding="utf-8")
        has_percent = bool(PERCENT_RE.search(text))
        has_source = any(h in text for h in SOURCE_HINTS)
        if has_percent and not has_source:
            warnings.append(
                f"{md.relative_to(REPO_ROOT)}: 出现了百分比数值但全文没有出处线索"
                "（GB/T、教科书简称、\"经验值\"、\"典型区间\"）—— 按 CLAUDE.md §1 数值必须标出处"
            )


def main() -> int:
    ap = argparse.ArgumentParser(description="TeaLearning 内容校验")
    ap.add_argument("--quiet", action="store_true", help="只报 error，不打印 warning")
    args = ap.parse_args()

    md_files = sorted(DOCS.rglob("*.md"))
    all_files = [
        p for p in REPO_ROOT.rglob("*")
        if p.is_file()
        and ".git/" not in str(p.relative_to(REPO_ROOT))
        and not str(p.relative_to(REPO_ROOT)).startswith(("site/", ".git"))
        and p.suffix in (".md", ".py", ".yml", ".yaml")
    ]
    log.info("检查 %d 个 .md（docs/），%d 个文本文件（全仓库）", len(md_files), len(all_files))

    anchor_cache: dict[Path, set[str]] = {}
    check_links(md_files, anchor_cache)
    check_abs_paths(all_files)
    check_orphan_answers(md_files)
    check_sources(md_files)

    if warnings and not args.quiet:
        for w in warnings:
            log.warning(w)
    for e in errors:
        log.error(e)

    if errors:
        log.error("校验失败：%d 个 error（%d 个 warning）", len(errors), len(warnings))
        return 1
    log.info("校验通过：0 error，%d 个 warning。", len(warnings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
