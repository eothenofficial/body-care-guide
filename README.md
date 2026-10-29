# 身体护理指南

写给年轻人的身体护理参考：弄懂日常习惯和常见用品，比较效果、成本与适用条件，也保留结论背后的证据和局限。

当前第一篇是**五官与头部**，含眼睛、鼻子、嘴唇、完整口腔、耳朵、面部皮肤与头发，共66条建议、170项来源。内容为2026年10月28日的研究修订版，经过案头资料与推导复核，**尚未完成临床医生逐条审阅**。

本目录是可独立构建的网站项目，仓库为 [eothenofficial/body-care-guide](https://github.com/eothenofficial/body-care-guide)。本轮先跑通上传、自动检查与GitHub Pages发布；许可证尚待作者确定。不要将“可运行”或CI通过理解成“所有医学结论已获验证”。

## 直接阅读

- 网站入口：[身体护理指南](https://eothenofficial.github.io/body-care-guide/)（首次部署通过后生效）。
- 第一次发布或更新：[不写代码的GitHub操作步骤](docs/GITHUB_MVP.md)。
- 本地阅读：构建后打开 `dist/index.html`，无需安装前端依赖。
- 离线分享：发送 `dist/downloads/guide-offline.html`。它包含全部内容、检索和阅读界面。
- 打印：在网站“项目与下载”选择“打印与另存PDF”，用浏览器打印完整正文。

离线文件不会自动更新，应同时保留内容版本号。未配置公开仓库时，网站不会出现指向假地址的贡献按钮。

## 本地启动

需要Python 3.11或以上，构建和校验仅使用标准库，不需要npm或数据库。

```sh
python scripts/build.py --check
python -m unittest discover -s tests -v
python scripts/build.py
python -m http.server 8000 --directory dist
```

浏览器打开 `http://localhost:8000`。直接双击离线HTML也能使用。每条建议另有 `read/<id>/` 静态分享页，完整正文和来源无需JavaScript；搜索、筛选与收藏使用阅读界面的JavaScript。

## 已实现的框架

| 用途 | 实现 |
| --- | --- |
| 阅读 | 部位目录、单元顺序、六字段正文、专业名词就近解释 |
| 查找 | 中文全文搜索、常用词映射、部位/证据标签/阅读方向组合筛选 |
| 追溯 | 文内引用、来源详情、支持范围与局限、反查引用条目 |
| 传播 | 66个稳定条目静态分享页、离线单HTML、Markdown/JSON下载、打印样式 |
| 日常使用 | 移动端导航、键盘操作、浅色/深色、本机收藏 |
| 开发 | canonical JSON、显式ID注册表、版本化只读静态API |
| 协作 | 内容纠错/网站故障表单、PR模板、内容贡献规范 |
| 自动化 | 构建前校验、测试、Pages发布工作流、每周维护报告 |

搜索、收藏都在浏览器本地完成。没有广告、第三方统计或症状上传接口。

## 项目结构

```text
content/
  chapters/          # 每章的元数据、单元与条目，唯一编辑源
  sources.json       # 稳定来源ID与书目
  id-registry.json   # 初次迁移后的稳定身份
  book.json          # 导览和证据说明
  review-log.json    # 66条案头核查记录
  config.json        # 标题、仓库与站点网址、后续篇章配置
web/                 # 阅读界面，无外部运行时依赖
scripts/             # 构建、校验、链接与到期报告
tests/               # 数据与维护行为测试
docs/                # 架构、证据、贡献、发布、后续路线
.github/             # CI、Pages、维护与贡献模板
dist/                # 生成结果，不手动编辑、不提交
```

编辑 `content/` 后构建，网站、数据接口和离线文件一起更新。不要直接改 `dist/`，也不要维护一份独立于数据源的网页正文。

## 给后续开发者的接口

构建后可直接读取：

```text
api/v1/manifest.json
api/v1/chapters.json
api/v1/entries.json
api/v1/sources.json
```

API有 `schema_version` 与 `content_version`，条目使用稳定ID，例如 `eyes-001`。来源使用从DOI或规范化URL建立的稳定ID，网页显示编号不承担身份。具体字段见 [架构说明](docs/ARCHITECTURE.md)。静态接口是读资料的入口，不提供诊断、处方或自动生成医学结论的服务。

## 发布与维护

推荐以GitHub保存内容和代码，以GitHub Pages承载公开静态站。`.github/workflows/pages.yml` 已准备构建、测试及部署步骤，但仍需创建自己的仓库，在仓库设置中启用Pages的GitHub Actions发布源。

首次公开前，确认仓库归属、内容许可、维护责任人和联系渠道，并在 `content/config.json` 填入实际仓库与站点网址。当前 `site_url` 为空，构建给首页和静态分享页加入 `noindex, nofollow`，不生成站点地图；配置正式HTTPS站点地址后，才生成分享页的规范网址和站点地图。`noindex` 不是访问权限控制，私人预览仍须由托管平台限制访问。[发布步骤与替代托管](docs/PUBLISHING.md)中区分了已准备的配置和需要GitHub管理员实际启用的保护规则。

自动化只检查机器能判断的事。链接可达不代表论文可信；到期提醒不代表结论已过时；CI通过不代表临床审核完成。医学更改先说明具体问题、证据与推理，再由维护者审查，不能自动爬取或让LLM静默替换结论。

## 继续参与

- [怎样贡献一条内容](docs/CONTRIBUTING.md)
- [证据与医学审核政策](docs/EVIDENCE_POLICY.md)
- [代码与数据结构](docs/ARCHITECTURE.md)
- [后续篇章与功能路线](docs/ROADMAP.md)

本项目参考了 [HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter) 的行动条目、多格式阅读和可追溯维护思路；网站代码与护理内容独立编写，没有直接移植其解析器、广告或统计脚本。研究时固定参考版本为 `e2605d3e2242bd6216c9255192b8a8957a08c55a`。

## 许可状态

当前未授予对外再分发许可。建议后续分别选择代码MIT与内容CC BY 4.0，但应由项目所有者在公开发布前确认，并加入正式许可证文件与署名方式。引用的论文、商标和机构页面各自保留原权利，不能替第三方材料授予许可。
