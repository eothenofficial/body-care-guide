"""Package the completed local book, each part, and reproducible sources."""
import hashlib
import html
import json
import shutil
import zipfile
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEST = ROOT.parent / '全身护理逐篇交付'
DIST = ROOT / '.draft-preview/whole-body/master/dist'


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan = read(HERE/'plan.json')
    if set(plan['delivered']) != {p['id'] for p in plan['parts']}:
        raise ValueError('All authorized parts must be delivered before final packaging')
    report = read(HERE/'compiled/master/build-report.json')
    validation = read(HERE/'compiled/master/validation.json')
    if validation['entries'] != report['entries']:
        raise ValueError('Stale cumulative validation')
    master = DEST/'身体护理指南_从头到脚合订稿_2026-10-29.html'
    if master.read_bytes() != (DIST/'downloads/guide-offline.html').read_bytes():
        raise ValueError('Delivered reader differs from built reader')
    receipts = [read(HERE/'deliveries'/(part['id']+'.json')) for part in plan['parts']]
    for part, receipt in zip(plan['parts'], receipts):
        if read(HERE/'evidence'/(part['id']+'-independent-review.json')).get('blocking_unresolved'):
            raise ValueError('Unresolved review: '+part['id'])
        for kind in ['html', 'zip']:
            if sha(Path(receipt[kind])) != receipt[kind+'_sha256']:
                raise ValueError('Delivery changed since verification: '+part['id'])
    e = html.escape
    rows = []
    for part, receipt in zip(plan['parts'], receipts):
        rows.append('<tr><td>'+str(part['order']).zfill(2)+'</td><td><a href="'+
            quote(Path(receipt['html']).name)+'">'+e(part['title'])+'</a></td><td>'+e(part['description'])+
            '</td><td>'+str(receipt['entries'])+'</td><td><a href="'+quote(Path(receipt['zip']).name)+'">校对包</a></td></tr>')
    index = DEST/'交付入口.html'
    index.write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>身体护理指南 · 从头到脚交付入口</title><style>
body{margin:0;background:#f6f5ef;color:#263b34;font:16px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1100px;margin:36px auto;padding:0 26px}h1{font-size:30px;margin:0 0 8px}p{margin:8px 0 18px}a{color:#216853;text-underline-offset:3px}.actions{display:flex;flex-wrap:wrap;gap:12px;margin:22px 0}.actions a{background:#e2ece4;border-radius:7px;padding:10px 16px;text-decoration:none}table{width:100%;border-collapse:collapse;background:#fffdf8}th,td{padding:10px 12px;border-bottom:1px solid #dfe4da;text-align:left}th{font-size:13px;color:#5b6b60}td:first-child,td:nth-child(4){width:36px}td:nth-child(2){min-width:175px}td:last-child{white-space:nowrap}.note{font-size:13px;color:#66746a}h2{font-size:21px;margin-top:25px}.scroll{overflow:auto}@media(max-width:650px){main{margin:22px auto;padding:0 14px}td:nth-child(3){min-width:230px}h1{font-size:25px}}
</style><main><p class="note">2026-10-29 · 本地待校对稿</p><h1>身体护理指南：从头到脚，按部位查找</h1><p>'''+str(report['entries'])+' 条建议 · '+str(report['sources'])+' 项去重来源 · '+str(len(report['chapters']))+''' 个内容模块。头面与五官保留既有126条，以下10篇为本轮新增。</p><div class="actions"><a href="'''+quote(master.name)+'''">打开完整合订稿</a></div><div class="scroll"><table><thead><tr><th>顺序</th><th>篇目</th><th>主要内容</th><th>条目</th><th>下载</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div><p class="note">每篇均有正文、独立摘要、来源与人群范围。核到何处、证据局限和未采用资料保留在校对包；来源与独立AI编辑核对不等于临床专业签审。本轮尚未公开发布。</p></main></html>''', encoding='utf-8')

    matrix = ['# 本轮全书需求与交付映射', '',
        '本轮将已确认的剩余日常身体护理范围逐篇完成；不等于穷尽每个内脏疾病或提供个体治疗方案。既有头面七模块126条继续保留。', '',
        '| 身体顺序 | 篇目 | 条目数 | 主要问题与原稿要求 |', '| --- | --- | --- | --- |']
    for part, receipt in zip(plan['parts'], receipts):
        matrix.append(f"| {part['order']} | {part['title']} | {receipt['entries']} | {part['description']} |")
    matrix.extend(['', '特别核对：', '',
        '- 肩颈篇：针灸、按摩、筋膜枪、办公活动与肩肘腕异常，区分短期舒适和疾病治疗。',
        '- 胸腋篇：文胸及运动支持、钢圈与聚拢营销、男女乳房变化、闷汗与腋下反复肿块。',
        '- 手足篇：皲裂、湿疹、指趾甲、趾缝发白、脚气、鞋袜与高风险足部。',
        '- 腹部篇：肚脐是否要抠、清洗与感染、鼓包与疝，以及胀气反流和排毒宣传。',
        '- 私密与如厕篇：按解剖结构清洁、内裤和经期用品、干湿厕纸、擦拭方向、冲洗器、症状分流；不以性别筛选推断妊娠或器官。',
        '- 体表篇：身体清洁、腋毛阴毛和脱毛、普通疤/肥厚疤/瘢痕疙瘩、既往与家族史风险；硅酮、注射、手术与放疗分别论证。生长因子及康复新液不借创面证据外推已有疙瘩消退。',
        '- 日常基础：睡眠、疲劳、活动、饮食、补充剂和情绪，不把心理或认知问题全部归为身体保养不足。', '',
        '每条保留稳定ID、独立摘要、六字段和年龄/男女阅读范围。没有有用成本或备注时省略其显示，不编费用，不重复无信息提醒。工程验证不证明医疗结论，尚未完成临床专业逐条签审。', ''])
    (ROOT/'docs/全书需求与交付映射.md').write_text('\n'.join(matrix), encoding='utf-8')
    shutil.copyfile(ROOT/'docs/身体护理指南全书规划与调用SOP.md', HERE/'SOP.md')
    readme = f'''身体护理指南：全书与源码校对包

先解压，再打开“交付入口.html”或“{master.name}”。无需安装软件。完整稿{report['entries']}条，{report['sources']}项去重来源，{len(report['chapters'])}个内容模块。每个单篇在根目录按身体顺序编号，HTML与对应校对ZIP配对。

合订稿支持按身体位置、症状与用品检索，保留年龄和男女阅读筛选、来源查看、收藏及离线阅读。引用原文需要联网。

“网页”含静态分享页、JSON接口与可打印正文；“项目源文件”含可编辑正文、证据记录、SOP、Prompt、审计、构建器与测试。复现方法见项目源文件/drafts/whole-body/README.md；源码中的content是原线上基线，新全书正文在drafts/whole-body，不能直接把旧content当新书发布。

本轮仅本地待用户校对，未推送GitHub或部署网站。来源核对和独立AI编辑复核不是临床专业签审。没有将引用数量、DOI或工程测试当成医学结论保证。
'''
    archive = DEST/'身体护理指南_全书与源码校对包_2026-10-29.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('先读我.txt', readme)
        z.write(master, master.name)
        z.write(index, index.name)
        proof = DEST/'从头到脚交付入口_2026-10-29.png'
        if proof.exists(): z.write(proof, '验收截图/'+proof.name)
        # Preserve relative links from the root-level entry page.
        for receipt in receipts:
            for key in ['html', 'zip']:
                p = Path(receipt[key]); z.write(p, p.name)
        for p in sorted(DIST.rglob('*')):
            if p.is_file(): z.write(p, '网页/'+p.relative_to(DIST).as_posix())
        for folder in ['content','docs','scripts','tests','web','.github','drafts/head-care-audience','drafts/whole-body']:
            for p in sorted((ROOT/folder).rglob('*')):
                if ('history' in p.relative_to(ROOT).parts or
                    ('extensions' in p.relative_to(ROOT).parts and plan.get('extension_status') != 'delivered_for_review')):
                    continue
                if p.is_file() and '__pycache__' not in p.parts and p.name != 'delivery-receipt.json':
                    z.write(p, '项目源文件/'+p.relative_to(ROOT).as_posix())
        for name in ['README.md','build.py','.gitignore']:
            z.write(ROOT/name, '项目源文件/'+name)
        # The merger needs these immutable first-edition inputs; avoid bundling
        # old compiled exports and archives while keeping the merge reproducible.
        for name in ['chapters/private.json','chapters/bodyskin.json',
            'evidence/private-sources.json','evidence/private-audit.json','evidence/private-independent-review.json',
            'evidence/bodyskin-sources.json','evidence/bodyskin-audit.json','evidence/bodyskin-independent-review.json']:
            p=HERE/'history/full-body-v1'/name
            if p.exists():z.write(p,'项目源文件/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert z.read(master.name) == master.read_bytes() == z.read('网页/downloads/guide-offline.html')
        assert z.read('项目源文件/docs/全书需求与交付映射.md') == (ROOT/'docs/全书需求与交付映射.md').read_bytes()
        count = len(z.namelist())
    receipt = dict(status='whole_book_local_review_not_published', entries=report['entries'], sources=report['sources'],
        doi_sources=report['doi_sources'], modules=len(report['chapters']), new_parts=len(receipts),
        html=dict(path=str(master), sha256=sha(master)), index=dict(path=str(index), sha256=sha(index)),
        zip=dict(path=str(archive), sha256=sha(archive), bytes=archive.stat().st_size, files=count),
        clinical_review_status='not_clinically_reviewed')
    write(HERE/'delivery-receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__': main()
