#!/usr/bin/env python3
"""JewelryLearning 书稿一致性校验。

姊妹书 InfraLearning 靠"真机跑代码"保证正确性，珠宝没有代码可跑，
所以把**可机器检查的纪律**尽量固化在这里，人工只负责查事实。

检查项（任何一项失败 → 退出码 1）：

1. 绝对路径     ——公开仓库禁止出现本机绝对路径（会泄漏用户名 / 目录布局）
2. admonition   ——禁止 MkDocs 专有的 `!!! note`（纯 Markdown 阅读器会露原文）
3. 思考题锚点   ——章节里引用的 `qa/xxx.md#qN` 必须真的存在 <a id="qN">
4. 术语表锚点   ——章节里引用的 `glossary.md#slug` 必须真的存在 <a id="slug">
5. 标准登记     ——正文出现的 GB/T 编号必须在 reference/standards.md 里登记过
6. 图片外链     ——禁止 ![](http...) 热链他人图片（版权 + 失效风险）
7. 章节结构     ——正式章节必须有「思考题」和「本章实操」小节

用法：
    python scripts/check_book.py          # 全量检查
    python scripts/check_book.py -v       # 附带逐文件明细
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"

# ---------- 各检查项的正则 ----------

# 本机绝对路径：/volume/... /root/... /home/xxx/... C:\...
ABS_PATH_RE = re.compile(r"(?:^|[\s\"'`(])(/(?:volume|root|home|mnt|data)/[\w./-]+|[A-Za-z]:\\\\[\w\\\\.-]+)")
ADMONITION_RE = re.compile(r"^\s*(?:!!!|\?\?\?)\s+\w+", re.MULTILINE)
# Markdown 链接里指向 qa 答案册的锚点
QA_LINK_RE = re.compile(r"\]\(([^)]*qa/([\w-]+)\.md)#(q\d+)\)")
GLOSSARY_LINK_RE = re.compile(r"\]\(([^)]*glossary\.md)#([\w-]+)\)")
ANCHOR_RE = re.compile(r'<a\s+id="([\w-]+)"\s*>')
# 正文引用的国标 / 行标编号（GB/T 16552、GB 11887、QB/T 1689、GB/T 16554 …）
STANDARD_RE = re.compile(r"\b((?:GB/T|GB|QB/T|DZ/T|SN/T)\s?\d{3,6})")
IMG_EXTERNAL_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)]+)\)")
# 正式章节文件：NN-name.md（排除 00-intro / summary / project-*）
CHAPTER_FILE_RE = re.compile(r"^(?!00-)\d{2}-[\w-]+\.md$")


def md_files() -> list[Path]:
    return sorted(p for p in DOCS.rglob("*.md"))


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


def strip_code_blocks(text: str) -> str:
    """去掉围栏代码块，避免代码示例里的路径 / 感叹号误报。"""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def collect_anchors(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(ANCHOR_RE.findall(path.read_text(encoding="utf-8")))


def main() -> int:
    ap = argparse.ArgumentParser(description="JewelryLearning 书稿校验")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印逐文件明细")
    args = ap.parse_args()

    files = md_files()
    if not files:
        print("✗ docs/ 下没有找到任何 .md，仓库结构不对")
        return 1

    print(f"检查 {len(files)} 个 Markdown 文件 ...")

    errors: list[str] = []
    warnings: list[str] = []

    glossary_anchors = collect_anchors(DOCS / "glossary.md")
    standards_text = (
        (DOCS / "reference" / "standards.md").read_text(encoding="utf-8")
        if (DOCS / "reference" / "standards.md").exists()
        else ""
    )
    # 登记表里出现过的标准编号（把空格差异归一化，GB/T 16552 == GB/T16552）
    registered = {s.replace(" ", "") for s in STANDARD_RE.findall(standards_text)}

    qa_anchor_cache: dict[Path, set[str]] = {}

    for f in files:
        raw = f.read_text(encoding="utf-8")
        body = strip_code_blocks(raw)
        tag = rel(f)
        n_before = len(errors)

        # 1. 绝对路径
        for m in ABS_PATH_RE.finditer(body):
            errors.append(f"{tag}: 出现本机绝对路径 `{m.group(1)}`（仓库内只允许相对路径）")

        # 2. MkDocs 专有 admonition
        for m in ADMONITION_RE.finditer(body):
            errors.append(f"{tag}: 出现 admonition `{m.group(0).strip()}`（改用引用块 `>` + 加粗）")

        # 3. 思考题锚点
        for link, qa_name, anchor in QA_LINK_RE.findall(body):
            target = (f.parent / link).resolve()
            if not target.exists():
                errors.append(f"{tag}: 答案册不存在 → {link}")
                continue
            if target not in qa_anchor_cache:
                qa_anchor_cache[target] = collect_anchors(target)
            if anchor not in qa_anchor_cache[target]:
                errors.append(f'{tag}: {qa_name}.md 里缺锚点 <a id="{anchor}">')

        # 4. 术语表锚点
        for _link, anchor in GLOSSARY_LINK_RE.findall(body):
            if anchor not in glossary_anchors:
                errors.append(f'{tag}: glossary.md 里缺术语锚点 <a id="{anchor}">')

        # 5. 标准登记（standards.md 自己不查）
        if f != DOCS / "reference" / "standards.md":
            for std in {s.replace(" ", "") for s in STANDARD_RE.findall(body)}:
                if std not in registered:
                    errors.append(f"{tag}: 引用了 {std} 但未在 reference/standards.md 登记")

        # 6. 图片外链（版权 + 失效风险）
        for url in IMG_EXTERNAL_RE.findall(body):
            errors.append(f"{tag}: 禁止外链图片 {url[:60]}...（改成文字判据 + gallery.md 链接）")

        # 7. 正式章节的固定结构
        if CHAPTER_FILE_RE.match(f.name) and "chapters/" in tag:
            if "思考题" not in body:
                errors.append(f"{tag}: 正式章节缺「思考题」小节")
            if "本章实操" not in body:
                errors.append(f"{tag}: 正式章节缺「本章实操」小节")
            if "🔎" not in body:
                warnings.append(f"{tag}: 建议补一个 🔎「柜台前的用处」小节")

        if args.verbose:
            mark = "✗" if len(errors) > n_before else "✓"
            print(f"  {mark} {tag}")

    for w in warnings:
        print(f"⚠ {w}")

    if errors:
        print(f"\n✗ 校验失败，{len(errors)} 处问题：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✓ 全部通过（{len(files)} 个文件，{len(warnings)} 条建议）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
