# 已确认书名与首页介绍

内容版本2026.10.30-8。本轮按照用户“可以，就按照这一版改”的授权，采用正式主名《少走弯路的人体保养指南》、保留Hero“从头到脚，学会照顾自己。”，逐字使用`home-copy.json`里已确认的两段介绍，不再将其记为候选。

首页保留原字号、留白、左右分栏、A抽象图和同源SVG图标。两段介绍分别呈现为完整段落，不截断、不缩写；内容增加所需的纵向高度自然伸展，不增加卡片或改变主目录结构。左上完整书名按前缀和主名分行，以保留原侧栏宽度。

```sh
python drafts/whole-body/approved-home-20261030/build_release.py
python drafts/whole-body/approved-home-20261030/run_checks.py
python drafts/whole-body/approved-home-20261030/package_release.py
python drafts/whole-body/approved-home-20261030/reproduce_source.py
```

输出位于`.draft-preview/approved-home-20261030/dist`，交付位于上级`少走弯路的人体保养指南_2026-10-30`。网页品牌、页签、Hero眉题、页脚、分享页、打印、Markdown/JSON内的书名及下载显示名称使用同一正式名称。源文件中旧维护文档路径保留兼容，仓库URL、稳定条目ID、原分享路由和收藏存储键不变。旧日期交付与原`content/`公开基线保留。

341条医学正文、638项来源、29个专题和9个合并别名不改。新增文案是导览说明，不扩大证据支持范围；仍未经过临床医生逐条签审。工程验证及源码重建记录单独保存，不把它们称为医学认证。本轮未自动同步GitHub或部署。
