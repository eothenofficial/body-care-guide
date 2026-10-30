"""Add researched sleep scenarios without replacing any existing stable entry."""
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
TARGET=ROOT/'.draft-preview/sleep-followup-20261030'
sys.path.insert(0,str(ROOT))
from scripts.build import build
from scripts.content_model import (read_json,write_json,source_identity,source_id,STABLE_REF,
    FIELD_NAMES,evidence_labels,editorial_tags,validate_content)


def previous():
    spec=importlib.util.spec_from_file_location('sleep_previous',HERE.parent/'lifestyle-20261030/build_release.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.make_data()


def verify_reviews(directory=HERE):
    expected={name+'-'+kind+'.json' for name in ['exercise','meals','screen','recovery'] for kind in ['entries','sources']}
    checked={}
    for filename,key in [('exercise-independent-review.json','input_sha256'),
                         ('meals-screen-independent-review.json','input_sha256'),
                         ('recovery-independent-review.json','reviewed_file_sha256')]:
        review=read_json(directory/filename)
        if review.get('blocking_unresolved') or review.get('remaining_literal_patches') or review.get('remaining_editorial_requests'):
            raise ValueError('Unresolved independent review: '+filename)
        for name,digest in review[key].items():
            if name not in expected or hashlib.sha256((directory/name).read_bytes()).hexdigest()!=digest:
                raise ValueError('Independent review input changed: '+name)
            checked[name]=digest
    if set(checked)!=expected:raise ValueError('Incomplete independent review coverage')
    return checked


def make_data():
    verify_reviews()
    book,chapters,sources,registry=previous()
    old_ids={e['id'] for c in chapters for e in c['entries']}
    current={e['id']:copy.deepcopy(e) for c in chapters for e in c['entries']}
    additions=[];raw_sources=[]
    for name in ['exercise','meals','screen','recovery']:
        additions+=read_json(HERE/(name+'-entries.json'))
        raw_sources+=read_json(HERE/(name+'-sources.json'))
    new_ids={e['id'] for e in additions}
    if len(new_ids)!=len(additions) or old_ids&new_ids:raise ValueError('New sleep IDs collide')
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
            for k in ['support','limitations','reading_depth','funding_disclosure','funding_note']:
                value=s.get(k,'').strip();prior=lookup[sid].get(k,'').strip()
                if value and value not in prior:
                    lookup[sid][k]=value if prior in value else prior+'；'+value
            merges.append(dict(alias=raw['id'],id=sid,reason='同DOI或规范URL，合并实际核读用途，保留永久来源身份。'))
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
    sleep=next(c for c in chapters if c['id']=='sleep')
    sleep.update(summary='从晚间运动、夜宵和手机，到缺觉次日安排、失眠与助眠用品',
        subtitle='从晚间运动、夜宵和手机，到缺觉次日安排、失眠与助眠用品',
        intro='先认出困倦驾驶、异常呼吸和夜里总想动腿等需要处理的线索，再安排光照、午睡、晚间运动、进食与睡前收尾。反复睡不着时，分清具体自护、完整治疗与助眠产品；偶尔少睡一晚，也有次日休息、咖啡因和训练的选择。调整运动、进食和屏幕使用时，既看离睡觉多久，也看强度、分量和个人反应，不必给自己定一张按钟点执行的禁令表。')
    units=[
        ('sleep-u1','先识别困倦与睡眠中的异常','先保通勤与操作安全，再核睡眠呼吸和夜间腿部不适等线索。',['sleep-001','basics-002','sleep-016']),
        ('sleep-u2','安排白天与睡前习惯，不给自己堆统一禁令','从睡眠机会与光照，到咖啡、午睡、运动、晚餐和手机，按具体场景调整。',['basics-001','sleep-008','sleep-005','sleep-006','sleep-009','sleep-010','sleep-011']),
        ('sleep-u3','睡不着时，分清自护、治疗与助眠产品','先处理当晚越躺越烦，再了解失眠治疗、褪黑素和时差，不靠叠药或不断加量。',['sleep-014','sleep-002','sleep-003','sleep-004','sleep-015']),
        ('sleep-u4','需要助眠声音，再比较耳机、耳塞与声机','明确放松还是隔音，兼顾声音暴露、佩戴压力与定时停播。',['sleep-007']),
        ('sleep-u5','前晚没睡好，次日先保安全再恢复','把通勤、咖啡、短小睡和训练放在一张当天的安排里，不把提神当补足睡眠。',['sleep-012','sleep-013'])]
    sleep['units']=[];sleep['entries']=[]
    for order,(uid,title,intro,eids) in enumerate(units,1):
        sleep['units'].append(dict(id=uid,title=title,intro=intro,order=order,entry_ids=eids))
        for eid in eids:
            e=copy.deepcopy(current[eid]);e.update(chapter_id='sleep',unit_id=uid,ordinal=len(sleep['entries'])+1)
            e.setdefault('legacy_chapter_id','sleep');sleep['entries'].append(e)
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
    book.update(content_version='2026.10.30-3',content_checked_at='2026-10-30',editorial_checked_at='2026-10-30')
    registry=dict(schema_version='1.0.0',edition=book['content_version'],
        entries={e['id']:dict(id=e['id'],import_title=e['title']) for c in chapters for e in c['entries']},
        units={u['id']:dict(id=u['id'],import_title=u['title']) for c in chapters for u in c['units']},
        sources={source_identity(s):dict(id=s['id'],identity=source_identity(s),legacy_number=s['number']) for s in sources})
    validate_content(book,chapters,sources,registry)
    write_json(HERE/'source-merge-audit.json',merges)
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
