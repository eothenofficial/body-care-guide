# 少走弯路的人体保养指南

## 从头到脚，学会照顾自己。

我们从小认真学过怎么读书、怎么考试，却很少系统学过怎么照顾自己的身体。眼睛干涩、嘴唇起皮、口腔溃疡、肩腰酸痛、皮肤起疙瘩……这些不大不小的困扰，常常被一句“忍忍就好了”带过去。可到底该观察什么、怎么自护、什么时候需要就医，我们未必清楚。

身体常识没学明白，保养的广告倒看了不少。叶黄素、护眼仪、蒸汽眼罩、漱口水……它们分别能解决什么问题，对谁有用，哪些可有可无？这份指南把日常不适、护理习惯和产品用途逐一查证，让你先弄清自己的需要，再决定怎么做、买不买。用更少的试错，把身体照顾好，少受罪，也少花冤枉钱。

**[在线阅读](https://eothenofficial.github.io/body-care-guide/)** · [下载离线 HTML](https://eothenofficial.github.io/body-care-guide/downloads/guide-offline.html) · [完整 Markdown](https://eothenofficial.github.io/body-care-guide/downloads/guide.md) · [问题与纠错](https://github.com/eothenofficial/body-care-guide/issues)

当前内容版本 **2026.10.30-8**：**29个专题、341条建议、638项去重来源**。覆盖全年龄段、所有性别；每条适用范围分别标注，不能把全年龄定位理解成所有建议都适合所有人。

为自己查，也为家人查。按需选读，不必把护理变成一张任务清单。内容尚未经过临床医生逐条签审，工程检查通过不代表临床认证，也不能代替个人检查、诊断与处方。

## 怎样查阅

- 按身体部位查找，或输入症状、习惯与用品名称；支持年龄和男女条件组合筛选。
- 标题和摘要先说明行动，正文解释概念、证据、适用条件与具体做法；专业名词就近介绍。
- 来源有统一书目、链接、DOI、支持范围和局限，可从正文回查。
- 可以收藏、导出与导入收藏、打印、离线阅读；9条已合并建议的旧链接继续有效。
- 手机提供常驻的首页、目录、查找与筛选入口；目录独立滚动，按钮和图标统一，正文与静态分享页均适配小屏阅读。

搜索和收藏在本机浏览器内完成，没有账号、广告追踪或症状上传接口。更换浏览器或清除存储可能影响收藏，请使用导出备份。

## 在本地构建当前版本

需要 **Python 3.12**；完整工程测试另需 **Node.js 24**，不需要 npm、数据库或付费服务。构建使用 Python 标准库。

```sh
python build.py --check
python scripts/run_current_checks.py
python build.py
python -m http.server 8000 --directory dist
```

打开 `http://localhost:8000`。也可以直接打开 `dist/downloads/guide-offline.html`，无需启动服务器。完整源码可用 GitHub 的 `Code → Download ZIP` 下载。

`python build.py` 与 `python scripts/build_current.py` 是同一个当前发布入口。`--check` 会重新准备 `.draft-preview/current/content` 与 `web`，验证当前内容和资源，不生成新的 `dist`。完整构建先在暂存目录生成，再复制到根 `dist/`。配置和当前已确认来源见 [release/current.json](release/current.json)；版本、条目数、专题数、来源数或书名不符时构建失败，防止自动发布旧版。

`content/` 和 `python scripts/build.py` 保留第一版七章66条的历史基线及回归测试，**不是当前全书入口**。不要直接编辑生成的 `dist/` 或把旧基线构建当作最新版发布。

## 项目结构与继续维护

| 路径 | 用途 |
| --- | --- |
| `release/current.json` | 当前版本、已确认编辑源、正式网址和数量检查 |
| `drafts/whole-body/` | 从全书资料到逐条修订的可复现编辑源、来源与审核记录 |
| `drafts/whole-body/approved-home-20261030/home-copy.json` | 已确认书名及两段首页介绍 |
| `web/` | 网站界面、原字号与布局、抽象插图及同源SVG标志 |
| `scripts/build_current.py` | 正式网站、API、静态分享页和多格式导出的统一构建入口 |
| `tests/` | 数据、引用、适用人群、旧链接、实际阅读器和发布回归检查 |
| `docs/` | 写作SOP、调用Prompt、验收清单和维护规则 |
| `content/` | 不覆盖的早期公开基线 |
| `.github/` | CI、Pages发布、只生成报告的定期维护和贡献模板 |

完整规范见[全书规划与调用SOP](docs/身体护理指南全书规划与调用SOP.md)、[继续写作Prompt](docs/继续写作Prompt.txt)、[验收清单](docs/身体护理项目验收清单.md)、[发布说明](docs/GITHUB_MVP.md)。后续AI或协作者应先读当前SOP，保留已确认的名字、首页文案、原字号与抽象图，不把历史版本的撤回决定恢复为现行要求。

改正文须同时核查来源身份、证据支持范围、年龄与男女适用条件和旧ID；不能让工具静默改写医学结论。编辑源通过后更新当前发布描述并重新运行完整检查，网页、静态分享页、离线HTML、Markdown和JSON均从同一数据生成。既有稳定条目ID、来源ID、分享路由和线上收藏键继续保留。

## 发布、接口与维护

`main` 上的推送自动触发 CI 和 GitHub Pages。两者均验证当前版、运行全部测试（有跳过视为不完整）并构建，检查失败不会部署。以对应提交的 Actions 最终结果及线上 `api/v1/manifest.json` 为准，不能仅凭提交成功就声称网站更新。

```text
api/v1/manifest.json
api/v1/chapters.json
api/v1/entries.json
api/v1/sources.json
```

这些是版本化静态数据，没有在线诊断或处方服务。每条建议有不依赖JavaScript的 `read/<id>/` 完整分享页；打印与PDF由浏览器提供，没有预生成PDF。

`manifest.reader_revision`标识阅读界面版本，与医学内容的`content_version`分开。网页按实际文件哈希更新样式、脚本与数据的缓存地址；界面修改不冒充医学资料重新核查。

每周维护先准备当前全书，再对 `.draft-preview/current` 运行链接和复核报告，不修改医学正文、不创建Issue或PR。链接可达不代表结论正确；到期提醒不证明结论过时。旧发布记录只证明各自历史提交的状态。

## 来源、许可与边界

项目参考 [HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter) 的行动条目、多格式阅读与可追溯维护思路，护理内容和网站代码独立编写。参考项目固定研究版本为 `e2605d3e2242bd6216c9255192b8a8957a08c55a`。

当前尚未授予对外再分发许可；公开仓库不等于采用MIT或CC许可。代码与原创内容的正式许可证待作者确定，第三方论文、机构页面和商标各自保留权利。临床专业签审、维护分工与分支保护也不能仅凭本次发布视为完成。
