# 网站与内容架构

状态：本地建设稿；仓库所有者、正式仓库地址、许可证与域名尚未确定。首版只有五官与头部七章，内容为案头资料复核，未经临床专业人员签审。本文不表示远端保护规则或发布服务已经配置。平台事实核查日期：2026-10-29。

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
| 条目 | `id`、`chapter_id`、`unit_id`、`ordinal`、`title`、`fields`、`evidence_labels`、`tags`、`source_ids`、`content_checked_at`、`clinical_review_status` |
| 六字段 `fields` | `cost`、`plain`、`benefit`、`evidence`、`sources`、`notes`，值为保留稳定引用标识的 Markdown；`evidence_labels` 可含多个等级，不代表整条建议统一评级 |
| 来源 | `id`、`number`、`citation`、`url`、`type`、`support`、`limitations`、`legacy_id`、`legacy_aliases`、`content_checked_at` |
| 章节 | `id`、`title`、`subtitle`、`order`、`intro`、`units`；单元使用 `entry_ids` 关联条目，不嵌入条目正文 |
| 清单 | 格式/内容版本、数量、核查日期、研究与临床审阅状态、`build_at`、网址、`api`、`downloads`、`book` 与 `planned_parts` |

完整下载 `downloads/guide.json` 是 `{manifest, entries, sources, chapters}`，不同于单个 API 文件的包装。清单不含 Git 提交哈希；部署后需另由发布记录或 Actions 运行关联提交。`build_at` 是构建时间，不是医学复核时间。

接口版本与正文发布版本分别记录；破坏兼容性的数据格式变化使用新版本。发布记录应能对应 Git 提交，消费者应保存读取时的版本。跨域访问、缓存与返回类型按选定平台实测后写入契约；没有配置和测试前不承诺服务等级。

## 托管可替换，内容保持独立

GitHub 作为拟议的主仓库；GitHub Pages 为首版默认发布路线，Cloudflare Pages 为可选的预览或替代托管。两者都应使用同一提交构建的产物，避免出现两个不同内容的“最新版”。GitHub Pages 本身提供静态托管，适用于本项目这一阶段。[官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)

只选一个正式访问入口；镜像显示来源、版本与更新时间。域名尚未配置，代码不能写死假定域名；项目子路径、资源路径、条目直达和 404 都应在上线前验证。若以后增加实时服务，再单独评估服务器、隐私和维护责任，不借用静态接口之名直接加诊断功能。

配套文档：[证据政策](EVIDENCE_POLICY.md)、[发布方案](PUBLISHING.md)、[协作方式](CONTRIBUTING.md)、[路线图](ROADMAP.md)。
