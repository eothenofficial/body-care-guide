# 第一次把指南发布到GitHub

仓库：[eothenofficial/body-care-guide](https://github.com/eothenofficial/body-care-guide)。
阅读网址：[身体护理指南](https://eothenofficial.github.io/body-care-guide/)，已通过[首次Pages部署](https://github.com/eothenofficial/body-care-guide/actions/runs/40822982762)，首页、搜索、正文、来源与分享页已实际打开。后续每次提交仍须检查对应运行结果。

## 只跑通这四步

1. 在GitHub新建名为`body-care-guide`的Public仓库。这一步已完成。
2. 打开仓库的`Upload files`，把干净上传目录**里面的内容**拖进上传区域。不要上传ZIP，也不要把外层`body-care-guide`文件夹一起拖进去。提交说明可写`发布五官与头部护理指南MVP`，点击`Commit changes`提交。
3. 在仓库选择`Settings → Pages → Build and deployment → Source → GitHub Actions`。已有工作流，无需使用GitHub推荐模板或购买域名。
4. 打开`Actions → 发布 GitHub Pages → Run workflow`，选择`main`后运行。状态成功后回到`Settings → Pages → Visit site`打开实际网址。

上传后，仓库根目录应该直接看见：

```text
.github/
content/
docs/
scripts/
tests/
web/
.gitignore
build.py
README.md
```

上传目录共42个源文件。**浏览器拖拽可能漏掉点号开头的文件或文件夹，本轮首次上传就漏过`.github`和`.gitignore`。**提交前后都要逐一核对，不能只看拖拽操作似乎成功：

- 根目录有`.gitignore`。
- `.github/workflows/`内有`ci.yml`、`pages.yml`、`maintenance.yml`三个工作流。
- `.github/ISSUE_TEMPLATE/`内有`config.yml`、`content.yml`、`bug.yml`。
- `.github/`内还有`PULL_REQUEST_TEMPLATE.md`，该目录共7个文件。

如有遗漏，用GitHub的`Add file → Create new file`按完整路径补建，或在对应目录上传并核对内容。不要把本机的`.git`、`.openai`、`dist`、`reports`或缓存文件上传；干净上传目录已排除这些文件。没有`.github/workflows`就不会出现预期的自动发布流程。

## 怎样算这轮成功

- 仓库中有完整源文件，默认分支为`main`。
- Actions中`内容与构建检查`与`发布 GitHub Pages`成功。
- 能从实际网站进入章节、搜索并打开单条建议，来源详情和下载可用。
- 下次修改源文件并提交后，网站会自动更新，不需要重新手工上传生成页面。

首次上传可能早于启用Pages，导致第一次发布在`configure-pages`提示未启用；先完成第3步，再重新运行第4步即可。普通内容测试失败则要查看具体日志并修正，不能用重新运行代替修复。

## 下一次怎样更新

在GitHub打开需要修改的文件，点铅笔编辑，完成后`Commit changes`保存。正文编辑源位于`content/`；页面源位于`web/`。每次提交会触发自动检查与发布。你可以先描述要改什么，由协作者准备修改，再审阅后提交。

不需要同时维护一套手写网页。运行记录在`Actions`里；报错时把对应运行链接发给协作者即可，不要发送密码、验证码或访问令牌。

## 本轮边界

UI、医学正文和未来篇章本轮不重写。公开仓库与网站不等于完成临床审阅。项目许可仍待确定；本轮无需随意添加一个不合适的许可证。

操作依据：[上传文件](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)、[配置Pages发布源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。文档核对日期：2026-10-29。
