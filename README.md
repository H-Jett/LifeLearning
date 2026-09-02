# 走走停停

> 📖 **在线阅读**：<https://h-jett.github.io/LifeLearning/>

一个方向一个仓库；这个仓库放**「走走停停」的书**。每本书自成体系、独立成站。

## 书目

| 书 | 主题 | 在线阅读 | 目录 |
|---|---|---|---|
| **系统学茶** | 工艺原理 + 茶叶化学 + 感官审评，对标评茶员知识体系 | [/tea/](https://h-jett.github.io/LifeLearning/tea/) | [`books/tea`](books/tea) |
| **珠宝入门** | 选购避坑 + 系统宝石学，对标准 GIA / FGA 知识框架 | [/jewelry/](https://h-jett.github.io/LifeLearning/jewelry/) | [`books/jewelry`](books/jewelry) |

## 共同的写法

- **教学法**：概念 → 思考题 → 实操（分「无器具版 / 有条件版」两档）；思考题答案单独成册。
- **正确性纪律**：数值必须有出处；流传的说法逐条标注**证据强度**（✅ 有共识 / ⚠️ 有争议 / ❌ 明确错误）；
  查不到一手来源的**宁可不写**。
- **可移植 Markdown**：在 GitHub / 任意 Markdown 阅读器 / MkDocs 三边都能读。

## 仓库结构

```
books.yml                  # 单一真源：有哪些书、站点地址
scripts/build_site.py      # 逐本校验 + mkdocs build → site/<slug>/，再生成索引页
books/<slug>/              # 一本书 = 一个完整的 MkDocs 工程
  mkdocs.yml  docs/  CLAUDE.md  scripts/  README.md
.github/workflows/pages.yml
```

**各书之间完全隔离**：各自的 `mkdocs.yml`、主题、搜索索引、校验脚本、`CLAUDE.md`。
构建脚本只负责按 `books.yml` 逐本调用，不碰书的内部。

## 本地构建

```bash
pip install mkdocs-material pyyaml

python scripts/build_site.py                # 全部书（含各书自己的校验）
python scripts/build_site.py --only tea     # 只构建一本
python scripts/build_site.py --check        # 只跑校验不构建
```

产物在 `site/`：`site/index.html` 是书架索引，`site/<slug>/` 是各本书。

单独调试某一本时，进到书目录直接用 mkdocs 即可（`site_url` 会回落到 localhost）：

```bash
cd books/tea && mkdocs serve
```

## 加一本新书

1. `books/<slug>/` 建一个完整的 MkDocs 工程（可照抄现有任意一本的骨架）；
2. `mkdocs.yml` 里 `site_url` 写成 `!ENV [BOOK_SITE_URL, "http://127.0.0.1:8000/"]`，
   `edit_uri` 写成 `edit/main/books/<slug>/docs/`；
3. 在 `books.yml` 加一条记录（含该书自己的校验命令）。

索引页会自动出现新卡片，不用手工维护列表。

## 姊妹仓库

| 仓库 | 主题 |
|---|---|
| [InfraLearning](https://github.com/H-Jett/InfraLearning) | 算法工程师的 Infra 入门（推理 → 分布式训练） |
| [MultiModalLearning](https://github.com/H-Jett/MultiModalLearning) | 多模态入门：给 LLM 工程师的一本书 |
