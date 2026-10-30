# 身体护理指南：2026-10-30版本

本版本包含300条建议、516项去重来源、26个具体部位入口。主目录依身体位置分组，每个具体部位有独立SVG图标。正式阅读文件名称为“身体护理指南”，制作指令、审校日志和SOP只放在维护资料中。

## 输入与修订

输入为 `drafts/whole-body/baseline/chapters/` 的7个头面模块、`drafts/whole-body/chapters/` 的10个身体模块，以及上一版核对过的 `compiled/master/sources.json` 来源账本。原始条目与来源ID保留。

本目录的补丁在构建时应用，不回写旧输入，因此可以重复构建；每项文本补丁要求旧值恰好出现一次，输入漂移会停止构建。顺序为全书措辞、头面独立阅读、补充字段阅读、人群标签、目录拆分与单元协调。来源说明补丁只修阅读体验与已核实的取样时序，不重写引用题录或伪造文献读取深度。原版本的阅读文件和归档未被覆盖。

`audience-overrides.json`记录300条人工编辑的人群决定、原标签与理由。`safety_pin`只标急症属性，不能越过年龄或男女筛选。男性和女性专属条目互斥；确实要求双方参与的通用内容保留。具体年龄仅映射查找分段，不生成处方或治疗资格。

`directory.json`由构建器生成，列出26个部位与旧章节兼容入口。原条目链接仍使用旧稳定ID，新章节有不同URL；例如旧`#/chapter/hands`显示手部与指甲两个入口，新`#/chapter/hand-skin`只显示手部皮肤。

## 复现与验证

在项目根目录运行：

```powershell
python -X utf8 drafts/whole-body/revision-20261030/build_release.py
python -X utf8 -m unittest discover -s tests
python -X utf8 drafts/whole-body/revision-20261030/package_release.py
```

构建输出在`.draft-preview/release-20261030/dist/`。离线HTML、完整JSON、Markdown、静态分享页及`api/v1/`由同一份数据生成。`package_release.py`验证输出一致、内部链接和来源可解析、原ID未丢失、公开文案无内部阶段标签，并生成独立阅读文件与源码包；它不推送GitHub或部署。

用HTTP服务预览此dist目录即可验证界面，正式阅读文件可直接双击打开。源代码测试覆盖实际JavaScript执行，而非只测试一份另写的筛选模拟函数。真实浏览器的验证范围与截图另记在`browser-validation.json`，未测场景不写通过。

完整下载是整本内容，页面明确告知不受当前筛选影响；交互搜索、章节、收藏、相邻建议、来源关联与打印应用相同人口规则。

## 医学与编辑边界

本轮逐条核人群，分批通读读者文字并修正指代、操作顺序、术语与内部语言。它不等于重新对516项来源做系统综述，也不等于临床医生签审。各条原医学核读日期保留，新增`editorial_checked_at`区分编辑修改日期。`clinical_review_status`仍如实为`not_clinically_reviewed`。不把工程测试通过或正式文件名称当成医学认证。

写作标准与下一次调用入口在`docs/身体护理指南全书规划与调用SOP.md`、`docs/继续写作Prompt.txt`和`docs/身体护理项目验收清单.md`。用户提供的写作风格原稿保持不变。
