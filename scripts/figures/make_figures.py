#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成书中的示意图（SVG）。

为什么用 SVG 而不是 matplotlib PNG：
  1. **中文**：本机没有任何中文字体，matplotlib 出图标中文会变成方框；
     SVG 的文字由读者浏览器渲染，中文正常显示。
  2. **可 diff**：SVG 是文本，符合本书「单一真源、可移植」的原则；PNG 是二进制。
  3. **三边可见**：GitHub 原生渲染、Markdown 阅读器、MkDocs 都能显示相对路径的 SVG。

约定（见 CLAUDE.md §7）：
  - 白底（明暗模式下都可读），细线 + 淡网格，直接标注而非图例；
  - 配色用 Okabe-Ito 色盲安全色板；
  - **没有实测数据的图一律在标题里写明「示意」**，绝不画成像实测数据的样子。

用法：
    python scripts/figures/make_figures.py            # 生成全部
    python scripts/figures/make_figures.py --check    # 只校验已生成且为合法 XML
"""

import argparse
import logging
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("make_figures")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
P1 = REPO_ROOT / "docs" / "chapters" / "01-foundation" / "figures"
P2 = REPO_ROOT / "docs" / "chapters" / "02-processing" / "figures"

# Okabe-Ito 色盲安全色板
BLUE, ORANGE, VERMILION = "#0072B2", "#E69F00", "#D55E00"
GREEN, SKY, PURPLE = "#009E73", "#56B4E9", "#CC79A7"
INK, MUTED, GRID = "#222222", "#666666", "#DDDDDD"

# 中文字体回退链：由读者浏览器解析，本机无需安装
FONT = ("Noto Sans CJK SC,Source Han Sans SC,PingFang SC,Microsoft YaHei,"
        "Hiragino Sans GB,WenQuanYi Micro Hei,sans-serif")


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def txt(x, y, s, size=13, fill=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{esc(s)}</text>')


def rect(x, y, w, h, fill="none", stroke=INK, sw=1, rx=0, op=1.0):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}" rx="{rx}" fill-opacity="{op}"/>')


def line(x1, y1, x2, y2, stroke=INK, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>')


def path(d, stroke=INK, sw=1.5, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}/>')


def arrow_defs() -> str:
    return ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>')


def svg(w, h, body, title):
    """包一层 SVG 外壳。白底 + <title> 无障碍标题。"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img">\n'
            f'<title>{esc(title)}</title>\n'
            f'{arrow_defs()}\n'
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#FFFFFF"/>\n'
            f'{body}\n</svg>\n')


# ---------------------------------------------------------------- 第二部分

def fig_process_matrix() -> str:
    """六大茶类 × 工序矩阵，格子里写第几步——一张图看懂六大茶类的分野。"""
    cols = ["萎凋", "做青", "杀青", "揉捻", "闷黄", "发酵", "渥堆", "干燥"]
    rows = [
        ("绿茶", {"杀青": 1, "揉捻": 2, "干燥": 3}, GREEN),
        ("白茶", {"萎凋": 1, "干燥": 2}, "#8FBF9F"),
        ("黄茶", {"杀青": 1, "揉捻": 2, "闷黄": 3, "干燥": 4}, ORANGE),
        ("乌龙茶", {"萎凋": 1, "做青": 2, "杀青": 3, "揉捻": 4, "干燥": 5}, "#B98B2E"),
        ("红茶", {"萎凋": 1, "揉捻": 2, "发酵": 3, "干燥": 4}, VERMILION),
        ("黑茶", {"杀青": 1, "揉捻": 2, "渥堆": 3, "干燥": 4}, "#6B4A2F"),
    ]
    x0, y0, cw, ch = 118, 92, 84, 44
    w, h = x0 + cw * len(cols) + 40, y0 + ch * len(rows) + 96
    b = [txt(24, 34, "六大茶类 = 同一套工序的不同组合", 18, INK, weight="bold"),
         txt(24, 58, "格子里的数字 = 该工序在这类茶里排第几步；空白 = 不做这一步",
             12.5, MUTED)]

    for j, c in enumerate(cols):
        cx = x0 + j * cw + cw / 2
        b.append(txt(cx, y0 - 12, c, 13.5, INK, anchor="middle", weight="bold"))
    for i, (name, steps, color) in enumerate(rows):
        ry = y0 + i * ch
        b.append(rect(x0 - 100, ry, 96, ch - 4, fill=color, stroke="none", op=0.16, rx=4))
        b.append(txt(x0 - 52, ry + ch / 2 + 1, name, 14.5, INK, anchor="middle", weight="bold"))
        for j, c in enumerate(cols):
            cx, n = x0 + j * cw, steps.get(c)
            if n:
                b.append(rect(cx + 3, ry, cw - 6, ch - 4, fill=color, stroke="none", op=0.85, rx=4))
                b.append(txt(cx + cw / 2, ry + ch / 2 + 5, str(n), 16, "#FFFFFF",
                             anchor="middle", weight="bold"))
            else:
                b.append(rect(cx + 3, ry, cw - 6, ch - 4, fill="#FAFAFA", stroke=GRID, rx=4))
    ly = y0 + ch * len(rows) + 30
    b += [
        txt(24, ly, "读法：绿茶最短（3 步）；白茶最少干预（2 步，连揉捻都没有）；",
            12.5, MUTED),
        txt(24, ly + 20,
            "乌龙茶最长（5 步），而且是唯一把「杀青」放在氧化工序（做青）之后的——先让它走，再叫停。",
            12.5, MUTED),
        txt(24, ly + 40,
            "黄茶 = 绿茶 + 闷黄；黑茶 = 绿茶 + 渥堆。这两类都是「在绿茶之后再加一步」。",
            12.5, MUTED),
    ]
    return svg(w, h, "\n".join(b), "六大茶类工序矩阵")


def fig_oxidation_axis() -> str:
    """氧化程度轴 —— 并强调黑茶不在这根轴上。"""
    w, h = 900, 330
    x0, x1, y = 90, 820, 150
    b = [txt(24, 34, "氧化程度：一根轴，外加一条岔路（示意）", 18, INK, weight="bold"),
         txt(24, 58, "刻度是相对位置的示意——国标并没有给各茶类规定「氧化百分比」，"
                     "见到「绿茶氧化度低于 5%、乌龙 15%~70%」这类精确数字请当经验说法看",
             12.5, MUTED)]
    b.append(line(x0, y, x1, y, INK, 2))
    b.append(f'<path d="M {x1} {y} l -10 -5 l 0 10 z" fill="{INK}"/>')
    b.append(txt(x0, y + 34, "不氧化", 12.5, MUTED, anchor="middle"))
    b.append(txt(x1 - 10, y + 34, "充分氧化", 12.5, MUTED, anchor="end"))

    marks = [(0.02, "绿茶", GREEN, "杀青：立刻灭酶"),
             (0.16, "白茶", "#8FBF9F", "萎凋：不主动灭酶"),
             (0.30, "黄茶", ORANGE, "闷黄：湿热为主"),
             (0.58, "乌龙茶", "#B98B2E", "做青：局部、部分"),
             (0.95, "红茶", VERMILION, "发酵：走完全程")]
    for t, name, color, note in marks:
        x = x0 + (x1 - x0) * t
        b.append(line(x, y - 12, x, y + 12, color, 3))
        b.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{color}"/>')
        b.append(txt(x, y - 26, name, 14, INK, anchor="middle", weight="bold"))
        b.append(txt(x, y - 46, note, 11, MUTED, anchor="middle"))

    by = y + 92
    b.append(path(f"M {x0 + 30} {y + 14} C {x0 + 30} {by - 20}, {x0 + 120} {by}, {x0 + 200} {by}",
                  MUTED, 1.6, dash="5,4"))
    b.append(rect(x0 + 196, by - 26, 300, 52, fill="#6B4A2F", stroke="none", op=0.14, rx=6))
    b.append(txt(x0 + 212, by - 6, "黑茶：不在这根轴上", 14, INK, weight="bold"))
    b.append(txt(x0 + 212, by + 14, "起点是绿茶，靠微生物走另一条路", 12, MUTED))
    b.append(txt(24, h - 26,
                 "所以「六大茶类按发酵程度排序」只是教学简化：黄茶靠湿热、黑茶靠微生物，"
                 "机制不同，不是同一根轴上的程度差。", 12.5, MUTED))
    return svg(w, h, "\n".join(b), "六大茶类氧化程度轴")


def fig_liquor_colors() -> str:
    """六大茶类汤色色卡（示意）。"""
    swatches = [
        ("绿茶", "#C6D64F", "嫩绿明亮 / 黄绿"),
        ("白茶", "#EBD98C", "浅杏黄"),
        ("黄茶", "#E8B84B", "杏黄 / 嫩黄"),
        ("乌龙茶", "#DE9A2C", "金黄 / 橙黄 / 橙红"),
        ("红茶", "#BE4520", "红艳 / 红亮"),
        ("黑茶", "#6E2A15", "红浓 / 红褐"),
    ]
    cw, cx0, cy0, chh = 132, 40, 108, 120
    w, h = cx0 * 2 + cw * len(swatches), cy0 + chh + 132
    b = [txt(24, 34, "六大茶类汤色（示意色卡）", 18, INK, weight="bold"),
         txt(24, 58, "色值为示意，用于建立「术语 ↔ 颜色」的对应；"
                     "实际汤色随品种、等级、冲泡浓度、光源变化很大，审评须用标准审评碗与自然光",
             12.5, MUTED),
         txt(24, 84, "术语依据 GB/T 14487《茶叶感官审评术语》", 12, MUTED, style="italic")]
    for i, (name, color, term) in enumerate(swatches):
        x = cx0 + i * cw
        b.append(rect(x, cy0, cw - 14, chh, fill=color, stroke="#00000022", rx=6))
        b.append(txt(x + (cw - 14) / 2, cy0 + chh + 26, name, 15, INK,
                     anchor="middle", weight="bold"))
        b.append(txt(x + (cw - 14) / 2, cy0 + chh + 48, term, 11.5, MUTED, anchor="middle"))
    ny = cy0 + chh + 82
    b += [txt(24, ny, "一条实用经验：汤色的「亮」比「深」更重要。",
              13, INK, weight="bold"),
          txt(24, ny + 22,
              "红茶「红艳明亮」对应茶黄素充足；「红暗」对应茶褐素偏高（发酵过度）——"
              "深而不亮通常是缺陷，不是浓。", 12.5, MUTED)]
    return svg(w, h, "\n".join(b), "六大茶类汤色示意色卡")


def fig_green_tea_branches() -> str:
    """绿茶四类的命名依据：蒸青看杀青方式，其余三类看干燥方式。"""
    w, h = 900, 486
    b = [txt(24, 34, "绿茶四类是怎么分出来的（一个常被讲错的问题）", 18, INK, weight="bold"),
         txt(24, 58, "蒸青按「杀青方式」命名；炒青 / 烘青 / 晒青按「最终干燥方式」命名",
             12.5, MUTED)]

    def box(x, y, ww, hh, label, sub, color, bold=True):
        o = [rect(x, y, ww, hh, fill=color, stroke="none", op=0.85, rx=6),
             txt(x + ww / 2, y + (hh / 2 if not sub else hh / 2 - 4), label, 14, "#FFFFFF",
                 anchor="middle", weight="bold" if bold else "normal")]
        if sub:
            o.append(txt(x + ww / 2, y + hh / 2 + 16, sub, 11, "#FFFFFFDD", anchor="middle"))
        return o

    b += box(30, 180, 110, 54, "鲜叶", None, MUTED)
    b.append(path("M 140 207 L 172 207", INK, 1.6))
    b.append(txt(146, 196, "杀青方式", 12, INK, weight="bold"))

    b += box(205, 120, 140, 54, "蒸汽杀青", None, SKY)
    b += box(205, 240, 140, 54, "炒热杀青", "锅炒 / 滚筒", BLUE)
    b.append(path("M 172 207 L 172 147 L 205 147", INK, 1.4).replace("/>", ' marker-end="url(#ah)"/>'))
    b.append(path("M 172 207 L 172 267 L 205 267", INK, 1.4).replace("/>", ' marker-end="url(#ah)"/>'))

    b.append(path("M 345 147 L 560 147", INK, 1.4).replace("/>", ' marker-end="url(#ah)"/>'))
    b += box(565, 120, 130, 54, "蒸青绿茶", None, SKY)
    b.append(txt(705, 143, "恩施玉露；日本煎茶 / 玉露 / 抹茶", 11.5, MUTED))
    b.append(txt(705, 161, "唐宋古法，明代起中国改锅炒", 11, MUTED, style="italic"))

    b.append(txt(404, 258, "最终干燥方式", 12, INK, weight="bold"))
    dry = [("炒干", "炒青绿茶", "龙井 / 碧螺春 / 眉茶 / 珠茶", BLUE, 296),
           ("烘干", "烘青绿茶", "黄山毛峰 / 太平猴魁 / 花茶茶坯", "#3E7FA6", 352),
           ("晒干", "晒青绿茶", "普洱生茶的原料（晒青毛茶）", "#7A6A2E", 408)]
    for label, name, egs, color, yy in dry:
        b.append(path(f"M 345 267 L 400 267 L 400 {yy + 20} L 430 {yy + 20}", INK, 1.3)
                 .replace("/>", ' marker-end="url(#ah)"/>'))
        b.append(txt(404, yy + 14, label, 11.5, INK))
        b += box(435, yy, 125, 40, name, None, color)
        b.append(txt(570, yy + 25, egs, 11.5, MUTED))
    b.append(txt(24, h - 20,
                 "关键佐证：普洱生茶也用锅炒杀青，但因为最终是晒干的，所以归晒青绿茶——"
                 "命名的落脚点在干燥，不在杀青。", 12.5, INK))
    return svg(w, h, "\n".join(b), "绿茶四类的划分依据")


def fig_shaqing_degrees() -> str:
    """杀青三档：不足 / 适度 / 过度（叶色示意）。"""
    w, h = 860, 330
    b = [txt(24, 34, "杀青三档（叶色示意）", 18, INK, weight="bold"),
         txt(24, 58, "杀青要在最短时间内把叶温提到 70 ℃ 以上——升温太慢与温度过高，缺陷方向相反",
             12.5, MUTED)]
    cards = [
        ("不足（升温太慢）", "#8FA83C", "#A8543A",
         ["叶温长时间停留在 20~45 ℃", "酶反而被「催」得更活跃", "→ 红叶红梗、闷红黄味"], VERMILION),
        ("适度", "#6E9B3E", None,
         ["失重 30%~40%", "熟、透、匀；折梗不断", "→ 色泽匀绿、透清香"], GREEN),
        ("过度（温度过高）", "#A79B33", "#3B2A18",
         ["叶绿素破坏过多", "叶色泛黄", "→ 焦边、爆点"], ORANGE),
    ]
    x0, cw = 40, 262
    for i, (title, leaf, spot, notes, color) in enumerate(cards):
        x = x0 + i * cw
        b.append(rect(x, 88, cw - 24, 200, fill="#FCFCFC", stroke=GRID, rx=8))
        b.append(rect(x, 88, cw - 24, 6, fill=color, stroke="none", rx=3))
        b.append(txt(x + (cw - 24) / 2, 118, title, 14, INK, anchor="middle", weight="bold"))
        lx, ly = x + (cw - 24) / 2, 168
        b.append(f'<ellipse cx="{lx}" cy="{ly}" rx="52" ry="26" fill="{leaf}" '
                 f'stroke="#00000022"/>')
        b.append(line(lx - 52, ly, lx + 52, ly, "#00000018", 1))
        if spot and i == 0:
            b.append(f'<rect x="{lx - 6}" y="{ly - 26}" width="8" height="52" '
                     f'fill="{spot}" opacity="0.85" rx="3"/>')
            b.append(txt(lx + 62, ly + 4, "梗红", 11, MUTED))
        if spot and i == 2:
            for dx, dy in ((-30, -8), (18, 6), (34, -10), (-12, 12)):
                b.append(f'<circle cx="{lx + dx}" cy="{ly + dy}" r="4.5" fill="{spot}" '
                         f'opacity="0.8"/>')
            b.append(txt(lx + 62, ly + 4, "爆点", 11, MUTED))
        for k, n in enumerate(notes):
            b.append(txt(x + 16, 214 + k * 20, "· " + n, 11.5, MUTED))
    b.append(txt(24, h - 18,
                 "下机后必须马上摊凉：余温会继续黄变、产生水闷味——「停」这个动作有延迟。",
                 12.5, INK))
    return svg(w, h, "\n".join(b), "杀青三档叶色示意")


# ---------------------------------------------------------------- 第一部分

def fig_enzyme_temp() -> str:
    """酶活性 - 叶温 示意曲线，叠加各工艺的温度带。"""
    w, h = 900, 430
    ox, oy, pw, ph = 90, 300, 620, 200
    b = [txt(24, 34, "多酚氧化酶活性与叶温（示意曲线，非实测）", 18, INK, weight="bold"),
         txt(24, 58, "曲线形状为示意；标注的三个温度节点来自制茶学通用表述，"
                     "用来解释工艺，不作定量依据", 12.5, MUTED)]
    # 坐标轴
    b.append(line(ox, oy, ox + pw, oy, INK, 1.6))
    b.append(line(ox, oy, ox, oy - ph, INK, 1.6))
    b.append(txt(ox - 10, oy - ph - 10, "酶活性", 12.5, INK, anchor="middle"))
    b.append(txt(ox + pw, oy + 34, "叶温 ℃", 12.5, INK, anchor="end"))

    def tx(t):  # 温度 → x（0~100 ℃）
        return ox + pw * (t / 100.0)

    for t in (0, 20, 45, 70, 85, 100):
        b.append(line(tx(t), oy, tx(t), oy + 6, MUTED, 1))
        b.append(txt(tx(t), oy + 22, str(t), 11.5, MUTED, anchor="middle"))
        b.append(line(tx(t), oy, tx(t), oy - ph, GRID, 1, dash="3,4"))

    # 示意曲线：20 ℃ 低 → 45~52 峰 → 70 明显下降 → 85 归零
    pts = [(0, 0.06), (20, 0.22), (30, 0.42), (40, 0.80), (48, 1.0),
           (56, 0.92), (65, 0.66), (70, 0.44), (76, 0.22), (82, 0.06), (86, 0.01), (100, 0.0)]
    d = " ".join(("M" if i == 0 else "L") + f" {tx(t):.1f} {oy - ph * v:.1f}"
                 for i, (t, v) in enumerate(pts))
    b.append(rect(tx(20), oy - ph, tx(45) - tx(20), ph, fill=GREEN, stroke="none", op=0.10))
    b.append(rect(tx(80), oy - ph, tx(85) - tx(80), ph, fill=VERMILION, stroke="none", op=0.14))
    b.append(path(d, BLUE, 2.6))

    # 关键节点
    for t, label, color, dy in ((45, "20~45 ℃ 最适区\n每升 10 ℃ 活性翻倍", GREEN, -150),
                                (70, "70 ℃ 开始钝化", ORANGE, -96),
                                (85, "80~85 ℃ 基本灭活", VERMILION, -44)):
        b.append(line(tx(t), oy, tx(t), oy - ph, color, 1.8, dash="6,4"))
        lines = label.split("\n")
        for k, ln in enumerate(lines):
            b.append(txt(tx(t) + 8, oy + dy + k * 16, ln, 12,
                         INK if k == 0 else MUTED, weight="bold" if k == 0 else "normal"))

    # 工艺温度带
    # 工艺温度带：标签紧贴各自色带，避免与另一条带的文字串位
    bands = [("晒青毛茶：叶温多在 80 ℃ 以下 → 保留部分酶活 → 普洱可陈化",
              0, 80, "#7A6A2E", 352, "after"),
             ("烘青 / 炒青：叶温多在 90 ℃ 以上 → 酶被彻底破坏",
              90, 100, BLUE, 380, "before")]
    for label, t1, t2, color, yy, side in bands:
        b.append(rect(tx(t1), yy - 10, tx(t2) - tx(t1), 12, fill=color, stroke="none", op=0.55, rx=3))
        if side == "after":
            b.append(txt(tx(t2) + 10, yy + 1, label, 11.5, MUTED))
        else:
            b.append(txt(tx(t1) - 10, yy + 1, label, 11.5, MUTED, anchor="end"))
    b.append(txt(24, h - 8, "⚠️ 注意区分「锅温 / 筒温」与「叶温」：龙井青锅锅温 80~100 ℃、"
                 "滚筒杀青筒温可达 260 ℃，叶温远低于此。", 12, INK))
    return svg(w, h, "\n".join(b), "酶活性与叶温示意曲线")


def fig_shoot_structure() -> str:
    """新梢结构与成分梯度。"""
    w, h = 900, 440
    b = [txt(24, 34, "新梢各部位与成分梯度", 18, INK, weight="bold"),
         txt(24, 58, "方向可靠（多来源一致）；本书不给分叶位的定量百分比——"
                     "公开可查的可追溯数据很少", 12.5, MUTED)]
    sx = 250                                   # 主茎 x
    lab_x = sx + 96                            # 部位标签统一右对齐到这一列，避免压在叶片上
    b.append(line(sx, 320, sx, 112, "#6E8B3D", 6))
    parts = [
        (112, "芽", 26, "#7FA83F", "未展开，多茸毛"),
        (156, "第一叶", 42, "#6E9B3E", None),
        (202, "第二叶", 54, "#5F8C36", None),
        (250, "第三叶", 64, "#547C30", None),
        (300, "鱼叶", 22, "#8FA86A", "发育不完全，不采"),
    ]
    for y, name, ln, color, note in parts:
        b.append(f'<ellipse cx="{sx + ln / 2 + 6}" cy="{y}" rx="{ln / 2}" ry="{ln / 4.4}" '
                 f'fill="{color}" stroke="#00000022"/>')
        b.append(f'<ellipse cx="{sx - ln / 2 - 6}" cy="{y + 12}" rx="{ln / 2}" ry="{ln / 4.4}" '
                 f'fill="{color}" stroke="#00000022" opacity="0.75"/>')
        b.append(line(sx + ln + 8, y, lab_x - 6, y, GRID, 1))
        b.append(txt(lab_x, y + 4, name, 13, INK, weight="bold"))
        if note:
            b.append(txt(lab_x + 54, y + 4, note, 11, MUTED))
    # 嫩梗：标注放左侧，箭头指向主茎
    b.append(txt(40, 222, "嫩梗", 13, INK, weight="bold"))
    b.append(txt(40, 242, "茶氨酸比芽叶", 11, VERMILION))
    b.append(txt(40, 258, "高 1~3 倍", 11, VERMILION))
    b.append(path(f"M 104 230 L {sx - 8} 238", VERMILION, 1.4)
             .replace("/>", ' marker-end="url(#ah)"/>'))

    # 梯度条（纵向间距拉开，避免上下条的标签互相打架）
    gx, gw = 540, 300
    grads = [("氨基酸 / 酚氨比低 → 鲜爽", GREEN, 128, True),
             ("咖啡碱", ORANGE, 206, True),
             ("纤维素 / 粗老度", "#8B6B3A", 284, False)]
    for label, color, y, decreasing in grads:
        b.append(txt(gx, y - 12, label, 12.5, INK, weight="bold"))
        o1, o2 = (0.9, 0.15) if decreasing else (0.15, 0.9)
        b.append(f'<defs><linearGradient id="g{y}" x1="0" x2="1">'
                 f'<stop offset="0" stop-color="{color}" stop-opacity="{o1}"/>'
                 f'<stop offset="1" stop-color="{color}" stop-opacity="{o2}"/>'
                 f'</linearGradient></defs>')
        b.append(f'<rect x="{gx}" y="{y}" width="{gw}" height="22" fill="url(#g{y})" rx="4"/>')
        b.append(txt(gx, y + 36, "芽", 10.5, MUTED))
        b.append(txt(gx + gw, y + 36, "老叶 / 梗以下", 10.5, MUTED, anchor="end"))
    b.append(txt(gx, 360, "→ 酚氨比随叶位下移而升高", 13, INK, weight="bold"))
    b.append(txt(24, h - 22, "「嫩」是规格不是品质：对绿茶，嫩通常对应鲜爽；"
                 "对乌龙茶，采太嫩直接是缺陷（见第 3 章开面采）。", 12.5, INK))
    return svg(w, h, "\n".join(b), "新梢结构与成分梯度")


def fig_kaimian() -> str:
    """开面三档：顶叶与第二叶的面积比。"""
    w, h = 860, 320
    b = [txt(24, 34, "开面三档：顶叶面积 ÷ 第二叶面积", 18, INK, weight="bold"),
         txt(24, 58, "乌龙茶的采摘判断依据。据鲜叶内含成分分析，三叶中开面梢最适制乌龙茶",
             12.5, MUTED)]
    cases = [("小开面", 0.5, "≈ 1/2", "夏暑茶、持嫩性强的茶园", ORANGE),
             ("中开面", 0.667, "≈ 2/3", "春、秋茶常用（最常见）", GREEN),
             ("大开面", 1.0, "≈ 1", "偏老，滋味易淡薄", "#8A7A4B")]
    x0, cw = 60, 262
    LEAF = "#6E9B3E"     # 三片顶叶是同一种叶子，只是大小不同——颜色必须一致
    for i, (name, ratio, rl, note, color) in enumerate(cases):
        cx = x0 + i * cw + 90
        b.append(rect(x0 + i * cw - 20, 88, cw - 30, 194, fill="#FCFCFC", stroke=GRID, rx=8))
        b.append(rect(x0 + i * cw - 20, 88, cw - 30, 6, fill=color, stroke="none", rx=3))
        b.append(txt(cx, 120, name, 15, INK, anchor="middle", weight="bold"))
        base = 46
        b.append(f'<ellipse cx="{cx}" cy="{212}" rx="{base}" ry="{base / 2.4}" '
                 f'fill="#4F7A2C" stroke="#00000022"/>')
        b.append(txt(cx + base + 8, 216, "第二叶", 10.5, MUTED))
        top = base * (ratio ** 0.5)          # 半径按面积比开方 → 面积比才等于定义值
        b.append(f'<ellipse cx="{cx}" cy="{164}" rx="{top}" ry="{top / 2.4}" '
                 f'fill="{LEAF}" stroke="#00000022"/>')
        b.append(txt(cx + top + 8, 168, "顶叶", 10.5, MUTED))
        b.append(txt(cx, 252, rl, 15, color, anchor="middle", weight="bold"))
        b.append(txt(cx, 272, note, 11, MUTED, anchor="middle"))
    b.append(txt(24, h - 16, "采太嫩 → 色泽红褐灰暗、香低味涩；采太老 → 外形粗大、滋味淡薄。",
                 12.5, INK))
    return svg(w, h, "\n".join(b), "开面三档示意")


FIGURES = [
    (P2, "process-matrix.svg", fig_process_matrix),
    (P2, "oxidation-axis.svg", fig_oxidation_axis),
    (P2, "liquor-colors.svg", fig_liquor_colors),
    (P2, "green-tea-branches.svg", fig_green_tea_branches),
    (P2, "shaqing-degrees.svg", fig_shaqing_degrees),
    (P1, "enzyme-temp.svg", fig_enzyme_temp),
    (P1, "shoot-structure.svg", fig_shoot_structure),
    (P1, "kaimian.svg", fig_kaimian),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="生成书中的 SVG 示意图")
    ap.add_argument("--check", action="store_true", help="只校验：文件存在且为合法 XML")
    args = ap.parse_args()

    bad = 0
    for outdir, name, fn in FIGURES:
        target = outdir / name
        if args.check:
            if not target.exists():
                log.error("缺失: %s", target.relative_to(REPO_ROOT)); bad += 1; continue
            content = target.read_text(encoding="utf-8")
        else:
            outdir.mkdir(parents=True, exist_ok=True)
            content = fn()
            target.write_text(content, encoding="utf-8")
            log.info("生成 %s (%d 字节)", target.relative_to(REPO_ROOT), len(content))
        try:
            ET.fromstring(content)
        except ET.ParseError as e:
            log.error("XML 非法: %s -> %s", target.relative_to(REPO_ROOT), e); bad += 1

    if bad:
        log.error("失败：%d 个图有问题", bad); return 1
    log.info("全部 %d 张图 %s。", len(FIGURES), "校验通过" if args.check else "生成并校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
