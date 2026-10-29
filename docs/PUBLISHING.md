# 发布与托管方案

当前状态：本地框架已完成，正在准备发布[所有者私人预览](https://body-care-guide-preview.sea.chatgpt.site)，尚未确认部署成功。公开 GitHub 仓库尚未创建，所有者、仓库名、许可证与正式公众网址仍待确认。以下为方案与操作顺序，不表示已经公开上线。平台文档核查日期：2026-10-29；开通时复核配额和账户可用功能。

## 建议先选一个发布入口

首版采用“GitHub 主仓库 + 静态网站”的路线。默认用 GitHub Pages，便于把源文件、讨论、PR 和发布记录放在同一处；需要更方便的在线预览或独立托管时再选 Cloudflare Pages。两套平台无需同时上线，若保留镜像也应来自同一已确认提交。

| 方案 | 适合本项目的部分 | 需要确认的部分 |
| --- | --- | --- |
| GitHub Pages | 直接从 GitHub 仓库发布静态页面；公开仓库可使用 GitHub Free；支持自定义域名和自定义 Actions 构建 | 项目站通常有仓库子路径；需正确构建链接；不是动态后端 |
| Cloudflare Pages | 可连接 GitHub，推送后构建；可预览改动，正式部署可回退 | 多一个账户与授权面；生产/预览分支、权限、配额及域名要配置 |
| Gitee 仓库镜像 | 可另行评估作为国内代码读取入口 | 官方帮助目录将 Gitee Pages 标为“功能已下线”，目前不列为已核实可用的网站托管路线 |

GitHub 的静态托管与账户范围见[Pages 说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)，Actions 发布见[自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。Cloudflare 的功能分别见[GitHub 接入](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/)、[预览部署](https://developers.cloudflare.com/pages/configuration/preview-deployments/)和[回退](https://developers.cloudflare.com/pages/configuration/rollbacks/)。Gitee 状态依据其[官方帮助目录](https://gitee.com/help.com/)的索引；详情页本次读取超时，今后使用前应重新确认服务状态。

## 配额与地域不要靠想象

当前 GitHub 文档列出：已发布站点不超过 1 GB、月带宽 100 GB 为软限制、部署超过十分钟超时；每小时十次构建的软限制不适用于自定义 Actions 工作流。这些是托管限制，不是项目流量保证。[GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)

Cloudflare Pages Free 当前列出每月 500 次构建、同时一次构建、构建二十分钟超时、每站最多 20,000 个文件、单文件 25 MiB；Functions 请求另计入 Workers 配额。首版只有静态页面和 JSON，不因此需要 Functions。[Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits/)

Cloudflare 官方仍提供 Pages 文档，也提供[迁往 Workers 的指引](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/)；存在迁移指引不等于 Pages 已下线。以后需要运行时服务，再重新评估。任何方案都要实测目标读者所在网络，不承诺“中国大陆一定快”或“永远免费”。

## 首次发布顺序

1. 确认 GitHub 个人账户或组织持有仓库，明确管理员与后备维护者。
2. 选择代码、原创正文及数据的许可，并明确第三方材料例外；决定前不放入猜测的 LICENSE 或许可证徽章。公开仓库并不自动成为可自由复用的开源项目。[GitHub 许可说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
3. 在项目根目录依次运行 `python scripts/build.py --check`、`python -m unittest discover -s tests -v`、`python scripts/build.py`，校验现有结构化内容和本地资源，再生成产物；浏览核验另行进行。清单记录内容版本、核查日期和构建时间，不含 Git 提交哈希，实际发布提交须另记。首批内容版本为 `2026.10.28-1`，案头复核状态不能因部署而变成临床签审。
4. 创建远端仓库并推送；设置受保护主分支、必需检查与审阅要求。再把实际负责人写进 CODEOWNERS，不能保留虚构账号。
5. 选定正式托管；GitHub Pages 选择 Actions 来源，由工作流运行 Python 构建并上传 `dist/`。若改用 Cloudflare，连接指定仓库，以项目根目录为构建根、`python scripts/build.py` 为构建命令、`dist` 为输出目录；仓库外层还有其他文件时先把根目录设为 `body-care-guide`。实际生产分支在控制台明确选择，不依赖首次推送的默认值。
6. 先在私人预览中核验章节、条目直达、资源路径、搜索、JSON、引用链接、404 与移动端；再禁用 JavaScript 核验 `read/eyes-001/` 等静态分享页的完整正文和来源。项目子路径也要测，不能只在根路径预览。私人访问权限由平台配置，不能用搜索引擎索引设置代替。
7. 域名仍为未配置状态。用户确认域名后再按平台说明配置并验证 HTTPS、规范访问地址及旧链接跳转；不用示例域名假装正式网址。

Cloudflare 根域通常要求将域名作为 Cloudflare zone；子域可按官方步骤使用 CNAME，仍需先关联 Pages 项目。实际 DNS 变更前应按所选方案核对。[Cloudflare 自定义域名](https://developers.cloudflare.com/pages/configuration/custom-domains/)

Cloudflare 构建镜像支持 Python，可通过 `PYTHON_VERSION` 或 `.python-version` 固定版本；选用与 CI 实测相同的版本，不依赖平台默认值。纯标准库构建不需要 npm，也不要求引入 Astro 或其他框架。还可在外部 CI 构建后再上传 `dist/`，但这会新增部署凭据与工具，首版不必同时维护两条 Cloudflare 部署路线。[构建镜像](https://developers.cloudflare.com/pages/configuration/build-image/)、[CI 直接上传](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/)

静态 JSON 位于 `dist/api/v1/{entries,sources,chapters,manifest}.json`，没有运行时 API 服务器。CORS、HTTP 缓存和压缩依托宿主配置与实测，不把“提供 JSON”写成对任意第三方浏览器的跨域保证。离线单 HTML、Markdown、JSON 和浏览器打印使用同一份内容，发布前核对没有漏章或丢引用；没有预生成的 PDF 文件。

## 正式网址与索引

`content/config.json` 的 `site_url` 为空时，构建为首页、离线首页和66个静态分享页加入 `noindex, nofollow`，且不生成 `sitemap.xml`；如果输出目录中有旧站点地图，会移除该文件。该设置只是索引提示，不阻止知道网址的人访问。

确认正式 HTTPS 网址后再填写 `site_url`，包括项目站必要的子路径并重建。届时逐条分享页生成 canonical 和 `og:url`，站点地图列出站点根网址及全部分享页；当前构建不会给首页自动添加 canonical。搜索、章节等哈希路由不单独列入站点地图。私人预览地址不作为正式 `site_url` 写入内容配置。

## 工作流与维护报告

`.github/workflows/ci.yml` 在主分支推送、PR 和手动运行时以只读权限执行校验、全部 unittest 和构建。`pages.yml` 只在 `main` 推送或手动触发，构建与部署任务也都限制在 `main`；构建依次通过校验、测试和生成后才上传 `dist/`，部署依赖构建成功。Pages 写入与身份令牌权限只给部署任务。工作流文件就绪不代表远端 Pages 已启用。

`maintenance.yml` 设定每周一02:17 UTC及手动运行，仅产生报告和保留30天的 artifact，不改医学正文、不创建 Issue 或 PR。也可在本地运行：

```sh
python scripts/check_links.py --output-dir reports
python scripts/review_due.py --output-dir reports --interval-days 180
```

前者写入 `link-health.json`、`link-health.md`，仅遇到 HTTP 405 才由 HEAD 回退 GET；404/410、访问限制、限流、服务器错误与网络超时分别记录。可用 `--strict` 让明确缺失的404/410返回失败，403等阻塞不据此判死链。后者写入 `review-due.json`、`review-due.md`，提醒距离 `content_checked_at` 已满180天的记录，并另列缺失、无效、未来日期及尚未临床签审的条目；待临床签审与到期是不同状态。

## 发布权限与回退

PR 检查只读仓库内容，无生产凭据；正式部署只使用已合并且通过检查的提交。抓取脚本、文献机器人、格式化工具和 LLM 均没有直接改主分支的权限。GitHub 保护规则与 CODEOWNERS 需要在远端实际启用，仅提交文件不会自动生效。[保护分支](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)、[CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

GitHub Actions 使用最小权限，部署权限只给部署任务；不要在有高权限的 `pull_request_target` 等上下文检出并运行不可信 PR。依赖锁定并审查工作流改动。[GitHub Actions 安全使用](https://docs.github.com/en/actions/reference/security/secure-use)

每次发布记录提交、内容版本、检查结果和已知限制。技术故障可重新部署上一个可信提交；医学错误回退后仍需在主分支更正并记录，避免下次自动部署再次带回。Cloudflare 的快捷回退只针对成功的生产部署，预览部署不能直接作为回退目标；回退不会代替修复源文件。
