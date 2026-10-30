# 五官、头皮头发与人群分层校对稿

版本：2026.10.29-head-care-audience-review-2。126条、7个模块；本地工作稿，尚未发布，尚未临床签审。

## 本轮变化

- 耳廓凹槽、耳后清洁；穿孔选择、耳洞愈合、感染、过敏、耳夹和重耳饰。
- 牙齿与牙周、嘴唇与口腔黏膜两条路线。旧ID保留，口腔溃疡、口干、舌苔移入黏膜路线。
- 换牙与六龄齿；首次正畸评估、青少年时机、地包天；成人正畸、缺牙比较、义齿维护。
- 儿童视力入口与年龄/男女侧栏。未核对的旧成人内容不假标全龄，急症在人群筛选中保留。

## 文件与复现

chapters是本版可编辑正文，evidence保存来源、原作者审计和独立AI编辑复核。parts是研究片段，不能不经整合直接覆盖章节。SOP.md是本版维护约定，用户风格原稿在references。

从仓库根目录运行：

```powershell
python drafts/head-care-audience/preview.py
python drafts/head-care-audience/verify.py
python -m unittest discover -s tests -q
```

preview.py校验结构后生成.draft-preview/head-care-audience/dist，包括完整离线HTML、Markdown、JSON及逐条静态分享页。构建不改已发布content目录。

新一轮研究片段确需重新整合时，先审读再运行integrate_audience.py；不要把这个脚本当作临床推理或自动分龄工具。原稿保存在drafts/head-care，便于对照。

## 证据边界

新增耳洞护理来源有细节分歧，见ears-audience-audit.json；牙科年龄阈值、保持与义齿储存也不能脱离条件，见dental-age-audit.json。独立复核发现的窝沟封闭引文缺口已补直接NIDCR来源，固定桥表述已收窄到天然牙支持桥。

工程检查只验证数据、引用格式和阅读功能。所有医学条目仍标not_clinically_reviewed；AI编辑复核不等于持证临床签审。
