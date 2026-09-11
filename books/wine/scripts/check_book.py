#!/usr/bin/env python3
"""WineLearning（《系统品酒》）书稿一致性校验。

姊妹书 InfraLearning 靠"真机跑代码"保证正确性，酒没有代码可跑，
所以把**可机器检查的纪律**尽量固化在这里，人工只负责查事实。

检查项（任何一项失败 → 退出码 1）：

1. 绝对路径     ——公开仓库禁止出现本机绝对路径（会泄漏用户名 / 目录布局）
2. admonition   ——禁止 MkDocs 专有的 `!!! note`（纯 Markdown 阅读器会露原文）
3. 思考题锚点   ——章节里引用的 `qa/xxx.md#qN` 必须真的存在 <a id="qN">
4. 术语表锚点   ——章节里引用的 `glossary.md#slug` 必须真的存在 <a id="slug">
5. 出处登记     ——正文出现的标准/法规编号（GB/T、(EU) 号、ISO、NOM、CFR）
                  必须已在 docs/standards.md 登记
6. 图片外链     ——禁止 ![](http...) 热链他人图片（版权 + 失效风险）
7. 章节结构     ——正式章节必须有「常见说法辨析」「思考题」「本章实操」「🔎」四块
8. 术语表节号   ——glossary.md 的 `## ` 标题不得重复（否则页内锚点互相覆盖）
9. 术语锚点重复 ——同一个 <a id="..."> 在同一文件里只能出现一次

另有**警告**（不阻断，但要看一眼）：

- 健康/疗效措辞：正文出现"抗癌""软化血管""养生功效"这类词
- 章节里带饮用动作的实操缺少"适度饮酒"提示
- 出现 "WSET" 字样的地方——提醒人工确认没有照抄 SAT 版权内容

用法：
    python scripts/check_book.py           # 全量检查
    python scripts/check_book.py -v        # 附带逐文件明细
    python scripts/check_book.py --quiet   # 只在失败时输出
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
STANDARDS = DOCS / "standards.md"

# ---------- 各检查项的正则 ----------

# 本机绝对路径：/volume/... /root/... /home/xxx/... C:\...
ABS_PATH_RE = re.compile(
    r"(?:^|[\s\"'`(])(/(?:volume|root|home|mnt|data|Users)/[\w./-]+|[A-Za-z]:\\\\[\w\\\\.-]+)"
)
ADMONITION_RE = re.compile(r"^\s*(?:!!!|\?\?\?)\s+\w+", re.MULTILINE)
# Markdown 链接里指向 qa 答案册的锚点
QA_LINK_RE = re.compile(r"\]\(([^)]*qa/([\w-]+)\.md)#(q\d+)\)")
GLOSSARY_LINK_RE = re.compile(r"\]\(([^)]*glossary\.md)#([\w-]+)\)")
ANCHOR_RE = re.compile(r'<a\s+id="([\w-]+)"\s*>')
IMG_EXTERNAL_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)]+)\)")
# 正式章节文件：NN-name.md（排除 00-intro / summary / project-*）
CHAPTER_FILE_RE = re.compile(r"^(?!00-)\d{2}-[\w-]+\.md$")

# ---------- 出处登记：本书引用的各类"编号" ----------
# 酒类横跨多个法系，所以登记检查不只管中国国标：
#   中国国标 / 行标   GB 2757、GB/T 15037、NY/T 1508、QB/T 1852
#   欧盟法规           (EU) 2019/787、(EU) No 1308/2013
#   ISO                ISO 3591
#   墨西哥官方标准     NOM-006-SCFI
#   美国联邦法规       27 CFR 5
REGISTRY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("中国标准", re.compile(r"\b((?:GB/T|GB|NY/T|QB/T|SN/T|DB\d{2}/T)\s?\d{3,6})")),
    ("EU 法规", re.compile(r"\((?:EU|EC|EEC)\)\s*(?:No\.?\s*)?(\d{2,4}/\d{4})")),
    ("ISO 标准", re.compile(r"\b(ISO\s?\d{3,5})")),
    ("墨西哥 NOM", re.compile(r"\b(NOM-\d{3}-[A-Z]{2,6})")),
    ("美国 CFR", re.compile(r"\b(\d{1,2}\s?CFR\s?(?:Part\s?)?\d{1,3})")),
]


def norm(s: str) -> str:
    """归一化编号：去空格、去 "No."、统一大写，让 `GB/T 15037` == `GB/T15037`。"""
    return re.sub(r"(?i)\bno\.?\b", "", s).replace(" ", "").replace("Part", "").upper()


# ---------- 只作警告的措辞 ----------
HEALTH_WORDS = [
    "抗癌", "防癌", "软化血管", "养生功效", "美容养颜", "延年益寿",
    "降血脂", "降血压", "治疗", "疗效", "保健功效",
]
# 带饮用动作的实操，应当带一句适度饮酒提示
DRINK_HINT_WORDS = ["开瓶", "倒一杯", "品鉴三支", "喝一口", "尝一口"]
MODERATION_WORDS = ["适度饮酒", "未成年人不饮酒", "酒后不驾车"]


def md_files() -> list[Path]:
    return sorted(p for p in DOCS.rglob("*.md"))


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


def strip_code_blocks(text: str) -> str:
    """去掉围栏代码块，避免代码/Mermaid 里的路径与感叹号误报。"""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def collect_anchors(path: Path) -> list[str]:
    if not path.exists():
        return []
    return ANCHOR_RE.findall(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="WineLearning 书稿校验")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印逐文件明细")
    ap.add_argument("--quiet", action="store_true", help="只在失败时输出")
    args = ap.parse_args()

    def say(msg: str = "") -> None:
        if not args.quiet:
            print(msg)

    files = md_files()
    if not files:
        print("✗ docs/ 下没有找到任何 .md，书的结构不对")
        return 1

    say(f"检查 {len(files)} 个 Markdown 文件 ...")

    errors: list[str] = []
    warnings: list[str] = []

    glossary_anchors = set(collect_anchors(DOCS / "glossary.md"))
    standards_text = STANDARDS.read_text(encoding="utf-8") if STANDARDS.exists() else ""
    if not standards_text:
        errors.append("docs/standards.md 缺失或为空——所有出处必须集中登记在这里")
    registered = {
        norm(m)
        for _label, pat in REGISTRY_PATTERNS
        for m in pat.findall(standards_text)
    }

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
                qa_anchor_cache[target] = set(collect_anchors(target))
            if anchor not in qa_anchor_cache[target]:
                errors.append(f'{tag}: {qa_name}.md 里缺锚点 <a id="{anchor}">')

        # 4. 术语表锚点
        for _link, anchor in GLOSSARY_LINK_RE.findall(body):
            if anchor not in glossary_anchors:
                errors.append(f'{tag}: glossary.md 里缺术语锚点 <a id="{anchor}">')

        # 5. 出处登记（standards.md 自己不查）
        if f != STANDARDS:
            for label, pat in REGISTRY_PATTERNS:
                for code in {m for m in pat.findall(body)}:
                    if norm(code) not in registered:
                        errors.append(
                            f"{tag}: 引用了{label} `{code.strip()}` 但未在 docs/standards.md 登记"
                        )

        # 6. 图片外链（版权 + 失效风险）
        for url in IMG_EXTERNAL_RE.findall(body):
            errors.append(f"{tag}: 禁止外链图片 {url[:60]}...（改成文字判据 + 正文给权威链接）")

        # 9. 同一文件里锚点不得重复
        dup = [a for a, c in Counter(collect_anchors(f)).items() if c > 1]
        for a in dup:
            errors.append(f'{tag}: 锚点 <a id="{a}"> 重复定义（页内跳转会错位）')

        # 7. 正式章节的固定结构
        if CHAPTER_FILE_RE.match(f.name) and "chapters/" in tag:
            for need, hint in [
                ("常见说法辨析", "逐条标证据强度的辨析表"),
                ("思考题", "章末思考题 + 答案册跳转"),
                ("本章实操", "🅐 无器具版 / 🅑 有条件版"),
                ("🔎", "🔎「买酒与点酒时的用处」"),
            ]:
                if need not in body:
                    errors.append(f"{tag}: 正式章节缺「{need}」（{hint}）")
            if any(w in body for w in DRINK_HINT_WORDS) and not any(
                w in body for w in MODERATION_WORDS
            ):
                warnings.append(f"{tag}: 有饮用动作的实操，建议补一句「适度饮酒，未成年人不饮酒」")

        # 警告：健康/疗效措辞
        for w in HEALTH_WORDS:
            if w in body:
                warnings.append(f"{tag}: 出现健康/疗效措辞「{w}」——本书只讲证据等级，请复核措辞")

        # 警告：WSET 版权提醒
        if "WSET" in body:
            warnings.append(f"{tag}: 出现 WSET 字样——确认没有照抄 SAT 的条目表述与表格版式")

        # 8. 术语表节号重复
        if f == DOCS / "glossary.md":
            heads = re.findall(r"^##\s+(.+)$", body, re.MULTILINE)
            for h, c in Counter(heads).items():
                if c > 1:
                    errors.append(f"{tag}: `## {h}` 出现 {c} 次（节号/标题不得重复）")

        if args.verbose:
            mark = "✗" if len(errors) > n_before else "✓"
            print(f"  {mark} {tag}")

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
