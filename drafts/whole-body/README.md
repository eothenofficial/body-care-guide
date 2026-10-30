# 从头到脚逐篇校对稿

本目录承接已交付的五官与头皮头发126条，按用户授权扩展其余身体部位。主目录采用身体相对位置；正文以症状、生活情境、相关用品与选择条件组织。篇目范围见 `plan.json` 和 `docs/全书身体位置目录.md`，实际完成数量以最新 `compiled/master/build-report.json` 为准。

本轮是供用户校对的本地稿。没有覆盖线上站点或 canonical `content/`，没有把工程检查、引用数量或独立AI编辑复核当作持证临床签审。每条仍标记 `not_clinically_reviewed`。

## 直接阅读

交付目录中的“身体护理指南_从头到脚合订稿_2026-10-29.html”可直接双击，样式、内容与脚本均已内嵌。无需安装软件，也不依赖网络载入正文；访问原文来源需要联网。单篇文件前缀按身体顺序固定，完成较早不改变目录位置。年龄和男女筛选、检索、来源和收藏沿用既有阅读器。

## 内容与证据

- `baseline/`：已交付的头面七模块与来源快照，保留稳定ID。
- `chapters/`：新增篇目可编辑JSON，含章/单元导语、独立摘要、六字段与阅读人群。
- `evidence/*-sources.json`：作者实际核读的来源、支持范围、局限、阅读深度和资助/利益说明；来源别名在构建时转成稳定哈希ID。
- `evidence/*-audit.json`：检索边界、来源冲突、未采用资料与作者核对记录。
- `evidence/*-independent-review.json`：另一编辑者核关键正文与原页后的发现与解决情况。它不等于临床复核。
- `compiled/`：由原稿生成的规范数据、ID注册表、版本与工程检查结果。
- `deliveries/`：各篇交付文件与SHA-256收据。`plan.delivered`决定哪些正文进入合订稿。

每条六字段键名保持兼容；没有可靠成本或有意义备注时允许空字符串，显示端省略空段。紧急条件必须写在行动正文。摘要只用于列表，正文表格与引文保留在详情。证据分级为项目自定A/B/C，不冒充GRADE。

## 复现

在项目根目录使用Python 3运行，无额外Python依赖：

```powershell
python -X utf8 drafts/whole-body/preview.py --part neck
python -X utf8 drafts/whole-body/verify.py --part neck
python -X utf8 drafts/whole-body/preview.py
python -X utf8 drafts/whole-body/verify.py
python -X utf8 -m unittest discover -s tests
```

最后两条构建命令生成合订稿，输出在 `.draft-preview/whole-body/master/dist/`。`downloads/guide-offline.html`为独立阅读文件，`downloads/guide.json`和`api/v1/`供开发者继续使用。Node.js用于执行阅读器测试；未安装时相关测试会明确跳过，不能写成通过。

一篇已经审读且没有未决阻断时，运行 `python -X utf8 drafts/whole-body/deliver.py neck`。此命令串行生成独立稿与ZIP，更新计划，再重新生成合订稿。多个交付命令不要并行运行，以免覆盖共享计划；研究可并行，同一正文指定一位整合者。

全部已授权篇目交付后运行 `python -X utf8 drafts/whole-body/package_review.py` 生成完整源码与阅读包。该脚本校验归档和离线文件一致；不执行Git推送或部署。

## 继续维护

新增问题先确定正文主要归属，补齐对应权威资料，保留旧ID；章节移动不要重发ID。改正文时同步独立摘要、人群、来源支持范围和审读记录。外部链接可访问不代表结论正确；无证据也不等于已证明无效。来源日期、更新日与专业复核日分开记录，不能用未来计划复查日伪装更新。

逐篇核对和工程验证后，再由用户确认内容。公开发布必须另有授权，不能把本目录的全书草稿直接当作线上现有版本。
