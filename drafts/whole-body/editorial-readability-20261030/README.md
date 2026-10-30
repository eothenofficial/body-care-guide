# 整书表达与阅读体验构建

版本2026.10.30-5：输入350条，全部逐条阅读并改写标题、独立摘要与正文；9组合并后341条、29个专题。原637项来源保留，另加入首页实际核读的NIMH患者教育，共638项、108项DOI。纯表达重组不等于重新完成637项来源的系统综述或临床签审。

## 修改输入

`head`126条、`intimate`100条、`body`124条各有原始输入快照、rewrites、merges和逐条audit。原标题/摘要/正文不靠截断或批量加模板改写；重要数字、引用集合和人群保留。9组合并只发生在年龄性别一致的条目中，部分相近但年龄不同者不合并。`entry_aliases`把旧入口指向完整新文；旧静态分享页仍直接包含完整正文，收藏/导入自动归并且搜索可认旧标题。

首页`home-content.json`解释用途、全年龄与所有性别、身体与情绪的双向关系、三种收获和阅读方法。`home-sources.json`记录新增主张真实核读范围；不把基本需要自查当作精神或躯体疾病的全部解释。

各组完成后交叉对照旧文与新文，检查医疗含义、引用附近主张与自然语言；精确修补记录另存。独立复核最终绑定rewrites/merges哈希，首页绑定content/sources。原作者生成脚本只供追溯，复核后不再运行覆盖精修raw。

## 构建与验证

在项目根目录，用Python3.11+运行：

```sh
python drafts/whole-body/editorial-readability-20261030/build_release.py
python drafts/whole-body/editorial-readability-20261030/run_checks.py
python drafts/whole-body/editorial-readability-20261030/package_release.py
```

生成内容在`.draft-preview/editorial-readability-20261030/dist`。此入口读取nutrition→sleep→lifestyle→revision的历史已审输入，再应用本轮最终JSON；`content/`旧公开基线不替换。`--preview-original`只供提前验证新阅读界面，不作为本轮完整成品打包；打包入口要求全部独立复核的最终文件哈希对应。

界面正文默认20px，顶部“阅读设置”支持18/20/22/24字号、两种行距、试读、恢复默认和本地保存。字号变更不改搜索、人群、路由或收藏。静态页同样默认放大，可进入有阅读设置的完整阅读器。窗口与手机断点、模态键盘和存储失败须检查，不能只凭CSS或单元测试声称实际浏览均通过。

`run_checks.py`绑定最终HTML哈希；`package_release.py`核网页内嵌数据、API、Markdown、静态页与来源图一致后，生成上级`身体护理指南_2026-10-30_阅读优化版`与完整项目ZIP。`reproduce_source.py`从该ZIP只提取项目源文件，在工作区按manifest的SOURCE_DATE_EPOCH重建并逐字节比较离线HTML。全文缓存不需要，也不放入分享源码包。

实际覆盖、合并与长度变化见editorial-coverage；独立复核、补丁、browser-review、test-results、source-reproduction与delivery-receipt分别说明真实检查范围。不存在或未通过的记录不能因本README列出步骤就视作完成。尚未临床医生逐条签审，本轮不自动推送GitHub或部署。
