# 内容与迁移约定

`chapters/*.json`、`sources.json`、`book.json` 是独立构建输入；构建不读取原来MVP目录，也不访问网络。`review-log.json`保留66条案头核查的原始记录，医学审阅状态仍是`not_clinically_reviewed`。

- 条目ID和单元ID在`id-registry.json`显式登记。`eyes-001`等ID发布后保持稳定，展示序号`ordinal`与ID分开；改变标题、调序或插入新条目时，不重新给已有条目发ID。
- 条目ID前缀只记录首次分配时的分类。跨章移动时保留ID，同时更新`chapter_id`、`unit_id`和两章的单元成员关系；注册表保留原有身份，分享链接不变。
- 来源ID取DOI优先、规范化URL兜底的身份字符串，计算SHA-256前12位。首次迁移后以注册表为准；修正书目或URL时须显式审查身份，不静默产生新ID。原编号和别名保留用于追溯。
- 六字段的正文保持Markdown，只把`[数字]`引用变为`[@src-xxxxxxxxxxxx]`。`source_ids`是整条六字段引用并集，因部分引用只出现在收益或备注里。
- `evidence_labels`只提取原文明确声明的等级，不把“不能沿用A”当作新的A级证据。原始证据等级段落始终完整保留；标签不能替代其限定。
- `tags`只是少量关键词产生的编辑分类，不是医学分诊、个体推荐或产品评级。规则位于`scripts/content_model.py`，可以人工校准。
- `content_checked_at`为原始案头核查版次日期，不能用构建时间覆盖。`build_at`只表示静态文件生成时间；需要可复现构建时可设置`SOURCE_DATE_EPOCH`。
- 来源书目的网页项可能以`Available from:`结尾，URL另存于`url`；构建排版时将它链接，不补造出版日期或DOI。
- 未来篇幅在`config.json`只能标为`planned`，不生成已发布的占位医学内容。

迁移器是一次性工具，默认拒绝标题/位置发生变化后按旧序号自动复用ID。编辑已导入的canonical JSON即可，不必每次修改内容都重新导入。原MVP引用已重排，迁移只使用当前`number`，不使用`previous_number`。

```sh
python scripts/import_legacy.py --manuscript /path/to/五官与头部护理指南_MVP修订稿.md --sources /path/to/修订证据与核查记录.json --audits /path/to/66条结论证据与推导核查.json
python build.py --check
python build.py
python -m unittest discover -s tests -v
```

静态API为`dist/api/v1/{manifest,entries,sources,chapters}.json`。条目、来源、章节列表各有`schema_version`和`content_version`包裹；`window.__GUIDE_DATA__`及完整JSON下载中的三个列表直接是数组。下载还包括书籍Markdown与把样式、数据、脚本内联的单文件HTML。
