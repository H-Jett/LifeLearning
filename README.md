# 系统学茶：从一片叶子到一杯茶汤

> 📖 **在线阅读**：<https://H-Jett.github.io/H-Jett-TeaLearning/>

一本"边学边记"的茶学入门书，深度对标**评茶员知识体系**：**工艺原理 + 茶叶化学 + 感官审评**。
不从"记名字"开始，而是先建立机理、再挂名字。

## 核心观点

> **茶的一切技术问题，本质都是一件事——让哪些成分、以多少比例、进入茶汤。**

- **工艺**在定向改造成分（六大茶类的分野 = 改造程度的分野）；
- **冲泡**在选择性溶出成分（四个旋钮各自调的是不同分子）；
- **审评**在从感受反向读出成分格局。

## 快速入口

| 页面 | 说明 |
|------|------|
| [首页 / 大纲与进度](docs/index.md) | 全书导航 |
| [学习路线图](docs/roadmap.md) | 七部分 40 章 + 5 个实战项目 |
| [第一部分 · 茶的物质基础](docs/chapters/01-foundation/00-intro.md) | 🔜 进行中 |
| [第 1 章 · 一片叶子里有什么](docs/chapters/01-foundation/01-leaf-chemistry.md) | ✅ 成分与滋味的对应，全书地基 |
| [术语表](docs/glossary.md) | 成分 / 工艺 / 审评术语（带国标规范词） |
| [国标与文献索引](docs/standards.md) | 所有数值与方法的出处 |
| [冲泡记录表](docs/forms/brewing-log.md) | 可复用的实操记录模板 |

## 这本书怎么保证"正确"

姊妹项目靠真机跑数据自证，茶叶没有 GPU 可跑，所以靠三条纪律：

1. **数值必须有出处**——国标编号 / 教科书 / 明确标注"行业经验值"，并说明波动范围，**不编精确数字**；
2. **区分「机理」与「说法」**——茶圈流传的说法逐条标注证据强度（✅ 有共识 / ⚠️ 有争议 / ❌ 明确错误）；
3. **数字只当示例，讲的是规律**。

**不做医疗建议**：茶与健康只陈述研究现状与证据等级。

## 体例

- 每章：**概念 → 常见说法辨析 → 思考题 → 本章实操**；
- 实操分两档：**🅐 无器具版**（现在就能做）/ **🅑 有条件版**（备齐茶具茶样后再做）；
- 思考题答案单独成册（`docs/qa/`），只记「问题 + 正确答案」；
- 单一真源 = 可移植标准 Markdown，在 **GitHub / 任意 Markdown 阅读器 / MkDocs** 三边都能读。

## 本地构建

```bash
pip install mkdocs-material
python scripts/check_book.py    # 锚点 / 绝对路径 / 出处校验
mkdocs build --strict           # 坏链接即失败（CI 同样跑这条）
mkdocs serve                    # 本地预览 http://127.0.0.1:8000
```

开发约定见 [CLAUDE.md](CLAUDE.md)。

## 姊妹项目

| 项目 | 主题 |
|------|------|
| [InfraLearning](https://github.com/H-Jett/InfraLearning) | 算法工程师的 Infra 入门（推理 → 分布式训练） |
| [MultiModalLearning](https://github.com/H-Jett/MultiModalLearning) | 多模态入门：给 LLM 工程师的一本书 |
