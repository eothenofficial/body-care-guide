# 饮食与体重扩展构建

本轮在338条睡眠增补版本上新增12条营养/血糖/体重体型内容，并明确修订原nutrition-009药物治疗入口。全书为350条、29个专题；饮食与体重27条、7个单元。旧338个entry ID及原5个营养unit ID均保留，`content/`公开数据基线不覆盖。

## 输入与研究记录

`foundation`：低钠钾盐、一日餐食、精制/超加工和标签；`glycemia`：餐后实践、筛查与设备；`medications`：009修订、针剂比较、安全、其他药物与渠道；`management`：BMI/腰围/体脂秤、减脂与抗阻、外观塑形、进食安全。各组保存entries、sources、audit和不同作者的independent-review。原作者生成器只供追溯，不在复核冻结后重新运行覆盖raw。

实际阅读范围、资助、推导限制和受限访问记录在source及audit内。独立AI复核不等于临床医生审核；状态仍为`not_clinically_reviewed`。说明书与许可会变化，旧版或未获得全文的情形明确记录，不补造最新版本。

`research-medications/`是本地核读缓存，不是构建输入，不打入分享源码包；包内保留正式题录、原始公开链接、实际核读范围与审计，避免把第三方期刊全文当本项目内容分发。

## 复现

在项目根目录用Python3.11+运行：

```sh
python drafts/whole-body/nutrition-followup-20261030/build_release.py
python -m unittest discover -s tests -v
```

当前构建依次调用revision→lifestyle→sleep-followup，再合并本目录最终raw。`build_release.py`先校验4份独立复核的8个entries/sources文件哈希；修改输入必须重新审阅。产物在`.draft-preview/nutrition-followup-20261030/dist`，包括在线静态站、离线HTML、Markdown/JSON/API及独立分享页。

`package_release.py`要求真实测试结果绑定当前离线HTML SHA256，再生成项目上级的`身体护理指南_2026-10-30_饮食体重增补版`和完整源码ZIP。源码重建按manifest中的build_at设置SOURCE_DATE_EPOCH，以排除时间戳差异后比较HTML；阅读数据与当前导出保持同源。没有自动推送GitHub或替换线上站点。

具体数量、文件哈希、测试与实际浏览器范围以build-report、test-results、browser-review、source-reproduction及delivery-receipt为准。未完成的检查不因本文写了步骤就视作通过。
