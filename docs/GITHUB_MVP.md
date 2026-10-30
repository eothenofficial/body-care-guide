# 更新GitHub仓库与在线指南

仓库：[eothenofficial/body-care-guide](https://github.com/eothenofficial/body-care-guide)。阅读网址：[少走弯路的人体保养指南](https://eothenofficial.github.io/body-care-guide/)。

当前正式构建描述是`release/current.json`，内容版本2026.10.30-8，341条建议、29个专题、638项去重来源。具体一次发布是否成功，查看该提交对应的Actions和线上manifest，不沿用旧发布成功记录。

## 不需要写代码也能使用

读者直接打开阅读网址；需要离线阅读时，在“项目与下载”下载HTML。需要整个项目，在仓库点`Code → Download ZIP`，解压后保留原目录结构。完整SOP位于`docs/身体护理指南全书规划与调用SOP.md`。

后续正文、UI或来源修改可先交给协作者准备完整文件，在本地预览后更新仓库。不要把整个项目ZIP当作网页源文件直接上传到仓库；ZIP本身不会被Pages自动解压或发布。

## 维护者的更新顺序

1. 获取现有main最新版本，保留远端历史。不要用旧本地目录覆盖别人新增的改动；不能force push跳过冲突。
2. 阅读当前SOP并修改编辑源。已确认书名和首页介绍不是待选项；正文修改另须核对医学证据、适用人群和旧链接。
3. 安装Python3.12与Node24后，依次运行：

```sh
python build.py --check
python scripts/run_current_checks.py
python build.py
```

4. 打开生成页面核对范围与交互。`--check`准备`.draft-preview/current/content`及`web`但不生成新dist，完整构建输出根`dist/`；`scripts/build.py`是历史66条入口，不用于当前发布。
5. 只提交项目源码和必要编辑记录，排除`.git`、凭证、`.env`、`.openai`、缓存、生成dist、报告、本机绝对路径和下载的文献PDF。冻结审核输入不可为上传随意改写。
6. 正常提交并推送main，检查同一提交的“内容与构建检查”和“发布GitHub Pages”均最终成功。未完成前不声称上线。
7. 打开正式站点及`api/v1/manifest.json`，核对2026.10.30-8、341/29/638、书名、两段介绍、代表性条目与旧链接、下载和窄屏阅读。

`.github/`不能漏传。CI和Pages使用当前构建器，Python3.12与Node24运行全部回归测试；测试失败或跳过都阻止发布。Pages来源保留`GitHub Actions`，不需要购买域名或改账号权限。每周维护先准备当前全书，再传`--root .draft-preview/current`，避免只维护早期66条。

## 凭证和故障

Git登录交给GitHub官方流程或Git Credential Manager，不把密码、令牌写进文件、命令行、截图或聊天。更改应用权限必须由账户所有者确认。推送失败先检查具体原因，不能因此伪造成功记录。

保存实际提交SHA、对应CI/Pages运行链接和终态、线上核验结果及时间。本地打包、远端提交、网站部署、实际可读是不同结果。技术故障可以回退到已知可用提交，但仍需在主分支修正，避免下次再次发布错误。

首次42文件与66条试点的历史发布说明不再是当前范围；许可证、临床专业签审、维护分工和分支保护仍需各自落实。工程发布成功不会改变`not_clinically_reviewed`。
