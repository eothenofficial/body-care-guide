# 生活基础扩展版的构建与核对

内容版本 `2026.10.30-2`。保留原300个条目ID，在25个身体部位入口之后，将旧“日常基础”拆为睡眠与作息、饮食与体重、运动与恢复、疲劳与日常风险。全书330条建议、573项去重来源、29个专题。旧基础篇URL继续提供聚合目录。

本版新增30条：睡眠8、饮食11、运动9、疲劳风险2；连同原有10条生活基础，共40条。褪黑素、生酮、断食、代餐、蛋白粉、肌酸、BCAA、减重药、助眠耳机和运动设备按具体目的评估，不以产品类别概括所有品牌。心理内容保留节律与必要求助边界，不扩成心理治疗百科。

## 从项目根目录复现

需要Python 3.11及以上；执行实际阅读器行为测试另需Node.js。

```sh
python drafts/whole-body/lifestyle-20261030/build_release.py
python -m unittest discover -s tests -v
python -m http.server 8131 --bind 127.0.0.1 --directory .draft-preview/lifestyle-20261030/dist
```

浏览器访问 `http://127.0.0.1:8131`。离线入口为 `.draft-preview/lifestyle-20261030/dist/downloads/guide-offline.html`。主项目 `content/` 仍为历史公开基线，不直接覆盖；只运行通用 `scripts/build.py` 不能得到本版330条。

## 输入与审校

- 上版 `revision-20261030/build_release.py` 返回完整300条；本目录四组 `*-entries.json` 和 `*-sources.json` 是新增内容输入。
- `build_release.py` 统一来源身份、DOI格式、单元顺序与稳定引用，生成离线HTML、静态分享页、Markdown、JSON与只读API。
- `*-audit.json`、独立复核记录及 `editorial-review.json` 记录实际核读范围和限制；不能把索引/摘要写成读完全文，也不能把AI复核写成医生签审。
- 网页收藏快捷入口、目录独立滚动、回到顶部及收藏导入/导出来自 `web/`；所有版本统一构建，不能手工只改导出HTML。
- 最终测试记录绑定离线HTML的SHA256。`package_release.py` 验证测试、来源图、旧ID、导出同源及公共文案后生成阅读文件与完整源码ZIP，并保留旧日期目录。

交付目录为项目上级 `身体护理指南_2026-10-30_生活基础扩展版/`。只在完成最后一次构建和测试记录后运行本目录 `package_release.py`。ZIP中的源码、SOP、Prompt、验收清单与同版网页一并提供。

临床状态保持 `not_clinically_reviewed`。所有研究与测试限度见对应记录；本次本地改动未推送GitHub或部署到线上站点。
