# 珠宝入门：从宝石学原理到选购决策

📖 **在线阅读（GitHub Pages）**：<https://h-jett.github.io/JewelryLearning/>

一本"边学边记"的珠宝书。**两个目标同时抓**：

1. **选购不被坑**——会读名称、会看证书、会识别处理与合成、知道哪些参数值得花钱；
2. **系统学宝石学**——深度对标 GIA GG / FGA / NGTC 的知识体系，讲原理而不是背结论。

品类全覆盖：钻石 · 有色宝石 · 玉石 · 有机宝石 · 贵金属与工艺。

内容以标准 Markdown 编写，**三种方式都能看**：

1. **直接在 GitHub 上浏览** [`docs/`](docs/) 里的 `.md`（脚注、表格、术语表跳转都可用）；
2. **本地用任意 Markdown 阅读器**（Typora / Obsidian / VSCode）打开 `docs/`；
3. **构建成网站**（GitHub Pages），带全文搜索和侧边栏导航。

从 [`docs/index.md`](docs/index.md) 开始读，或直接跳到
[第 1 章 · 什么是宝石](docs/chapters/01-gemology/01-what-is-gemstone.md)。

## 快速入口

| 想干什么 | 去哪 |
|----------|------|
| 看全书大纲与进度 | [学习路线图](docs/roadmap.md) |
| 查折射率 / 比重 / 硬度 | [宝石物理常数速查表](docs/reference/constants.md) |
| 查本书引用的标准出处 | [标准与文献索引](docs/reference/standards.md) |
| 想看宝石实物图 | [权威图库索引](docs/reference/gallery.md) |
| 打印一份观察 / 验货清单 | [记录表](docs/forms/index.md) |
| 查术语（中英对照） | [术语表](docs/glossary.md) |

## 这本书怎么保证"正确"

珠宝行业信息噪音极大。本书立四条纪律（详见 [CLAUDE.md](CLAUDE.md) §1）：

1. **数值有出处、给区间不给单点**；
2. **区分事实 / 标准规定 / 市场惯例 / 传说**四层，证据不足的单独辨析并标注证据强度；
3. **价格只讲机制不写死数字**（金价钻价随时变，讲的是定价结构）；
4. **不做鉴定结论、不做投资建议**——隔着屏幕不能鉴定；本书教你怎么看、怎么问、何时必须送检。

## 目录结构

```
jewelry-learning/
  docs/                      # 书的正文（唯一内容真源）
    index.md                 # 封面 / 大纲 / 进度
    roadmap.md               # 七部分学习路线图
    glossary.md              # 术语表（中英对照，显式 <a id> 锚点）
    reference/               # 速查：常数表 / 标准索引 / 权威图库索引
    forms/                   # 可复用记录表（观察、证书核对、选购决策）
    chapters/01-gemology/    # 第一部分 · 宝石学地基
    qa/                      # 思考题答案册（含案例题推理链）
  scripts/check_book.py      # 校验：锚点 / 标准登记 / 绝对路径 / 图片版权
  mkdocs.yml                 # 网站构建配置
  .github/workflows/         # GitHub Pages 自动发布
```

## 本地预览网站

```bash
python -m venv .venv && source .venv/bin/activate
pip install mkdocs-material
mkdocs serve            # 打开 http://127.0.0.1:8000
```

## 提交前校验

```bash
python scripts/check_book.py    # 锚点 / 标准登记 / 绝对路径 / admonition
mkdocs build --strict           # 坏链接或警告即失败（CI 也跑这条）
```

## 发布到 GitHub Pages

推到 GitHub 后，在仓库 **Settings → Pages → Build and deployment → Source** 选
**GitHub Actions**。⚠️ 改完这个设置**还需要再 push 一次**才会真正发布
（否则 build 绿、deploy 红、站点 404）。之后每次 push 到 `main` 自动构建发布。

## 姊妹项目

同一套"边学边记"体例的其他几本：

- [InfraLearning](https://github.com/H-Jett/InfraLearning) —— 算法工程师的 Infra 入门
- [MultiModalLearning](https://github.com/H-Jett/MultiModalLearning) —— 多模态入门

## 免责声明

本书为学习笔记，**不构成鉴定结论、不构成投资建议**。贵重珠宝的真伪与品质，
请以国家认可的检测机构（如 NGTC）或国际权威实验室（GIA / SSEF / Gübelin / AGL 等）
出具的检测报告为准。涉及 CITES 管制材料的内容仅用于识别与合规提示。
