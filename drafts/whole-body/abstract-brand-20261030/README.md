# 已确认的抽象插图与图标

内容版本2026.10.30-7。本轮只执行用户明确选择的A抽象线描：右侧插图复用选定PNG；左上标志按同一错位侧脸、单眼与轮廓简化为SVG，替换“护”字与绿色底框；favicon同步。保留原字号、留白、目录、正文、年龄性别筛选和兼容入口。

名称前缀、最终主名组合、Hero大标题与引言仍在讨论。构建输入中的首页文案与上一版本完全相同，不把“少走弯路”或利益表达候选自行写进正式网页。当前读者文件维持原名，待用户确认后统一更名。

```sh
python drafts/whole-body/abstract-brand-20261030/build_release.py
python drafts/whole-body/abstract-brand-20261030/run_checks.py
python drafts/whole-body/abstract-brand-20261030/package_release.py
python drafts/whole-body/abstract-brand-20261030/reproduce_source.py
```

输出为`.draft-preview/abstract-brand-20261030/dist`，交付为上级`身体护理指南_2026-10-30_抽象图标版`。原`content/`及旧日期交付保留。新PNG在离线单文件中内嵌，品牌SVG在页面内嵌，favicon同样内嵌，不依赖在线图片服务。

SVG图标是按已选抽象图形手工简化的矢量形状，不声称与PNG逐像素相同；图标不是医学示意图。原图及生成记录见`web/assets/home-portrait-abstract.png`和`abstract-brand-notes.md`。

341条正文、638项来源、29个专题、9个兼容别名均未在本轮改写。工程检查不能代替临床签审。本轮不自动同步GitHub或部署。
