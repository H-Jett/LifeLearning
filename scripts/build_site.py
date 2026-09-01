#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
构建整个书架站点：每本书各自 mkdocs build 到 site/<slug>/，再生成索引页 site/index.html。

设计要点：
  1. **books.yml 是单一真源**——构建哪些书、索引列哪些书，都从它读，不会漏改。
  2. **各书完全隔离**：各自的 mkdocs.yml、主题、搜索索引、校验脚本。
     本脚本只负责「按顺序调用各书自己的校验和构建」，不碰书的内部。
  3. **site_url 由 base_url 拼出**，通过环境变量 BOOK_SITE_URL 注入
     （各书 mkdocs.yml 里写 `site_url: !ENV [BOOK_SITE_URL, ...]`）。
     所以**仓库改名时只改 books.yml 一行**，不用逐本改配置。

用法：
    python scripts/build_site.py                # 全量构建（含各书自己的校验）
    python scripts/build_site.py --only tea     # 只构建某一本（可重复）
    python scripts/build_site.py --skip-checks  # 跳过各书校验，只构建
    python scripts/build_site.py --check        # 只跑各书校验，不构建
"""

import argparse
import html
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("build_site")

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"
CONFIG = REPO_ROOT / "books.yml"


def load_config() -> dict:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    base = cfg.get("base_url", "")
    if not base.endswith("/"):
        cfg["base_url"] = base + "/"
    return cfg


def run(cmd: str, cwd: Path) -> None:
    """在指定目录跑一条命令，失败直接抛。"""
    log.info("  $ %s  (cwd=%s)", cmd, cwd.relative_to(REPO_ROOT))
    subprocess.run(cmd, cwd=cwd, shell=True, check=True)


def build_book(book: dict, base_url: str, skip_checks: bool, build: bool) -> None:
    book_dir = REPO_ROOT / book["dir"]
    if not (book_dir / "mkdocs.yml").exists():
        raise FileNotFoundError(f"{book['slug']}: 缺少 mkdocs.yml（{book_dir}）")

    log.info("[%s] %s", book["slug"], book["title"])
    if not skip_checks:
        for cmd in book.get("checks", []):
            run(cmd, book_dir)

    if not build:
        return

    out = SITE_DIR / book["slug"]
    env = dict(os.environ, BOOK_SITE_URL=f"{base_url}{book['slug']}/")
    cmd = ["mkdocs", "build", "--strict", "-d", str(out)]
    log.info("  $ %s  (BOOK_SITE_URL=%s)", " ".join(cmd), env["BOOK_SITE_URL"])
    subprocess.run(cmd, cwd=book_dir, env=env, check=True)


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{site_title}</title>
<meta name="description" content="{site_description}">
<style>
  :root {{
    --bg: #fbfbfa; --fg: #1b1b1a; --muted: #6a6a68;
    --card: #ffffff; --line: #e6e6e3; --shadow: 0 1px 2px rgba(0,0,0,.05);
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #16171a; --fg: #e8e8e6; --muted: #9a9a97;
      --card: #1e1f23; --line: #2c2d32; --shadow: none;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--fg);
    font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans CJK SC",
          "Source Han Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 860px; margin: 0 auto; padding: 72px 24px 96px; }}
  header {{ margin-bottom: 48px; }}
  h1 {{ font-size: 30px; margin: 0 0 8px; letter-spacing: -.01em; }}
  .tagline {{ color: var(--muted); font-size: 15px; margin: 0 0 16px; }}
  .desc {{ color: var(--muted); font-size: 14.5px; max-width: 62ch; margin: 0; }}
  .grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }}
  a.card {{
    display: block; text-decoration: none; color: inherit; background: var(--card);
    border: 1px solid var(--line); border-radius: 12px; padding: 22px 22px 20px;
    box-shadow: var(--shadow); transition: transform .12s ease, border-color .12s ease;
    position: relative; overflow: hidden;
  }}
  a.card:hover {{ transform: translateY(-2px); border-color: var(--accent); }}
  a.card::before {{
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--accent);
  }}
  .card h2 {{ font-size: 19px; margin: 0 0 4px; }}
  .card .sub {{ color: var(--muted); font-size: 13.5px; margin: 0 0 12px; }}
  .card p {{ font-size: 14px; margin: 0 0 14px; }}
  .meta {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font-size: 12.5px; }}
  .badge {{
    border: 1px solid var(--accent); color: var(--accent);
    border-radius: 999px; padding: 1px 9px; font-weight: 600;
  }}
  .progress {{ color: var(--muted); }}
  footer {{ margin-top: 56px; color: var(--muted); font-size: 13px; }}
  footer a {{ color: inherit; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>{site_title}</h1>
    <p class="tagline">{site_tagline}</p>
    <p class="desc">{site_description}</p>
  </header>
  <main class="grid">
{cards}
  </main>
  <footer>
    源码与勘误：<a href="{repo_url}">{repo_short}</a>
  </footer>
</div>
</body>
</html>
"""

CARD_TEMPLATE = """    <a class="card" href="{slug}/" style="--accent: {accent}">
      <h2>{title}</h2>
      <p class="sub">{subtitle}</p>
      <p>{description}</p>
      <div class="meta">
        <span class="badge">{status}</span>
        <span class="progress">{progress}</span>
      </div>
    </a>"""


def render_index(cfg: dict) -> None:
    e = lambda s: html.escape(str(s), quote=True)
    cards = "\n".join(
        CARD_TEMPLATE.format(
            slug=e(b["slug"]), accent=e(b.get("accent", "#666")),
            title=e(b["title"]), subtitle=e(b.get("subtitle", "")),
            description=e(b.get("description", "")),
            status=e(b.get("status", "")), progress=e(b.get("progress", "")),
        )
        for b in cfg["books"]
    )
    repo_url = cfg.get("repo_url", "")
    page = INDEX_TEMPLATE.format(
        site_title=e(cfg.get("site_title", "书架")),
        site_tagline=e(cfg.get("site_tagline", "")),
        site_description=e(cfg.get("site_description", "").strip()),
        repo_url=e(repo_url), repo_short=e(repo_url.replace("https://github.com/", "")),
        cards=cards,
    )
    (SITE_DIR / "index.html").write_text(page, encoding="utf-8")
    # Actions 部署的产物直接服务，不走 Jekyll；仍放一个 .nojekyll 作零成本保险
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")
    log.info("索引页已生成: site/index.html（%d 本书）", len(cfg["books"]))


def main() -> int:
    ap = argparse.ArgumentParser(description="构建书架站点")
    ap.add_argument("--only", action="append", metavar="SLUG", help="只处理某本书（可重复）")
    ap.add_argument("--skip-checks", action="store_true", help="跳过各书自己的校验")
    ap.add_argument("--check", action="store_true", help="只跑校验，不构建")
    args = ap.parse_args()

    cfg = load_config()
    books = cfg["books"]
    if args.only:
        wanted = set(args.only)
        unknown = wanted - {b["slug"] for b in books}
        if unknown:
            log.error("books.yml 里没有这些书: %s", ", ".join(sorted(unknown)))
            return 1
        books = [b for b in books if b["slug"] in wanted]

    build = not args.check
    if build and not args.only and SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)      # 全量构建先清干净，避免删掉的书残留在站点里
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    log.info("base_url = %s", cfg["base_url"])
    for b in books:
        build_book(b, cfg["base_url"], args.skip_checks, build)

    if build:
        render_index(cfg)            # 索引始终按 books.yml 全量渲染，即使只构建了一本
        log.info("完成：site/ 下 %d 本书 + 索引页", len(cfg["books"]))
    else:
        log.info("校验通过：%d 本书", len(books))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as e:
        log.error("子命令失败（退出码 %s）: %s", e.returncode, e.cmd)
        sys.exit(1)
