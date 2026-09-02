# CLAUDE.md — 仓库级约定（多本书的单仓库）

> 这是**仓库级**规范。每本书**另有自己的 `books/<slug>/CLAUDE.md`**，
> 在某本书的目录下干活时，那份才是主规范——**书内的写作纪律以书自己的 CLAUDE.md 为准**。
> 本文件只管"多本书共处一个仓库"带来的那些事。

## 1. 这个仓库是什么

一个方向一个仓库。这个仓库是「**走走停停的书**」这个方向，站点
<https://h-jett.github.io/LifeLearning/>。

目前两本：`books/tea`（系统学茶）、`books/jewelry`（珠宝入门）。

## 2. 铁律：书与书之间互不干涉

- **不要**把各书的 `mkdocs.yml`、主题配置、校验脚本"统一"或抽成公共模块。
  它们各自演化：tea 有 SVG 插图生成器，jewelry 的 `check_book.py` 多了禁 admonition
  和图片版权检查——**这些差异是刻意的，不是重复代码**。
- **不要**跨书引用内容（`../jewelry/...`）。要引用就复述并注明"另一本书里讲过"。
- 各书**独立的搜索索引**。搜索不跨书是设计，不是缺陷。

## 3. 单一真源：`books.yml`

**加一本书 = 建目录 + 在 `books.yml` 加一条记录。** 构建脚本据此决定构建哪些、
索引页列哪些，所以不会出现"书加了但索引忘了改"。

每条记录里的 `checks` 是**该书自己的校验命令**（在书目录下执行）。
新书如果有特殊校验，写进它自己的记录，不要塞进 `build_site.py`。

## 4. 站点地址与 `site_url`

- **`books.yml` 的 `base_url` 是唯一写死站点地址的地方**；
  各书 `mkdocs.yml` 里写 `site_url: !ENV [BOOK_SITE_URL, "http://127.0.0.1:8000/"]`，
  由 `scripts/build_site.py` 注入。**仓库改名时只改 `books.yml` 一行。**
- `edit_uri` 必须写成 `edit/main/books/<slug>/docs/`，否则"在 GitHub 上编辑"会指错目录。
- ⚠️ **`github.io` 的路径改名后不会重定向**（实测过，直接 404，
  GitHub 只重定向 `github.com` 上的仓库地址）。所以 `base_url` 和各书 `slug` **一次定好**。

## 5. 构建与校验（提交前必做）

```bash
python scripts/build_site.py            # 全部书：各自校验 + mkdocs build --strict + 索引页
python scripts/build_site.py --only tea # 只动了一本书时
```

任何一本书的校验或构建失败，整个构建就失败——**站点不会发布半成品**。

单独调试某本书时进到书目录用 mkdocs（`site_url` 回落到 localhost，不影响）：

```bash
cd books/tea && mkdocs serve
```

## 6. 提交

- 提交信息中文、说清做了什么 + 为什么；**每完成一块可独立成立的内容就提交**。
- **提交信息里标明动的是哪本书**，例如 `tea: 第 7 章 白茶·萎凋` / `jewelry: 修正第 3 章折射率`；
  改仓库级的东西（构建脚本、索引页、books.yml）用 `repo:` 前缀。
- push 到 `main` 触发 Actions 构建全部书并发布。

## 7. 通用约束（来自用户全局规范）

- **不主动写报告文件**（`*.md` 总结、`report_*.json` 等）；结论直接说，除非明确要求导出。
- 需要时间戳用**北京时间**：`TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M'`。
- **仓库内所有文件禁止出现绝对路径**——公开仓库会泄漏个人信息；只用相对路径 / 环境变量。
