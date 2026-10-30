"""Validate and package the current reader and maintenance sources, without publishing."""
import hashlib
import html
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from scripts.content_model import load_content, read_json, write_json, STABLE_REF

TARGET=ROOT/'.draft-preview/release-20261030'
DIST=TARGET/'dist'
DEST=ROOT.parent/'身体护理指南_2026-10-30'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def verify():
    book,chapters,sources,registry=load_content(TARGET)
    data=read_json(DIST/'downloads/guide.json')
    offline=(DIST/'downloads/guide-offline.html').read_text(encoding='utf-8')
    embedded=json.loads(re.search(r'window\.__GUIDE_DATA__=(.*?);\n',offline,re.S).group(1))
    assert embedded==data
    for name in ['entries','sources','chapters']:
        assert read_json(DIST/f'api/v1/{name}.json')[name]==data[name]
    assert read_json(DIST/'api/v1/manifest.json')==data['manifest']
    entries=data['entries'];ids={e['id'] for e in entries};used=set()
    baseline={e['id'] for p in (ROOT/'drafts/whole-body/compiled/master/chapters').glob('*.json') for e in read_json(p)['entries']}
    report=read_json(HERE/'build-report.json')
    assert not report.get('editorial_preview',False),'A preview cannot be delivered as completed editorial work'
    aliases=data['manifest'].get('entry_aliases',{})
    assert baseline<=ids|set(aliases) and len(ids)==len(entries)==report['entries']
    assert all(old not in ids and target in ids for old,target in aliases.items())
    for value in [data['manifest'].get('book',{}).get('front_matter',''),data['manifest'].get('book',{}).get('back_matter','')]:used.update(STABLE_REF.findall(value))
    for c in chapters:
        used.update(STABLE_REF.findall(c['intro']))
        for u in c['units']:used.update(STABLE_REF.findall(u['intro']))
    markdown=(DIST/'downloads/guide.md').read_text(encoding='utf-8')
    assert not STABLE_REF.search(markdown)
    public=[]
    for e in entries:
        assert report.get('summary_min',100)<=len(e['summary'])<=report.get('summary_max',180)
        assert not re.search(r'[\r\n|]|\[@|\]\(',e['summary'])
        assert e['clinical_review_status']=='not_clinically_reviewed'
        for value in e['fields'].values():
            used.update(STABLE_REF.findall(value))
            assert set(re.findall(r'\]\(#/entry/([a-z][a-z0-9-]+)\)',value))<=ids
        share=(DIST/'read'/e['id']/'index.html').read_text(encoding='utf-8')
        assert e['audience']['scope_note'] in share
        assert bool(re.search(r'<h2\b[^>]*>成本</h2>',share))==bool(e['fields']['cost'])
        public.append(share)
    assert used=={s['id'] for s in sources}
    assert [s['number'] for s in sources]==list(range(1,len(sources)+1))
    for s in sources:
        assert all(s.get(k) for k in ['citation','url','support','limitations','reading_depth'])
        if s.get('doi'):
            assert s['doi_url']=='https://doi.org/'+s['doi']
            assert 'doi:'+s['doi'] in s['citation']
    symbols=set(re.findall(r'<symbol id="i-([^\"]+)"',(DIST/'index.html').read_text(encoding='utf-8')))
    assert len(chapters)==len(report['chapters'])
    for c in chapters:assert c['icon'] in symbols and c['icon']!='book'
    forbidden=re.compile('本地校对稿|校对稿|交付稿|初稿研究|出片|待用户确认|按用户要求|按本款图示|如图所示|见上图|点击下方视频')
    for value in [offline,markdown,*public]:assert not forbidden.search(value)
    expected=read_json(HERE/'build-report.json')['canonical_fingerprints']
    actual={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'content').rglob('*.json'))}
    assert expected==actual
    result=dict(status='passed_export_and_reader_contracts',entries=len(entries),sources=len(sources),
        modules=len(chapters),source_graph_resolves=True,all_ids_preserved=True,
        offline_json_api_equal=True,public_copy_scan_passed=True,icons_defined=True,merged_aliases_preserved=len(aliases),
        canonical_baseline_unchanged=True,clinical_review_status='not_clinically_reviewed')
    write_json(HERE/'validation.json',result)
    return data


def main():
    data=verify()
    tests=read_json(HERE/'test-results.json')
    if tests['returncode']!=0 or tests.get('skipped',0):raise ValueError('Required tests did not all pass')
    if tests['reader_sha256']!=sha(DIST/'downloads/guide-offline.html'):
        raise ValueError('The built reader changed after the recorded test run')
    DEST.mkdir(parents=True,exist_ok=True)
    public_title=data['manifest']['title']
    reader=DEST/globals().get('READER_FILENAME','身体护理指南.html')
    shutil.copyfile(DIST/'downloads/guide-offline.html',reader)
    # A consistent named entry for future reading; retain old dated deliverables.
    shutil.copyfile(reader,ROOT.parent/'身体护理指南.html')
    if reader.name!='身体护理指南.html':shutil.copyfile(reader,ROOT.parent/reader.name)
    sop=ROOT/'docs/身体护理指南全书规划与调用SOP.md'
    shutil.copyfile(sop,ROOT/'drafts/whole-body/SOP.md')
    docrows=[]
    for name in ['身体护理指南全书规划与调用SOP.md','继续写作Prompt.txt','身体护理项目验收清单.md']:
        shutil.copyfile(ROOT/'docs'/name,DEST/name)
        docrows.append('<a href="'+quote(name)+'">'+html.escape(name)+'</a>')
    # The portable SOP keeps its reference links beside the portable file.
    p=DEST/sop.name
    p.write_text(p.read_text(encoding='utf-8').replace('../drafts/head-care-audience/references/写作风格校准SOP_用户提供原稿.md','写作风格校准SOP_用户提供原稿.md'),encoding='utf-8')
    shutil.copyfile(ROOT/'drafts/head-care-audience/references/写作风格校准SOP_用户提供原稿.md',DEST/'写作风格校准SOP_用户提供原稿.md')
    parts=[]
    for group in data['manifest']['body_layout']:
        links=[]
        for ch in group['chapters']:
            count=sum(e['chapter_id']==ch['id'] for e in data['entries'])
            links.append('<a href="'+quote(reader.name)+'#/chapter/'+ch['id']+'">'+html.escape(ch['title'])+' <small>'+str(count)+'条</small></a>')
        parts.append('<section><h2>'+html.escape(group['title'])+'</h2><div class="links">'+''.join(links)+'</div></section>')
    index=DEST/'打开指南.html'
    index.write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>身体护理指南 · 阅读入口</title><style>
body{margin:0;background:#f6f5ef;color:#273832;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1000px;margin:32px auto;padding:0 24px}h1{margin-bottom:8px}h2{font-size:17px;margin:0;min-width:150px}p{color:#64736b}.start{display:inline-block;background:#176b5b;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;margin:10px 0 25px}section{display:flex;gap:22px;padding:18px 0;border-top:1px solid #dfe4da}.links{display:flex;flex-wrap:wrap;gap:10px}.links a{padding:5px 10px;border:1px solid #d8dfd4;border-radius:6px;text-decoration:none;color:#176b5b;background:#fffefa}.links small{color:#79817a;margin-left:5px}details{margin-top:28px}details a{display:block;color:#176b5b}footer{font-size:13px;color:#79817a;margin-top:25px}@media(max-width:600px){section{display:block}h2{margin-bottom:10px}}</style><main><p>2026-10-30 · 身体护理指南</p><h1>从头到脚，按需要查找</h1><p>'''+str(len(data['entries']))+'条建议 · '+str(len(data['chapters']))+'个内容专题 · '+str(len(data['sources']))+'''项可追溯来源</p><a class="start" href="'''+quote(reader.name)+'''">打开完整指南 →</a>'''+''.join(parts)+'''<details><summary>给作者与维护者：SOP、调用提示与验收清单</summary>'''+''.join(docrows)+'''</details><footer>健康科普与产品选择参考。尚未经过临床医生逐条审核，不能替代个人检查、诊断和处方。</footer></main></html>''',encoding='utf-8')
    index.write_text(index.read_text(encoding='utf-8').replace('<title>身体护理指南 · 阅读入口</title>','<title>'+html.escape(public_title)+' · 阅读入口</title>').replace('2026-10-30 · 身体护理指南</p>','2026-10-30 · '+html.escape(public_title)+'</p>'),encoding='utf-8')
    # Updated anatomical directory for maintainers; public UI uses the same data.
    directory=['# 身体位置目录','', '内容版本 '+data['manifest']['content_version']+'：'+str(len(data['entries']))+'条建议、'+str(len(data['sources']))+'项来源、'+str(len(data['chapters']))+'个专题。按区域及生活基础分组，每条只有一个主要归属，交叉入口使用稳定链接。','',
        '| 区域 | 具体部位 | 条目 | 页面ID | 图标 |','| --- | --- | --- | --- | --- |']
    for ch in data['chapters']:
        count=sum(e['chapter_id']==ch['id'] for e in data['entries'])
        directory.append(f"| {ch['body_group']} | {ch['title']} | {count} | {ch['id']} | {ch['icon']} |")
    directory+=['','旧模块为编辑输入及兼容入口，目录以本版manifest为准。条目ID与来源身份保留，新增条目不复用旧ID。','',
        '本轮按正式阅读文案组织本地文件，未自动同步远端。医学与编辑核对日期分开，未把工程或AI审校称为临床签审。','']
    (ROOT/'docs/全书身体位置目录.md').write_text('\n'.join(directory),encoding='utf-8')
    archive=DEST/globals().get('ARCHIVE_FILENAME','身体护理指南_完整项目.zip')
    readme='''身体护理指南

打开“身体护理指南.html”即可阅读；“打开指南.html”提供按身体位置的目录。无需安装软件。
“网站”是同一数据生成的网页、静态分享页、完整导出与JSON接口。
“项目源文件”含可编辑正文、来源账本、补丁、SOP、Prompt、审校记录、构建器和测试。
当前复现入口见项目源文件/README.md与本版drafts/whole-body目录内的README。

本轮文件已在本地修改、构建与校验，未推送GitHub或部署。content目录为历史公开基线；新完整版本必须使用本版README指定的drafts构建入口，不能混用旧基线。
本书是健康科普，未经过临床医生逐条审核。审校记录不属于读者正文，工程测试不证明临床结论。
'''
    readme=readme.replace('身体护理指南.html',reader.name).replace('身体护理指南\n',public_title+'\n')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('先读我.txt',readme)
        z.write(reader,reader.name);z.write(index,index.name)
        for p in list(DEST.glob('*.md'))+list(DEST.glob('*.txt')):z.write(p,p.name)
        for p in sorted(DIST.rglob('*')):
            if p.is_file():z.write(p,'网站/'+p.relative_to(DIST).as_posix())
        for folder in ['content','docs','scripts','tests','web','.github','drafts/head-care-audience','drafts/whole-body']:
            for p in sorted((ROOT/folder).rglob('*')):
                if not p.is_file() or '__pycache__' in p.parts or 'history' in p.parts or 'research-medications' in p.parts or p.name=='delivery-receipt.json':continue
                z.write(p,'项目源文件/'+p.relative_to(ROOT).as_posix())
        for name in ['README.md','build.py','.gitignore']:z.write(ROOT/name,'项目源文件/'+name)
        for p in DEST.glob('*.png'):z.write(p,'界面截图/'+p.name)
        # Retain the small frozen merge inputs needed by the older extension tool.
        for name in ['chapters/private.json','chapters/bodyskin.json',
            'evidence/private-sources.json','evidence/private-audit.json','evidence/private-independent-review.json',
            'evidence/bodyskin-sources.json','evidence/bodyskin-audit.json','evidence/bodyskin-independent-review.json']:
            p=ROOT/'drafts/whole-body/history/full-body-v1'/name
            if p.exists():z.write(p,'项目源文件/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert z.read(reader.name)==reader.read_bytes()==z.read('网站/downloads/guide-offline.html')
        assert z.read('项目源文件/docs/身体护理指南全书规划与调用SOP.md')==sop.read_bytes()
        assert json.loads(z.read('网站/api/v1/entries.json'))['entries']==data['entries']
        assert not any('/research-medications/' in name for name in z.namelist())
        files=len(z.namelist())
    receipt=dict(version=data['manifest']['content_version'],entries=len(data['entries']),sources=len(data['sources']),
        modules=len(data['chapters']),tests=tests,html=dict(path=str(reader),sha256=sha(reader)),
        zip=dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size,files=files),
        index=dict(path=str(index),sha256=sha(index)),published=False,clinical_review_status='not_clinically_reviewed')
    write_json(HERE/'delivery-receipt.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':main()
