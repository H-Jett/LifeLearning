#!/usr/bin/env python3
"""《系统学缠论》书稿一致性与合规校验。

这本书和书架上另外四本的校验重点**刻意不同**：茶 / 珠宝 / 咖啡 / 酒查的是
"数值有没有出处"，这本书查的是**合规红线**与**命题有没有打标签**——
因为这本书的风险不在写错一个折射率，而在不小心写成了荐股。

检查项（任何一项失败 → 退出码 1）：

  合规类（本书特有，最优先）
   1. 股票代码     ——正文禁止出现 6 位 A 股代码，例子一律匿名化（"某标的"）
   2. 承诺性措辞   ——"稳赚 / 保证盈利 / 100% 安全"等只允许出现在引用块里（作为被评注的原文）
   3. 合规提示     ——正式章节结尾必须带 ⚖️ 风险与合规提示

  体例类
   4. 命题标签     ——正式章节必须用〔定义〕〔推论〕〔经验断言〕〔不可证伪〕至少一种
   5. 章节结构     ——必须有「常见说法辨析」「思考题」「本章实操」，实操给 🅐 / 🅑 两档
   6. 证据强度     ——「常见说法辨析」里必须出现 ✅ / ⚠️ / ❌ / 缺乏证据

  引用与链接类
   7. 课次登记     ——正文出现的「第 NN 课」必须在 docs/sources.md 里登记过
   8. 思考题锚点   ——章节引用的 `qa/xxx.md#qN` 必须真的存在 <a id="qN">
   9. 术语表锚点   ——章节引用的 `glossary.md#slug` 必须真的存在 <a id="slug">
  10. 术语表节号   ——glossary.md 的 `## ` 标题不许重复（否则锚点会打架）

  可移植性类
  11. 绝对路径     ——公开仓库禁止出现本机绝对路径（会泄漏用户名 / 目录布局）
  12. admonition   ——禁止 MkDocs 专有的 `!!! note`（纯 Markdown 阅读器会露原文）
  13. 图片外链     ——禁止 ![](http...) 热链他人图片（版权 + 失效风险）

用法：
    python scripts/check_book.py          # 全量检查
    python scripts/check_book.py -v       # 附带逐文件明细
    python scripts/check_book.py --quiet  # 只在失败时输出
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
SOURCES = DOCS / "sources.md"
GLOSSARY = DOCS / "glossary.md"

# ---------- 各检查项的正则 ----------

# 本机绝对路径：/volume/... /root/... /home/xxx/... C:\...
ABS_PATH_RE = re.compile(
    r"(?:^|[\s\"'`(])(/(?:volume|root|home|mnt|data)/[\w./-]+|[A-Za-z]:\\\\[\w\\\\.-]+)"
)
ADMONITION_RE = re.compile(r"^\s*(?:!!!|\?\?\?)\s+\w+", re.MULTILINE)
QA_LINK_RE = re.compile(r"\]\(([^)]*qa/([\w-]+)\.md)#(q\d+)\)")
GLOSSARY_LINK_RE = re.compile(r"\]\(([^)]*glossary\.md)#([\w-]+)\)")
ANCHOR_RE = re.compile(r'<a\s+id="([\w-]+)"\s*>')
IMG_EXTERNAL_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)]+)\)")

# 原著课次引用：「第 17 课」。sources.md 用同一格式登记。
LESSON_RE = re.compile(r"第\s?(\d{1,3})\s?课")

# A 股代码：沪 6 开头、深 0/3 开头、北 4/8 开头，六位。
# 刻意从严——宁可误伤一个普通六位数（换个写法即可），也不许漏掉一个真代码。
STOCK_CODE_RE = re.compile(r"(?<![\d.])([03468]\d{5})(?![\d.%])")

# 承诺性措辞：只允许出现在引用块（作为被本书评注的原文主张）
PROMISE_WORDS = (
    "稳赚", "包赚", "必赚", "躺赚", "保证盈利", "保证收益", "保本",
    "战无不胜", "绝对安全", "100% 安全", "100%安全",
)

# 正式章节文件：NN-name.md（排除 00-intro / summary / project-*）
CHAPTER_FILE_RE = re.compile(r"^(?!00-)\d{2}-[\w-]+\.md$")

EVIDENCE_MARKS = ("✅", "⚠️", "❌", "缺乏证据")
PROPOSITION_TAGS = ("〔定义〕", "〔推论〕", "〔经验断言〕", "〔不可证伪〕")


def md_files() -> list[Path]:
    return sorted(p for p in DOCS.rglob("*.md"))


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


def strip_code_blocks(text: str) -> str:
    """去掉围栏代码块与行内代码，避免代码示例里的路径 / 数字误报。"""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return re.sub(r"`[^`\n]*`", "", text)


def quoted_lines(text: str) -> set[int]:
    """引用块所在的行号集合（承诺性措辞只允许出现在这里）。"""
    return {i for i, line in enumerate(text.splitlines()) if line.lstrip().startswith(">")}


def collect_anchors(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(ANCHOR_RE.findall(path.read_text(encoding="utf-8")))


def check_glossary_sections(errors: list[str]) -> None:
    """术语表的 `## ` 节标题不许重复——重复会让自动锚点相互覆盖。"""
    if not GLOSSARY.exists():
        errors.append("docs/glossary.md 不存在")
        return
    heads = re.findall(r"^##\s+(.+)$", GLOSSARY.read_text(encoding="utf-8"), re.MULTILINE)
    seen: set[str] = set()
    for h in heads:
        key = h.strip()
        if key in seen:
            errors.append(f"docs/glossary.md: 节标题重复 `## {key}`（锚点会冲突）")
        seen.add(key)


def main() -> int:
    ap = argparse.ArgumentParser(description="《系统学缠论》书稿校验")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印逐文件明细")
    ap.add_argument("--quiet", action="store_true", help="只在失败时输出")
    args = ap.parse_args()

    def say(msg: str) -> None:
        if not args.quiet:
            print(msg)

    files = md_files()
    if not files:
        print("✗ docs/ 下没有找到任何 .md，书的结构不对")
        return 1

    say(f"检查 {len(files)} 个 Markdown 文件 ...")

    errors: list[str] = []
    warnings: list[str] = []

    glossary_anchors = collect_anchors(GLOSSARY)
    sources_text = SOURCES.read_text(encoding="utf-8") if SOURCES.exists() else ""
    if not sources_text:
        errors.append("docs/sources.md 不存在或为空（所有出处必须集中登记）")
    registered_lessons = set(LESSON_RE.findall(sources_text))

    qa_anchor_cache: dict[Path, set[str]] = {}

    for f in files:
        raw = f.read_text(encoding="utf-8")
        body = strip_code_blocks(raw)
        quoted = quoted_lines(body)
        tag = rel(f)
        n_before = len(errors)
        is_chapter = bool(CHAPTER_FILE_RE.match(f.name)) and "chapters/" in tag

        # ---- 合规类 ----

        # 1. 股票代码
        for m in STOCK_CODE_RE.finditer(body):
            errors.append(
                f"{tag}: 出现疑似 A 股代码 `{m.group(1)}`"
                "（合规红线：例子必须匿名化成「某标的」；若是普通数字请换个写法）"
            )

        # 2. 承诺性措辞——只允许在引用块里（作为被评注的原文）
        for i, line in enumerate(body.splitlines()):
            if i in quoted:
                continue
            for w in PROMISE_WORDS:
                if w in line:
                    errors.append(
                        f"{tag}: 正文出现承诺性措辞「{w}」"
                        "（只允许作为被评注的原文出现在引用块 `>` 里）"
                    )

        # 3. 合规提示
        if is_chapter and "⚖️" not in body:
            errors.append(f"{tag}: 正式章节结尾缺 ⚖️ 风险与合规提示（措辞见 CLAUDE.md §5）")

        # ---- 体例类 ----

        # 4. 命题标签
        if is_chapter and not any(t in body for t in PROPOSITION_TAGS):
            errors.append(
                f"{tag}: 正式章节没有用命题标签"
                "（每章至少要出现〔定义〕〔推论〕〔经验断言〕〔不可证伪〕之一）"
            )

        # 5 / 6. 章节固定结构
        if is_chapter:
            if "常见说法辨析" not in body:
                errors.append(f"{tag}: 正式章节缺「常见说法辨析」小节")
            elif not any(mark in body for mark in EVIDENCE_MARKS):
                errors.append(f"{tag}: 「常见说法辨析」里没有证据强度标记（✅/⚠️/❌/缺乏证据）")
            if "思考题" not in body:
                errors.append(f"{tag}: 正式章节缺「思考题」小节")
            if "本章实操" not in body:
                errors.append(f"{tag}: 正式章节缺「本章实操」小节")
            else:
                if "🅐" not in body:
                    errors.append(f"{tag}: 本章实操缺 🅐 手工版（读者不一定会写代码）")
                if "🅑" not in body:
                    errors.append(f"{tag}: 本章实操缺 🅑 代码版")
            if "🔎" not in body:
                warnings.append(f"{tag}: 建议补一个 🔎「看盘时的用处」小节")

        # ---- 引用与链接类 ----

        # 7. 课次登记（sources.md 自己不查）
        if f != SOURCES:
            for n in set(LESSON_RE.findall(body)):
                if n not in registered_lessons:
                    errors.append(f"{tag}: 引用了「第 {n} 课」但未在 docs/sources.md 登记")

        # 8. 思考题锚点
        for link, qa_name, anchor in QA_LINK_RE.findall(body):
            target = (f.parent / link).resolve()
            if not target.exists():
                errors.append(f"{tag}: 答案册不存在 → {link}")
                continue
            if target not in qa_anchor_cache:
                qa_anchor_cache[target] = collect_anchors(target)
            if anchor not in qa_anchor_cache[target]:
                errors.append(f'{tag}: {qa_name}.md 里缺锚点 <a id="{anchor}">')

        # 9. 术语表锚点
        for _link, anchor in GLOSSARY_LINK_RE.findall(body):
            if anchor not in glossary_anchors:
                errors.append(f'{tag}: glossary.md 里缺术语锚点 <a id="{anchor}">')

        # ---- 可移植性类 ----

        # 11. 绝对路径
        for m in ABS_PATH_RE.finditer(body):
            errors.append(f"{tag}: 出现本机绝对路径 `{m.group(1)}`（仓库内只允许相对路径）")

        # 12. MkDocs 专有 admonition
        for m in ADMONITION_RE.finditer(body):
            errors.append(f"{tag}: 出现 admonition `{m.group(0).strip()}`（改用引用块 `>` + 加粗）")

        # 13. 图片外链
        for url in IMG_EXTERNAL_RE.findall(body):
            errors.append(f"{tag}: 禁止外链图片 {url[:60]}...（改用 Mermaid / 内联 SVG）")

        if args.verbose:
            mark = "✗" if len(errors) > n_before else "✓"
            print(f"  {mark} {tag}")

    # 10. 术语表节号
    check_glossary_sections(errors)

    for w in warnings:
        say(f"⚠ {w}")

    if errors:
        print(f"\n✗ 校验失败，{len(errors)} 处问题：")
        for e in errors:
            print(f"  - {e}")
        return 1

    say(f"✓ 全部通过（{len(files)} 个文件，{len(warnings)} 条建议）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
