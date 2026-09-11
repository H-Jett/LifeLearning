#!/usr/bin/env python3
"""《做菜的原理》书稿一致性校验。

姊妹书 InfraLearning 靠"真机跑代码"保证正确性，做菜没有代码可跑，
所以把**可机器检查的纪律**尽量固化在这里，人工只负责查事实。

厨房是谣言密度最高的领域，本书的两条核心纪律因此被做成了硬检查：
**每章必须有「常见说法辨析」并标证据强度**、**每章必须有「本章依据」列出处**。

检查项（任何一项失败 → 退出码 1）：

1. 绝对路径     ——公开仓库禁止出现本机绝对路径（会泄漏用户名 / 目录布局）
2. admonition   ——禁止 MkDocs 专有的 `!!! note`（纯 Markdown 阅读器会露原文）
3. 思考题锚点   ——章节里引用的 `qa/xxx.md#qN` 必须真的存在 <a id="qN">
4. 术语表锚点   ——章节里引用的 `glossary.md#slug` 必须真的存在 <a id="slug">
5. 站内链接     ——所有相对 .md 链接的目标文件必须存在（`--strict` 之前先挡一道）
6. 出处登记     ——正文出现的 GB / ISO 等标准编号必须在 docs/standards.md 里登记过
7. 图片外链     ——禁止 ![](http...) 热链他人图片（版权 + 失效风险）
8. 章节结构     ——正式章节必须有「常见说法辨析」「思考题」「本章实操」「本章依据」，
                   实操必须同时给 🅐 / 🅑 两档，并建议有 🔎 栏目
9. 证据强度     ——「常见说法辨析」小节必须出现证据强度标记（✅ / ⚠️ / ❌ / 缺乏证据）
10. 术语表节号  ——glossary.md 的 `## ` 标题不许重复（否则锚点会打架）
11. 温度单位    ——摄氏温度必须写成 `x °C` / `x~y °C`，不许裸写 `x度`（避免与"几成热"混淆）

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
STANDARDS = DOCS / "standards.md"
GLOSSARY = DOCS / "glossary.md"

# ---------- 各检查项的正则 ----------

# 本机绝对路径：/volume/... /root/... /home/xxx/... C:\...
ABS_PATH_RE = re.compile(
    r"(?:^|[\s\"'`(])(/(?:volume|root|home|mnt|data)/[\w./-]+|[A-Za-z]:\\\\[\w\\\\.-]+)"
)
ADMONITION_RE = re.compile(r"^\s*(?:!!!|\?\?\?)\s+\w+", re.MULTILINE)
# Markdown 链接里指向 qa 答案册的锚点
QA_LINK_RE = re.compile(r"\]\(([^)]*qa/([\w-]+)\.md)#(q\d+)\)")
GLOSSARY_LINK_RE = re.compile(r"\]\(([^)]*glossary\.md)#([\w-]+)\)")
ANCHOR_RE = re.compile(r'<a\s+id="([\w-]+)"\s*>')
# 任意站内 .md 链接（相对路径），可带锚点
INTERNAL_LINK_RE = re.compile(r"\]\((?!https?://|mailto:)([^)#\s]+\.md)(?:#[\w-]+)?\)")
# 正文引用的标准编号。做菜这边主要是中国食品安全国家标准（GB）与偶发的 ISO。
STANDARD_RE = re.compile(r"\b((?:GB/T|GB|ISO|SN/T)\s?\d{3,6})")
IMG_EXTERNAL_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)]+)\)")
# 正式章节文件：NN-name.md（排除 00-intro / summary / project-*）
CHAPTER_FILE_RE = re.compile(r"^(?!00-)\d{2}-[\w-]+\.md$")
# 证据强度标记（「常见说法辨析」表里必须出现至少一种）
EVIDENCE_MARKS = ("✅", "⚠️", "❌", "缺乏证据")
# 裸写的中文温度（"180度油温"），统一要求写成 `180 °C`；"几成热"另说，不含数字不管
BARE_DEGREE_RE = re.compile(r"\d+\s*度(?!数)")

# 正式章节必须出现的小节名
REQUIRED_SECTIONS = ("常见说法辨析", "思考题", "本章实操", "本章依据")


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
    ap = argparse.ArgumentParser(description="《做菜的原理》书稿校验")
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
    standards_text = STANDARDS.read_text(encoding="utf-8") if STANDARDS.exists() else ""
    if not standards_text:
        errors.append("docs/standards.md 不存在或为空（所有出处必须集中登记）")
    # 登记表里出现过的标准编号（把空格差异归一化，GB 31654 == GB31654）
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

        # 5. 站内 .md 链接的目标文件必须存在
        for link in set(INTERNAL_LINK_RE.findall(body)):
            if not (f.parent / link).resolve().exists():
                errors.append(f"{tag}: 站内链接指向不存在的文件 → {link}")

        # 6. 标准编号登记（standards.md 自己不查）
        if f != STANDARDS:
            for std in {s.replace(" ", "") for s in STANDARD_RE.findall(body)}:
                if std not in registered:
                    errors.append(f"{tag}: 引用了 {std} 但未在 docs/standards.md 登记")

        # 7. 图片外链（版权 + 失效风险）
        for url in IMG_EXTERNAL_RE.findall(body):
            errors.append(f"{tag}: 禁止外链图片 {url[:60]}...（改成文字判据 + Mermaid 自绘）")

        # 11. 温度单位写法（全书统一 `x °C`，避免与中式"几成热"混淆）
        for m in BARE_DEGREE_RE.finditer(body):
            errors.append(f"{tag}: 温度请写成 `x °C` 而不是 `{m.group(0)}`（"
                          "中式'几成热'不带数字时不受此限）")

        # 8 / 9. 正式章节的固定结构
        if CHAPTER_FILE_RE.match(f.name) and "chapters/" in tag:
            for section in REQUIRED_SECTIONS:
                if section not in body:
                    errors.append(f"{tag}: 正式章节缺「{section}」小节")
            if "常见说法辨析" in body and not any(mark in body for mark in EVIDENCE_MARKS):
                errors.append(f"{tag}: 「常见说法辨析」里没有证据强度标记（✅/⚠️/❌/缺乏证据）")
            if "本章实操" in body:
                if "🅐" not in body:
                    errors.append(f"{tag}: 本章实操缺 🅐 零成本版（读者可能没灶台也没食材）")
                if "🅑" not in body:
                    errors.append(f"{tag}: 本章实操缺 🅑 开火版")
            if "🔎" not in body:
                warnings.append(f"{tag}: 建议补一个 🔎「下次做菜时的用处」小节")

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
