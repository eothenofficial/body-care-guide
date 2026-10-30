"""Extend nutrition with traceable evidence; preserve all previous stable IDs."""
import copy
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TARGET=ROOT/'.draft-preview/nutrition-followup-20261030'
sys.path.insert(0,str(ROOT))
from scripts.build import build
from scripts.content_model import (read_json,write_json,source_identity,source_id,STABLE_REF,
    FIELD_NAMES,evidence_labels,editorial_tags,validate_content)


def previous():
    spec=importlib.util.spec_from_file_location('nutrition_previous',HERE.parent/'sleep-followup-20261030/build_release.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.make_data()


def verify_reviews(directory=HERE):
    expected={name+'-'+kind+'.json' for name in ['foundation','glycemia','medications','management'] for kind in ['entries','sources']}
    audit_names={name+'-audit.json' for name in ['foundation','glycemia','medications','management']}
    checked={}
    for filename,key in [(name+'-independent-review.json','input_sha256') for name in ['foundation','glycemia','medications','management']]:
        review=read_json(directory/filename)
        if review.get('blocking_unresolved') or review.get('remaining_literal_patches') or review.get('remaining_editorial_requests'):
            raise ValueError('Unresolved independent review: '+filename)
        # Reviews may keep the original author input and the final reviewed output separately.
        for name,digest in review.get('output_sha256',review[key]).items():
            if name not in expected|audit_names or hashlib.sha256((directory/name).read_bytes()).hexdigest()!=digest:
                raise ValueError('Independent review input changed: '+name)
            if name in expected:checked[name]=digest
    if set(checked)!=expected:raise ValueError('Incomplete independent review coverage')
    return checked


def make_data():
    verify_reviews()
    book,chapters,sources,registry=previous()
    old_ids={e['id'] for c in chapters for e in c['entries']}
    current={e['id']:copy.deepcopy(e) for c in chapters for e in c['entries']}
    additions=[];raw_sources=[]
    for name in ['foundation','glycemia','medications','management']:
        additions+=read_json(HERE/(name+'-entries.json'))
        raw_sources+=read_json(HERE/(name+'-sources.json'))
    addition_ids={e['id'] for e in additions}
    revised_ids={'nutrition-009'}
    new_ids=addition_ids-old_ids
    if len(addition_ids)!=len(additions) or addition_ids&old_ids!=revised_ids:raise ValueError('Unexpected nutrition ID replacement')
    if new_ids!={f'nutrition-{i:03d}' for i in range(12,24)}:raise ValueError('Missing new nutrition entries')
    lookup={s['id']:copy.deepcopy(s) for s in sources};aliases={s['id']:s['id'] for s in sources};merges=[]
    for raw in raw_sources:
        s=copy.deepcopy(raw);sid=source_id(source_identity(s));aliases[s['id']]=sid;s['id']=sid
        s['citation']=re.sub(r'\s+',' ',s['citation']).strip()
        doi=re.search(r'\bdoi\s*:\s*(10\.\d{4,9}/\S+)',s['citation'],re.I)
        if doi:
            value=doi.group(1).rstrip('.,;，。；');s['doi']=value;s['doi_url']='https://doi.org/'+value
            s['citation']=s['citation'][:doi.start()].rstrip(' .;')+'. doi:'+value+'.'
        if any(not s.get(k) for k in ['support','limitations','reading_depth']):raise ValueError('Missing source scope '+raw['id'])
        if sid in lookup:
            old_citation=lookup[sid]['citation']
            if s.get('doi') and s['citation']!=old_citation:
                # The new formal metadata has its own independent evidence review.
                lookup[sid]['citation']=s['citation']
            for k in ['support','limitations','reading_depth','funding_disclosure','funding_note']:
                value=s.get(k,'').strip();prior=lookup[sid].get(k,'').strip()
                if value and value not in prior:
                    lookup[sid][k]=value if prior in value else prior+'；'+value
            merges.append(dict(alias=raw['id'],id=sid,reason='同DOI或规范URL，合并实际核读用途，保留永久来源身份。',prior_citation=old_citation,final_citation=lookup[sid]['citation']))
        else:lookup[sid]=s
    def refs(text):
        def replace(m):
            if m.group(1) not in aliases:raise ValueError('Unknown source '+m.group(1))
            return '[@'+aliases[m.group(1)]+']'
        return re.sub(r'\[@([^\]]+)\]',replace,str(text))
    for e in additions:
        e['fields']={k:refs(e['fields'].get(k,'')) for k in FIELD_NAMES.values()}
        e['source_ids']=list(dict.fromkeys(STABLE_REF.findall('\n'.join(e['fields'].values()))))
        e['evidence_labels']=evidence_labels(e['fields']['evidence']);e['tags']=editorial_tags(e['title'],e['fields'])
        e.update(clinical_review_status='not_clinically_reviewed',content_checked_at='2026-10-30',editorial_checked_at='2026-10-30')
        if not 100<=len(e['summary'])<=180 or re.search(r'[\r\n|]|\[@|\]\(',e['summary']):raise ValueError('Invalid summary '+e['id'])
        current[e['id']]=e
    nutrition=next(c for c in chapters if c['id']=='nutrition')
    nutrition.update(summary='把日常餐食、血糖检查、减脂增肌和减重药分别安排清楚',
        subtitle='把日常餐食、血糖检查、减脂增肌和减重药分别安排清楚',
        intro='想吃得更好，可以先从一日餐食、减盐和食品标签开始；担心血糖，再分清日常安排、正规筛查与监测设备。想改变体重或线条，先量腰围、评估是否需要减重，再选择能持续的饮食和力量训练。生酮、限时进食、代餐与补剂各有适用条件；减重药确有临床作用，却需要按具体制剂、适应证和身体情况选择。这里把这些问题分开讲，也保留节食不适和进食失控时的求助入口。')
    units=[
        ('nutrition-u1','节食出现不适，先分普通饥饿与危险信号','低血糖与酮症酸中毒的处置不能互换，也不能按生酮宣传排除急症。',['nutrition-001']),
        ('nutrition-u2','先安排餐食、减盐、饮水与食品选择','把吃齐、吃多少和怎样选择分开落实，低钠钾盐也要先核适用条件。',['basics-004','nutrition-013','nutrition-012','nutrition-014','basics-005']),
        ('nutrition-u6','想管好血糖，先改餐食和久坐，再做正规筛查','不追求人人零波动，不让健康设备替代诊断，也不忽略用药者低血糖。',['nutrition-015','nutrition-016']),
        ('nutrition-u7','先评估减重需要，再改善脂肪、力量与线条','把BMI、腰围、体脂秤与实际能力一起看，进食失控时先退出惩罚式减重。',['nutrition-020','basics-010','nutrition-021','nutrition-022','nutrition-023']),
        ('nutrition-u3','按营养、风险和可持续性比较饮食方案','低碳、限时进食与医疗低能量方案不同；代餐、无糖饮料也不自动带来减脂。',['nutrition-002','nutrition-003','nutrition-004','nutrition-008','nutrition-011']),
        ('nutrition-u4','先核缺口，再选蛋白和训练补充品','补剂先核目标、重复摄入与用药，再看具体成分有没有相应人体收益。',['basics-007','nutrition-005','nutrition-006','nutrition-007']),
        ('nutrition-u5','需要减重药，逐个核适应证、收益和风险','先看治疗路径，再比较具体药物；不买研究针剂，不照抄别人的加量表。',['nutrition-009','nutrition-017','nutrition-018','nutrition-019','nutrition-010'])]
    nutrition['units']=[];nutrition['entries']=[]
    for order,(uid,title,intro,eids) in enumerate(units,1):
        nutrition['units'].append(dict(id=uid,title=title,intro=intro,order=order,entry_ids=eids))
        for eid in eids:
            e=copy.deepcopy(current[eid]);e.update(chapter_id='nutrition',unit_id=uid,ordinal=len(nutrition['entries'])+1)
            e.setdefault('legacy_chapter_id','nutrition');nutrition['entries'].append(e)
    used=[]
    def note(text):
        for sid in STABLE_REF.findall(str(text)):
            if sid not in used:used.append(sid)
    for c in chapters:
        note(c['intro'])
        for u in c['units']:
            note(u['intro'])
            for eid in u['entry_ids']:
                for value in next(e for e in c['entries'] if e['id']==eid)['fields'].values():note(value)
    sources=[lookup[sid] for sid in used]
    for number,s in enumerate(sources,1):s['number']=number
    actual=[e['id'] for c in chapters for e in c['entries']]
    if set(actual)!=old_ids|new_ids or len(actual)!=len(set(actual)):raise ValueError('Lost or duplicated entry')
    book.update(content_version='2026.10.30-4',content_checked_at='2026-10-30',editorial_checked_at='2026-10-30')
    registry=dict(schema_version='1.0.0',edition=book['content_version'],
        entries={e['id']:dict(id=e['id'],import_title=e['title']) for c in chapters for e in c['entries']},
        units={u['id']:dict(id=u['id'],import_title=u['title']) for c in chapters for u in c['units']},
        sources={source_identity(s):dict(id=s['id'],identity=source_identity(s),legacy_number=s['number']) for s in sources})
    validate_content(book,chapters,sources,registry)
    write_json(HERE/'source-merge-audit.json',merges)
    write_json(HERE/'migration-audit.json',dict(previous_entries=len(old_ids),new_entries=sorted(new_ids),revised_entries=sorted(revised_ids),previous_stable_ids_preserved=True))
    return book,chapters,sources,registry


def main():
    before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'content').rglob('*.json'))}
    book,chapters,sources,registry=make_data()
    config=dict(title=book['title'],repository_url=read_json(ROOT/'content/config.json').get('repository_url',''),site_url='',planned_parts=[])
    for name,value in [('book',book),('sources',sources),('id-registry',registry),('config',config)]:write_json(TARGET/'content'/(name+'.json'),value)
    for c in chapters:write_json(TARGET/'content/chapters'/(c['id']+'.json'),c)
    shutil.copytree(ROOT/'web',TARGET/'web',dirs_exist_ok=True)
    p=TARGET/'web/app.js';p.write_text(p.read_text(encoding='utf-8').replace("'body-care-guide:bookmarks:v1'","'body-care-guide:whole-body:bookmarks:v1'"),encoding='utf-8')
    build(root=TARGET)
    after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'content').rglob('*.json'))}
    if before!=after:raise ValueError('Published baseline changed')
    report=dict(content_version=book['content_version'],entries=sum(len(c['entries']) for c in chapters),sources=len(sources),doi_sources=sum(bool(s.get('doi')) for s in sources),
        chapters={c['id']:len(c['entries']) for c in chapters},canonical_fingerprints=before,original_entry_ids_preserved=True,clinical_review_status='not_clinically_reviewed',output=str(TARGET/'dist'))
    write_json(HERE/'build-report.json',report);write_json(HERE/'directory.json',dict(chapters=[{k:v for k,v in c.items() if k!='entries'} for c in chapters],aliases=book['chapter_aliases']))
    print(json.dumps({k:v for k,v in report.items() if k!='canonical_fingerprints'},ensure_ascii=False))


if __name__=='__main__':main()
