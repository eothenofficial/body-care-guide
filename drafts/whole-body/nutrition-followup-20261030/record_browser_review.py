"""Record root's observed UI checks, with explicit untested boundaries."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
if __name__=='__main__':
    preview=ROOT/'.draft-preview/nutrition-followup-20261030'
    report=dict(checked_at='2026-10-30',method='实际内置浏览器通过本机HTTP；DOM/可访问树与截图结合，不是仅看HTML源码',url='http://127.0.0.1:8133/#/chapter/nutrition',reader_sha256=hashlib.sha256((preview/'dist/downloads/guide-offline.html').read_bytes()).hexdigest(),
        observations=[dict(view='章节',entry_cards=27,tables_on_chapter=0,raw_pipe_characters=False,units=7),dict(view='nutrition-017',result='表格按行列渲染，三制剂BMI门槛与差异可读；空成本字段不显示'),dict(view='引用600',result='实际打开SURMOUNT-5来源弹窗，题录、DOI、支持、局限、阅读范围和原文链接出现'),dict(view='年龄弹窗',result='实际选择儿童并应用；017标题正文隐藏，仅显示筛选提示；清除后恢复'),dict(view='最终构建',result='修改013公开备注后重新构建并刷新浏览器，章节27卡和无裸竖杠/表格再次确认')],
        screenshots=['饮食与体重.png','减重药比较.png'],
        limits=['本轮未重新操作所有器官、男女及全部年龄组合；这些契约由同版自动测试覆盖。','本轮未重测窄屏、file://真实浏览器执行和下载等待；离线数据同源与导出由打包检查验证。','药物表格与引用检查在仅013备注修改前完成；其后药物内容与UI无变，最终章节已刷新。','工程与界面核对不是临床签审。'],clinical_review_status='not_clinically_reviewed')
    (HERE/'browser-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    integrated=json.loads((HERE/'integrated-reader-review.json').read_text(encoding='utf-8'))
    post=dict(checked_at='2026-10-30',prior_integrated_review_input_sha256=integrated['input_sha256'],final_preview_sha256={n:hashlib.sha256((preview/'content'/('chapters/nutrition.json' if n=='nutrition.json' else n)).read_bytes()).hexdigest() for n in ['nutrition.json','sources.json']},change_after_integrated_review='仅013的公开备注去除编辑过程语言，已由原独立复核者再审并更新foundation最终raw哈希；其余正文不变。',blocking_unresolved=[],clinical_review_status='not_clinically_reviewed')
    (HERE/'post-integration-check.json').write_text(json.dumps(post,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
