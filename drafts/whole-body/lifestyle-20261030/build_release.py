"""Extend the reviewed full book with daily physical-care topics; keep stable IDs."""
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
TARGET=ROOT/'.draft-preview/lifestyle-20261030'
sys.path.insert(0,str(ROOT))
from scripts.build import build
from scripts.content_model import (read_json,write_json,source_identity,source_id,STABLE_REF,
    FIELD_NAMES,evidence_labels,editorial_tags,validate_content)


def previous():
    spec=importlib.util.spec_from_file_location('reader_previous',HERE.parent/'revision-20261030/build_release.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.make_data()


def records(name):
    value=read_json(HERE/(name+'.json'))
    return value['entries'] if isinstance(value,dict) and 'entries'in value else value['sources'] if isinstance(value,dict) and 'sources'in value else value


def make_data():
    book,oldchapters,sources,registry=previous()
    original_ids={e['id'] for c in oldchapters for e in c['entries']}
    existing={e['id']:copy.deepcopy(e) for c in oldchapters for e in c['entries']}
    allnew=[];new_sources=[]
    for name in ['sleep','nutrition','activity','energy']:
        allnew+=records(name+'-entries');new_sources+=records(name+'-sources')
    if len({e['id'] for e in allnew})!=len(allnew) or original_ids&{e['id'] for e in allnew}:raise ValueError('New IDs collide')
    lookup={s['id']:copy.deepcopy(s) for s in sources};aliases={s['id']:s['id'] for s in sources}
    source_merges=[]
    for raw in new_sources:
        s=copy.deepcopy(raw);sid=source_id(source_identity(s));aliases[s['id']]=sid;s['id']=sid
        citation=re.sub(r'\s+',' ',s['citation']).strip()
        doi=re.search(r'\bdoi\s*:\s*(10\.\d{4,9}/\S+)',citation,re.I)
        if doi:
            value=doi.group(1).rstrip('.,;，。；');s['doi']=value;s['doi_url']='https://doi.org/'+value
            citation=citation[:doi.start()].rstrip(' .;')+'. doi:'+value+'.'
        s['citation']=citation
        for k in ['support','limitations','reading_depth']:
            if not s.get(k):raise ValueError('Missing source scope: '+raw['id']+' '+k)
        if sid in lookup:
            old=lookup[sid]
            for k in ['support','limitations','reading_depth']:
                value=s[k].strip();prior=old[k].strip()
                if value and value not in prior:
                    old[k]=value if prior in value else prior+'；'+value
            for k in ['funding_disclosure','funding_note']:
                if s.get(k) and s[k] not in str(old.get(k,'')):old[k]=(str(old.get(k,''))+'；'+s[k]).strip('；')
            source_merges.append(dict(id=sid,alias=raw['id'],reason='相同DOI或规范URL，保留稳定身份，补入新增用途的实际核读范围。'))
        else:lookup[sid]=s
    def refs(text):
        def replace(m):
            sid=aliases.get(m.group(1))
            if not sid:raise ValueError('Unknown source alias: '+m.group(1))
            return '[@'+sid+']'
        return re.sub(r'\[@([^\]]+)\]',replace,str(text))
    for e in allnew:
        e['fields']={k:refs(e['fields'].get(k,'')) for k in FIELD_NAMES.values()}
        e['source_ids']=list(dict.fromkeys(STABLE_REF.findall('\n'.join(e['fields'].values()))))
        e['evidence_labels']=evidence_labels(e['fields']['evidence']);e['tags']=editorial_tags(e['title'],e['fields'])
        e['clinical_review_status']='not_clinically_reviewed';e['content_checked_at']='2026-10-30';e['editorial_checked_at']='2026-10-30'
        if not 100<=len(e['summary'])<=180 or re.search(r'[\r\n|]|\[@|\]\(',e['summary']):raise ValueError('Invalid independent summary: '+e['id'])
        existing[e['id']]=e
    # Keep the old safety boundary, but do not expand this book into psychotherapy.
    e=existing['basics-008']
    e['title']='情绪或注意力持续影响生活就求助，别只靠养生或体检指标解释'
    e['fields']['plain']='**持续低落、焦虑、失去兴趣或注意力困难，也值得认真评估；不必等体检异常才求助。** 睡眠、疾病、药物和生活处境都可能参与，不能只归因于身体差或意志不够。严重或已影响日常生活即可联系全科、心理或精神科，不把两周等提醒当必须先忍满的等待期。[@src-c8a3ee731e7d]\n\n若有伤害自己的念头、已受伤或无法确保安全，立即联系当地急诊或急救服务，并请可信任者陪同，不等待作息、日晒、聊天或补剂起效。这里保留的是求助入口，不能凭文章或某个生理指标自诊。[@src-c8a3ee731e7d]'
    e['fields']['benefit']='在身体护理之外保留必要的求助路径，避免用补剂或单一指标拖延评估。'
    e['editorial_checked_at']='2026-10-30'
    # Driving safety comes from the directly read traffic-safety source, not the caffeine page alone.
    e=existing['energy-001'];drive=aliases['LIFE-SLP-S01']
    e['fields']['plain']=e['fields']['plain'].replace('困倦时需要睡眠与查原因，不能靠咖啡因证明可以安全驾车。','困倦时需要睡眠与查原因，不能靠咖啡因证明可以安全驾车，见[困倦驾驶](#/entry/sleep-001)。[@'+drive+']')
    e=existing['activity-003']
    e['fields']['plain']=e['fields']['plain'].replace('普通酸痛与危险信号的区分见本篇的练后恢复条目。','普通酸痛与危险信号的区分见[练后酸痛与恢复](#/entry/activity-005)。')
    chapters=[copy.deepcopy(c) for c in oldchapters if c['id']!='basics']
    def ids(prefix,*values):return [f'{prefix}-{i:03d}' for i in values]
    def unit(identifier,title,intro,entry_ids):return dict(id=identifier,title=title,intro=intro,entry_ids=entry_ids)
    def chapter(identifier,title,icon,subtitle,intro,units):
        c=dict(id=identifier,title=title,icon=icon,body_group='生活基础',summary=subtitle,subtitle=subtitle,intro=intro,units=units,entries=[])
        for index,u in enumerate(units,1):
            u['order']=index
            for eid in u['entry_ids']:
                e=copy.deepcopy(existing[eid]);e.update(chapter_id=identifier,unit_id=u['id'],ordinal=len(c['entries'])+1)
                e.setdefault('legacy_chapter_id','basics' if eid.startswith('basics-') else identifier)
                e['source_ids']=list(dict.fromkeys(STABLE_REF.findall('\n'.join(e['fields'].values()))))
                e['evidence_labels']=evidence_labels(e['fields']['evidence']);e['tags']=editorial_tags(e['title'],e['fields'])
                c['entries'].append(e)
        chapters.append(c)
    chapter('sleep','睡眠与作息','sleep','先分困倦、失眠与生物钟，再选褪黑素、耳机和助眠用品',
        '白天撑不住、晚上睡不着和跨时区后的错位，需要不同处理。先看驾驶风险与打鼾憋醒，再看规律作息、白天见光和午睡；需要治疗或用品时，区分完整CBT-I、不同褪黑素制剂和听觉产品。日光用于节律与生活安排，不代替情绪疾病的评估。',[
        unit('sleep-u1','先分困倦安全与异常呼吸','困倦时先停止高风险任务；睡够仍困或夜间异常呼吸需要查原因。',['sleep-001','basics-002']),
        unit('sleep-u2','把睡眠机会、光照和午睡安排好','从起床和主睡眠入手，再调整咖啡酒精、小睡与白天见光。',['basics-001']+ids('sleep',5,6,8)),
        unit('sleep-u3','反复失眠与时差分别选择治疗和褪黑素','先认清适应证、剂型与时机，不把标签剂量当成人人的处方。',ids('sleep',2,3,4)),
        unit('sleep-u4','需要助眠声音，再比较耳机、耳塞与声机','先明确放松还是隔音，音量、佩戴压力和定时都要考虑。',['sleep-007'])])
    chapter('nutrition','饮食与体重','nutrition','比较生酮、禁食、代餐与增肌补剂，把减脂和掉水重分开',
        '先处理节食时的明显不适，再把餐食、饮水与长期目标安排好。低碳、禁食和极低能量方案不是越严格越好；蛋白粉、肌酸、代餐、无糖饮料和减重药分别解决不同问题。比较要看体重、脂肪、力量或疾病结局，不能只看秤上数字。',[
        unit('nutrition-u1','节食出现不适，先分普通饥饿与危险信号','低血糖与酮症酸中毒的处置不能互换，也不能按生酮宣传排除急症。',['nutrition-001']),
        unit('nutrition-u2','先安排餐食、饮水和可持续目标','普通食物与日常支持仍是基础，不给每个人同一热量和饮水数字。',['basics-004','basics-005','basics-010']),
        unit('nutrition-u3','按营养、风险和可持续性比较饮食方案','低碳、限时进食与医疗低能量方案的适用条件不同。',ids('nutrition',2,3,4)),
        unit('nutrition-u4','先核缺口，再选蛋白和训练补充品','补剂先核目标、重复摄入与用药，再看具体成分有没有相应人体收益。',['basics-007']+ids('nutrition',5,6,7)),
        unit('nutrition-u5','把便利、药物治疗与营销产品分开','代餐不等于蛋白奶昔，减重药不等于研究针剂，无糖也不是无限额。',ids('nutrition',8,9,10,11))])
    chapter('activity','运动与恢复','activity','先识别运动急症，再安排训练、恢复、补水与设备选择',
        '运动要能持续，也要知道什么时候先停下来。先看胸痛、晕厥、热病与异常肌肉损伤，再从当前能耐受的活动开始，比较热身、力量进阶和酸痛恢复。运动饮料与手表各有用途，不能把数据或短时燃脂比例当成长远效果保证。',[
        unit('activity-u1','胸痛、意识变化或异常肌痛，先停止训练并求助','热病与严重肌肉损伤不能等症状凑齐，设备读数也不能排除危险。',ids('activity',1,2,3)),
        unit('activity-u2','从能持续的活动，逐步练到合适负荷','周量目标、热身冷身、力量进阶和恢复分别安排，不追求每次练到痛。',['basics-006']+ids('activity',4,9,5)),
        unit('activity-u3','补水、记录与进食时机按训练需要选择','运动饮料是特定场景的选择，手表是估计工具，空腹不是必需门槛。',ids('activity',6,7,8))])
    chapter('energy','疲劳与日常风险','wellbeing','疲劳先查因，提神和烟酒按具体风险判断',
        '累不一定是缺某种营养，也不都能靠多练解决。持续影响生活先评估；轻活动后反复迟发加重，要记录活动耐受。咖啡因与烟酒分别看总量、症状和戒断风险。情绪与注意力只保留必要的求助入口，不扩成心理治疗或人生建议。',[
        unit('energy-u1','持续疲劳与活动后加重，先找原因','记录持续时间、活动与症状关系；突发危险表现仍按对应急症处理。',['basics-003','energy-002']),
        unit('energy-u2','提神与烟酒不靠标签判断安全','查总咖啡因、个人反应与药物，也为依赖者保留正规安全减停的路径。',['energy-001','basics-009']),
        unit('energy-u3','持续情绪或注意力异常，保留求助入口','一般自护不能替代严重或持续功能受影响时的评估。',['basics-008'])])
    actual=[e['id'] for c in chapters for e in c['entries']]
    if len(actual)!=len(set(actual)) or set(actual)!=original_ids|{e['id'] for e in allnew}:raise ValueError('Lost or duplicated entries')
    used=[]
    def note_refs(text):
        for sid in STABLE_REF.findall(text):
            if sid not in used:used.append(sid)
    for order,c in enumerate(chapters,1):
        c['order']=order;note_refs(c['intro'])
        for u in c['units']:
            note_refs(u['intro'])
            for eid in u['entry_ids']:
                for value in next(e for e in c['entries'] if e['id']==eid)['fields'].values():note_refs(value)
    sources=[lookup[sid] for sid in used]
    for number,s in enumerate(sources,1):s['number']=number
    book.update(content_version='2026.10.30-2',content_checked_at='2026-10-30',editorial_checked_at='2026-10-30',chapter_ids=[c['id'] for c in chapters])
    book['front_matter']+='\n\n生活基础按睡眠、饮食、运动与疲劳风险选读。日光与作息可讨论身体节律，持续情绪或注意力异常另有求助入口；不把一般聊天或心情技巧写成疾病治疗。各条资料核读日期与限制保留在正文和来源中。'
    book['chapter_aliases']['basics']=dict(title='生活基础',chapter_ids=['sleep','nutrition','activity','energy'])
    book['body_layout']=[group for group in book['body_layout'] if group['title']!='日常基础']
    book['body_layout'].append(dict(title='生活基础',description='睡眠、饮食体重、运动恢复与疲劳风险。',chapters=[dict(id=c['id'],title=c['title']) for c in chapters[-4:]]))
    book['search_examples']=['褪黑素','生酮','断食','蛋白粉','运动饮料','月经碟','脚气','牙线']
    registry=dict(schema_version='1.0.0',edition=book['content_version'],
        entries={e['id']:dict(id=e['id'],import_title=e['title']) for c in chapters for e in c['entries']},
        units={u['id']:dict(id=u['id'],import_title=u['title']) for c in chapters for u in c['units']},
        sources={source_identity(s):dict(id=s['id'],identity=source_identity(s),legacy_number=s['number']) for s in sources})
    validate_content(book,chapters,sources,registry)
    write_json(HERE/'source-merge-audit.json',source_merges)
    return book,chapters,sources,registry


def main():
    before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'content').rglob('*.json'))}
    book,chapters,sources,registry=make_data()
    for name,value in [('book',book),('sources',sources),('id-registry',registry),('config',dict(title=book['title'],repository_url=read_json(ROOT/'content/config.json').get('repository_url',''),site_url='',planned_parts=[]))]:write_json(TARGET/'content'/(name+'.json'),value)
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
