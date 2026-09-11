# 系统学咖啡：从一颗生豆到一杯咖啡

📖 **在线阅读（GitHub Pages）**：<https://h-jett.github.io/LifeLearning/coffee/>

一本"边学边记"的咖啡书。**两个目标同时抓**：

1. **实用**——会买豆（读懂标签上每个字段）、会冲煮（知道每个旋钮在调什么分子）、
   会描述（说得出为什么，而不是背风味词）；
2. **系统**——深度对标 **SCA / CQI（Q-Grader）的知识框架**：咖啡化学、处理法、烘焙化学、
   萃取物理、感官审评，讲原理而不是背结论。

链条全覆盖：种植 · 处理 · 生豆 · 烘焙 · 萃取 · 冲煮 · 感官 · 选购。

**全书的一条主线**：

> 咖啡的一切技术问题，本质都是同一件事——**让哪些成分、以多少比例、进入这一杯**。

内容以标准 Markdown 编写，**三种方式都能看**：

1. **直接在 GitHub 上浏览** [`docs/`](docs/) 里的 `.md`（脚注、表格、术语表跳转都可用）；
2. **本地用任意 Markdown 阅读器**（Typora / Obsidian / VSCode）打开 `docs/`；
3. **构建成网站**（GitHub Pages），带全文搜索和侧边栏导航。

从 [`docs/index.md`](docs/index.md) 开始读，或直接跳到
[第 1 章 · 一颗咖啡豆里有什么](docs/chapters/01-foundation/01-bean-composition.md)。

## 快速入口

| 想干什么 | 去哪 |
|----------|------|
| 看全书大纲与进度 | [学习路线图](docs/roadmap.md) |
| 查本书引用的出处与标准 | [出处与资料登记](docs/standards.md) |
| 查术语（中英对照） | [术语表](docs/glossary.md) |
| 打印一份冲煮 / 杯测 / 买豆记录表 | [记录表](docs/forms/index.md) |

## 这本书怎么保证"正确"

咖啡是个"实践经验先行、科学解释后到"的领域，信息噪音很大：
器具商文案、咨询师口号、论坛共识混在一起，其中一部分是错的，另一部分只是**尚未被验证**。
本书立四条纪律（详见 [CLAUDE.md](CLAUDE.md) §1）：

1. **数值有出处、给区间不给单点**；关键数字要求**两个独立来源**，
   查不到就只写规律、或明确标注"经验值"并说明波动范围；
2. **区分事实 / 标准规定 / 行业惯例 / 圈内说法**四层，
   证据不足的一律进「常见说法辨析」小节并标注证据强度
   （✅ 有共识 · ⚠️ 有争议 · ❌ 明确错误 · 缺乏证据）；
3. **价格只讲机制不写死数字**（C 价与零售价随时变，讲的是定价结构）；
4. **不做医疗 / 健康建议**——咖啡与健康**只讲证据等级**，不给摄入量建议、不做疗效承诺。

另外两条硬规矩：

- **不搬运他人实拍图**，也不内嵌外链图片；要图用 Mermaid 或纯文字判据，
  必要时正文给权威来源的链接。
- **不复制 SCA 官方杯测表 / CVA 表的条文与分值版式**（有版权）。
  本书的[杯测记录表](docs/forms/cupping-sheet.md)是**参考行业框架自拟**的，
  官方表请去 <https://sca.coffee/> 获取现行版本。

## 目录结构

```
books/coffee/
  docs/                          # 书的正文（唯一内容真源）
    index.md                     # 首页 / 大纲 / 进度
    roadmap.md                   # 七部分学习路线图
    glossary.md                  # 术语表（中英对照，显式 <a id> 锚点）
    standards.md                 # 出处与资料登记（标准编号 / 教材 / 一手网页）
    forms/                       # 可复用记录表（冲煮 / 杯测 / 豆袋核对）
    chapters/01-foundation/      # 第一部分 · 咖啡的物质基础
    qa/                          # 思考题答案册（含案例题推理链）
  scripts/check_book.py          # 校验：锚点 / 出处登记 / 绝对路径 / 章节结构
  mkdocs.yml                     # 网站构建配置
```

## 本地预览网站

```bash
python -m venv .venv && source .venv/bin/activate
pip install mkdocs-material
mkdocs serve            # 打开 http://127.0.0.1:8000
```

单独 `mkdocs serve` 时 `site_url` 会回落到 localhost，不影响阅读。

## 提交前校验

```bash
python scripts/check_book.py    # 锚点 / 出处登记 / 绝对路径 / admonition / 章节结构
mkdocs build --strict           # 坏链接或警告即失败（CI 也跑这条）
```

仓库级构建（顺带下发配色与 PWA 生成物，在仓库根目录执行）：

```bash
python scripts/build_site.py --only coffee
```

> ⚠️ `docs/assets/palette.css`、`docs/assets/favicon.svg`、`overrides/main.html`
> **由 `books.yml` 下发生成，不要手写、不要手改**。

## 姊妹书

同一书架（[走走停停](https://h-jett.github.io/LifeLearning/)）上的其他几本：

- [系统学茶](../tea/) —— 从一片叶子到一杯茶汤
- [珠宝入门](../jewelry/) —— 从宝石学原理到选购决策

## 免责声明

本书为学习笔记。**不构成任何健康、医疗或投资建议**；
咖啡与健康的内容仅复述公开研究与机构结论的**证据等级与适用范围**，
不给摄入量建议。涉及商业采购、贸易、检验的正式场合，
一律以相关标准与协议的**最新有效版本原文**为准。
