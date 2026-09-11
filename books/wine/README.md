# 系统品酒：从葡萄酒到烈酒

📖 **在线阅读（GitHub Pages）**：<https://h-jett.github.io/LifeLearning/wine/>

一本"边学边记"的品酒书。**两个目标同时抓**：

1. **实用**——读懂酒标、把风味说清楚、判断一瓶酒值不值这个价、会侍酒与配餐；
2. **系统**——从**物质基础 → 品种与风土 → 酿造与陈年 → 产区与法规 → 系统品鉴 →
   烈酒**建立完整框架，蒸馏酒一侧覆盖威士忌 / 白兰地 / 朗姆 / 龙舌兰 / 金酒 / 中国白酒。

全书的主线只有一句话：

> **一杯酒给你的所有感受，都来自可以命名、可以测量、可以拆开比较的东西。**

所以本书不从"记酒名"开始，而是**先建立机理，再挂名字**。

内容以标准 Markdown 编写，**三种方式都能看**：

1. **直接在 GitHub 上浏览** [`docs/`](docs/) 里的 `.md`（脚注、表格、术语表跳转都可用）；
2. **本地用任意 Markdown 阅读器**（Typora / Obsidian / VSCode）打开 `docs/`；
3. **构建成网站**（GitHub Pages），带全文搜索和侧边栏导航。

从 [`docs/index.md`](docs/index.md) 开始读，或直接跳到
[第 1 章 · 一杯酒里有什么](docs/chapters/01-foundation/01-what-is-in-the-glass.md)。

## 快速入口

| 想干什么 | 去哪 |
|----------|------|
| 看全书大纲与进度 | [学习路线图](docs/roadmap.md) |
| 查本书引用的法规、标准与教材出处 | [出处与资料登记](docs/standards.md) |
| 查术语（中文 / 原文 / 英文对照） | [术语表](docs/glossary.md) |
| 拿一份可填写的品鉴记录表 | [记录表](docs/forms/index.md) |

## 这本书怎么保证"正确"

酒是个话术密度极高的行业，法规还改得很勤。本书立四条纪律（详见 [CLAUDE.md](CLAUDE.md) §1）：

1. **数值有出处、给区间不给单点**，关键数字要两个独立来源；查不到就写规律或标"经验值"；
2. **区分事实 / 法规规定 / 行业惯例 / 酒圈传说**四层，证据不足的进「常见说法辨析」并标证据强度
   （✅ 有共识 / ⚠️ 有争议 / ❌ 明确错误 / 缺乏证据）；
3. **价格只讲机制不写死数字**（汇率与年份行情随时变，讲的是定价结构）；
4. **不做鉴定结论、不做投资建议、不做健康建议**——酒与健康只讲证据等级。

**版权纪律**：本书**不照抄 WSET 的 SAT 品鉴体系**（那是 WSET 的版权材料），
品鉴结构自拟，只引用可公开引用的框架（OIV 国际评酒会评分表、ISO 3591 品酒杯标准等）；
也**不搬运他人实拍图与酒标图**，要看图就给权威链接。

## 目录结构

```
books/wine/
  docs/                        # 书的正文（唯一内容真源）
    index.md                   # 封面 / 大纲 / 进度
    roadmap.md                 # 七部分学习路线图
    standards.md               # 出处与资料登记（法规 / 标准 / 教材，带核对状态）
    glossary.md                # 术语表（显式 <a id> 锚点）
    forms/                     # 可复用记录表（品鉴记录表…）
    chapters/01-foundation/    # 第一部分 · 一杯酒的物质基础与感官
    qa/                        # 思考题答案册（含案例题推理链）
  scripts/check_book.py        # 校验：锚点 / 出处登记 / 绝对路径 / 章节结构
  mkdocs.yml                   # 网站构建配置
```

## 本地构建与预览

本书是 `H-Jett/LifeLearning` 仓库里的一本，构建有两种方式。

**① 只看这一本（最快，`site_url` 会回落到 localhost，不影响阅读）**：

```bash
python -m venv .venv && . .venv/bin/activate
pip install mkdocs-material
cd books/wine && mkdocs serve      # 打开 http://127.0.0.1:8000
```

**② 走仓库级构建（和线上一致，会生成配色与 PWA 文件）**，在**仓库根目录**执行：

```bash
python scripts/build_site.py --only wine
```

> ⚠️ **一定要带 `--only wine`**：不带 `--only` 会清空整个 `site/` 并重建所有书。
> `docs/assets/palette.css`、`docs/assets/favicon.svg`、`overrides/main.html`
> 由 `books.yml` 下发生成，**不要手写、不要手改**。

## 提交前校验

```bash
cd books/wine && python scripts/check_book.py    # 锚点 / 出处登记 / 绝对路径 / 章节结构
mkdocs build --strict                            # 坏链接或警告即失败（CI 也跑这条）
```

两条全绿再提交。提交信息带书名前缀，如 `wine: 第 2 章 感官通道`。

## 免责声明

本书为学习笔记。**面向法定饮酒年龄以上的读者**；**适度饮酒，未成年人不饮酒，酒后不驾车**。

本书**不构成鉴定结论、不构成投资建议、不构成任何医疗或健康建议**。
酒与健康的内容只陈述研究现状与证据等级。法规与标准请以官方最新发布版本为准——
本书登记的版本状态可能滞后，[出处与资料登记](docs/standards.md) 里标注了每条的核对时间。
