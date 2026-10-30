# 网站与内容架构

当前整书《少走弯路的人体保养指南》以`release/current.json`选择已批准编辑源，由`python build.py`或`scripts/build_current.py`生成正式站点；包含29个专题、341条建议、638项去重来源，面向全年龄与所有性别。原`content/`和`scripts/build.py`保持历史公开基线。正式构建保留真实网址及线上收藏键，在`.draft-preview/current`准备数据后输出根`dist/`；CI、Pages和维护使用同一当前入口。现行规范见项目README、[全书SOP](身体护理指南全书规划与调用SOP.md)和[发布步骤](GITHUB_MVP.md)。下文首版42文件、66条及已发布记录只描述2026-10-29工程底座，不能代替当前提交的远端验收。

合并条目使用`book.entry_aliases`，导出到`manifest.entry_aliases`，例如`{"eyes-015":"eyes-007"}`。`entries`仅列完整主条目；客户端收到旧ID应先按别名解析，再按主条目的年龄/性别条件展示。别名不能自指、指向不存在条目或与主条目重名；退休ID不得复用。旧静态分享地址包含完整新文，旧收藏/导入以主ID去重。

`manifest.home_content`保存首页文案与引用。首页只呈现短引言、统计与查找，完整导览保留在项目说明的折叠内容和`book.front_matter`导出中。当前按用户最新偏好取消阅读设置，不读写先前的字号键；旧键即使留在浏览器也不会影响默认比例。书签、主题和人群URL参数仍按各自规则工作，不改变系统缩放。

当前已确认的A抽象插画来自`web/assets/home-portrait-abstract.png`。桌面保留Hero右图；手机在标题旁保留小幅同图，完整介绍占整行，不再执行早期的窄屏隐藏规则。品牌SVG与favicon沿用同一抽象人物。构建器把同一PNG内嵌进离线版，favicon也内嵌。来源与原图生成提示词见`web/assets/abstract-brand-notes.md`；早期被拒绝资产仅作历史材料，不恢复为当前设计。正式主名和两段介绍保持逐字一致。

手机（宽760px及以下，或宽1024px及以下且高500px及以下的短横屏）使用固定顶栏的首页、目录、查找与筛选；常规桌面原侧栏和字号保留。CSS与JS使用相同断点条件。手机目录为顶栏下的面板，章节区独立滚动，背景锁定且不可交互，退出后恢复阅读位置；关闭、遮罩、Escape、导航和跨断点均处理状态与焦点。同路由的首页/查找也显式收起目录，不能只依赖hashchange。主题入口在手机目录内，横屏也保持可达；桌面原位置不变。收藏、复制链接和返回操作采用统一尺寸，长来源、单元标签与表格各有换行或局部滚动规则。

静态分享页不加载JavaScript，同样有手机固定导航和可滚动表格；它不能伪装成拥有SPA的收藏/筛选功能。`manifest.reader_revision`由界面源码生成，与医学内容版本分开；生成的首页资源URL按各文件实际字节哈希追加缓存参数，静态分享页也携带样式版本。原始web/index保持无版本参数以供离线内嵌校验，离线文件不依赖这些外部资源。

读者显示名称由`manifest.title`统一提供，页面标题、品牌、Hero眉题、页脚及下载文件名称不再硬编码旧书名。侧栏将同一完整名称分为前缀和主名两行，保留原宽度。`home_content.lead`以空行分段，网页渲染完整的两个段落，Markdown保持相同空行；正文条目和来源数据不因品牌更名而改写。工程维护文档的旧文件名保留以免破坏既有链接，当前项目入口与正式交付文件使用新名。

状态：公开仓库[eothenofficial/body-care-guide](https://github.com/eothenofficial/body-care-guide)已创建，42个源文件已齐，完整提交`b76e1e3c4510834db9635b1d07d6f5baf408243f`已通过CI及Pages部署，网站为[身体护理指南](https://eothenofficial.github.io/body-care-guide/)。首版只有五官与头部七章，内容为案头资料复核，未经临床专业人员签审。许可证、维护分工与远端分支保护仍待落实；后续更改应单独检查对应运行。平台事实核查日期：2026-10-29。

## 让同一份内容支撑阅读与复用

项目首先是一份可追溯的护理指南。网站提供易读入口，Git 保存修改过程，静态 JSON 供搜索、目录和后续开发复用。各类输出使用同一内容来源，避免网页与接口各自维护一套医学结论。

```mermaid
flowchart LR
  A[结构化条目与文献] --> B[结构与引用校验]
  B --> C[静态构建]
  C --> D[阅读页面与站内搜索]
  C --> E[只读 JSON]
  F[问题报告与新证据候选] --> G[人工核对与 PR 审阅]
  G --> A
```

内容层保留原有六项：成本、说人话、收益、证据等级、来源、备注。条目与文献各有稳定 ID；显示用的文献序号存于 `sources[].number`，由构建按此值呈现，不能作为接口中的永久标识。重排显示编号应显式修改来源数据并重建全部产物。章节、主题单元和条目是不同层级，不能只靠标题文字或出现顺序猜测关系。

## 目录与构建契约

构建使用 Python 3 标准库，不需要安装第三方 Python 包或前端框架；阅读界面使用原生 HTML、CSS 和 JavaScript。

| 路径 | 作用 |
| --- | --- |
| `content/chapters/*.json` | 正式编辑的章节与条目数据，属于 canonical 来源 |
| `content/sources.json` | 文献、稳定来源 ID 与可追溯元数据 |
| `content/config.json`、`content/id-registry.json` | 发布配置与显式稳定 ID 注册表 |
| `web/index.html`、`web/styles.css`、`web/app.js` | 页面模板、样式和交互 |
| `scripts/build.py` | 校验与生成静态产物的入口 |
| `scripts/static_pages.py` | 逐条生成无需 JavaScript 的分享页，以及按正式网址生成站点地图 |
| `docs/` | 架构、证据政策、协作和发布说明 |
| `dist/` | 生成的网站、条目分享页、静态接口、离线单 HTML、Markdown 与 JSON；不直接编辑 |

在项目根目录运行 `python scripts/build.py`。运行时版本以根 README 和 CI 的实际固定版本为准。构建成功只证明程序检查通过，不能推断医学结论已经临床签审。

当前数据契约为 `schema_version: 1.0.0`，首批内容版本为 `content_version: 2026.10.28-1`。条目 ID 如 `eyes-001`，来源采用基于来源标识生成的 hash ID；更改正文、排序或显示编号时不重用旧条目 ID。来源身份变化要显式迁移关联，不能手动改 hash 冒充原来源。

网页、离线版和 Markdown 都是导出格式。文字纠错先改 JSON 再重建，避免下载版与在线版各自漂移。仅构建日期变新不能自动刷新医学核查日期或声称内容已更新。

## 四层各做一件事

| 层 | 职责 | 不承担的职责 |
| --- | --- | --- |
| 内容与证据 | 保存行动、适用人群、收益、限制、文献和核查记录 | 不从商品广告自动生成结论 |
| 校验与构建 | 检查字段、ID、引用、路由，生成固定产物 | 不替代证据审读，也不自动提升证据等级 |
| 阅读界面 | 目录、搜索、可分享链接、来源展开、核查日期与版本说明 | 不根据访客症状给诊断或用药方案 |
| 发布与协作 | PR、预览、版本、回退、问题追踪 | 不把托管平台或自动检查当作医学背书 |

目前66个 `read/<id>/index.html` 分享页静态输出完整六字段和对应来源，无需 JavaScript。首页、章节、搜索、收藏和 `#/print` 打印界面由 JavaScript 渲染；没有单独预生成 PDF 或打印文件，PDF 由浏览器打印保存。阅读数据随 `data.js` 嵌入，离线版再内嵌样式、脚本和数据。首版不引入登录、病历上传、广告跟踪或用户症状存储。国内外访问质量需要用实际网络测试，不能凭 CDN 名称承诺速度或可用性。

## 静态接口的边界

首版接口是构建时生成、通过 GET 读取的 JSON 文件：返回公开指南内容、稳定 ID、版本和来源关系。发布后的相对路径为：

- `api/v1/entries.json`：条目。
- `api/v1/sources.json`：来源。
- `api/v1/chapters.json`：章节与主题层级。
- `api/v1/manifest.json`：格式与内容版本等发布信息。

这些文件构建到 `dist/api/v1/`。项目站访问时前面可能有仓库子路径。它们不接收个人健康资料、不写回内容，也不执行诊断、风险评分、处方或问答推理。

`entries.json`、`sources.json` 和 `chapters.json` 分别以 `{schema_version, content_version, entries|sources|chapters}` 包装数组；`manifest.json` 直接返回清单对象。主要字段如下：

| 对象 | 字段与含义 |
| --- | --- |
| 条目 | `id`、`chapter_id`、`unit_id`、`ordinal`、`title`、可选 `summary`、`fields`、`evidence_labels`、`tags`、`source_ids`、`content_checked_at`、`clinical_review_status` |
| 六字段 `fields` | `cost`、`plain`、`benefit`、`evidence`、`sources`、`notes`，值为保留稳定引用标识的 Markdown；`evidence_labels` 可含多个等级，不代表整条建议统一评级 |
| 来源 | `id`、`number`、`citation`、`url`、`type`、`support`、`limitations`、`legacy_id`、`legacy_aliases`、`content_checked_at` |
| 章节 | `id`、`title`、`subtitle`、`order`、`intro`、`units`；单元使用 `entry_ids` 关联条目，不嵌入条目正文 |
| 清单 | 格式/内容版本、数量、核查日期、研究与临床审阅状态、`build_at`、网址、`api`、`downloads`、`book` 与 `planned_parts` |

完整下载 `downloads/guide.json` 是 `{manifest, entries, sources, chapters}`，不同于单个 API 文件的包装。清单不含 Git 提交哈希；部署后需另由发布记录或 Actions 运行关联提交。`build_at` 是构建时间，不是医学复核时间。

`summary` 是供章节、搜索与收藏列表使用的独立纯文本段落，通常约120至170字、两三句；不用正文表格、脚注或Markdown充当摘要。它概括读者应先知道的结论和适用条件，具体理由、证据及比较表保留在六字段正文。构建器原样保留此可选字段，旧数据无此字段仍兼容；阅读器回退到正文首个非表格段的有限长度文字。卡片最多显示五行，实际行数随屏幕宽度变化。摘要须与正文同步审读，不从摘要另行推出新的医学结论。

2026-10-29新增的省略规则：六字段键形状保持兼容，允许 `fields.cost` 与 `fields.notes` 为空字符串；行动正文、收益、证据和来源仍须非空。缺少可靠且有实际信息的成本，或没有额外备注时，网页、分享页、Markdown和打印均跳过相应标题及段落。旧版有内容的字段照常显示，不渲染“价格待核”等占位文案。安全条件必须留在正文，不能因为省略备注而遗漏。

全身校对版在book与manifest中可附带 `body_layout` 数组。每项包含 `title`、`description` 与 `chapters`；`chapters`是 `{id, title}` 对象数组，只引用已交付的章节，未交付时为空。此结构只定义从头到脚的主目录；章节及条目正文仍各有唯一归属。阅读器使用实际章节的标题与摘要生成新部位入口，无须硬编码新页面。未交付的篇目显示状态，不生成通往不存在正文的链接。旧版没有此字段时保留原首页。合订稿按 `drafts/whole-body/plan.json` 的身体顺序编排，不按完成时间排列。

可选 `search_examples` 为维护者选择的检索词数组，随book进入manifest，供首页快捷入口使用。独立篇只用本篇确有内容的词，合订稿使用跨部位示例；没有此字段的旧版保留原快捷词。它不是搜索热度、产品排名或个体诊断结果。

接口版本与正文发布版本分别记录；破坏兼容性的数据格式变化使用新版本。发布记录应能对应 Git 提交，消费者应保存读取时的版本。跨域访问、缓存与返回类型按选定平台实测后写入契约；没有配置和测试前不承诺服务等级。

## 托管可替换，内容保持独立

GitHub 已作为主仓库，GitHub Pages 已承载首版公开网站；Cloudflare Pages保留为可选替代托管方案，尚未为本项目另行配置。若以后增加镜像，应使用同一提交构建的产物，避免出现两个不同内容的“最新版”。GitHub Pages 本身提供静态托管，适用于本项目这一阶段。[官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)

正式访问入口为`https://eothenofficial.github.io/body-care-guide/`，配置保留了项目子路径；未配置自定义域名。首页、搜索、正文、来源、分享页和线上离线HTML已实际打开，manifest接口返回7章、66条、170项来源及正确网址；其他网络、下载与404等检查按每次发布记录分别说明，不把当前成功扩展成所有功能和环境均已验证。若以后增加实时服务，再单独评估服务器、隐私和维护责任，不借用静态接口之名直接加诊断功能。

配套文档：[证据政策](EVIDENCE_POLICY.md)、[发布方案](PUBLISHING.md)、[协作方式](CONTRIBUTING.md)、[路线图](ROADMAP.md)。


## 2026-10-30目录与筛选修订

当前全书构建入口为`drafts/whole-body/revision-20261030/build_release.py`，原17个编辑输入生成26个具体身体部位页面，仍有300条建议与516项来源。每条原ID保留，`chapter_id`反映当前归属，`legacy_chapter_id`记录原篇；旧章节URL由manifest的`chapter_aliases: {旧ID: {title, chapter_ids: [...]}}`指向拆分后的部位组，避免旧链接失效。新章节ID与旧组ID不同，防止循环导航。章节`icon`必须匹配内嵌SVG symbol，`body_group`提供侧栏区域标题。

年龄/性别schema版本1.1.0废止safety_pin绕过。单一过滤函数贯穿搜索、章卡片/目录、收藏、相邻条目、来源引用关联与打印。直接访问不匹配条目显示范围提示；不会把完整正文强行展示。部分匹配的混合导语不展示；切换人群导致单元无结果时退回本章匹配内容。导出全书明确不受筛选影响。详见AUDIENCE_MODEL.md与实际JavaScript回归测试。

读者文字、工作指令及审计记录分开。页面标题不含校对稿、交付稿等；临床审核元数据仍真实保留。编辑核对日不替代原医学核读日。旧草稿构建器仅作历史复现，当前发布包应使用本轮dist与同版数据，不与旧content混装。
