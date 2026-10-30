"""Merge reviewed additions into the book while preserving all original IDs."""
import copy
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = BASE.parents[1]
HISTORY = BASE/'history/full-body-v1'


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path, obj): path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def array(value, key): return value if isinstance(value, list) else value[key]


def main():
    groups = ['period','contraception','fertility','reader','body-gaps']
    provenance = {}
    for group in groups:
        review = HERE/(group+'-independent-review.json')
        if not review.exists() or read(review).get('blocking_unresolved'):
            raise ValueError('Independent review not resolved: '+group)
        provenance[group] = {p.name:sha(p) for p in sorted(HERE.glob(group+'-*.json'))}
    private = read(HISTORY/'chapters/private.json')
    old = {e['id']:copy.deepcopy(e) for e in private['entries']}
    additions = {g:array(read(HERE/(g+'-entries.json')),'entries') for g in groups}
    mapping = {'period-001':'private-009', 'period-010':'private-002'}
    counter = 19
    for group in ['period','reader','contraception','fertility']:
        for entry in additions[group]:
            if entry['id'] not in mapping:
                counter += 1; mapping[entry['id']] = 'private-'+str(counter).zfill(3)
    def rewrite(value):
        if isinstance(value,str):
            return re.sub(r'#\/entry\/([a-z][a-z0-9]*(?:-[a-z0-9]+)*-\d{3})',
                lambda m:'#/entry/'+mapping.get(m.group(1),m.group(1)), value)
        if isinstance(value,list):return [rewrite(v) for v in value]
        if isinstance(value,dict):return {k:rewrite(v) for k,v in value.items()}
        return value
    for group in ['period','reader','contraception','fertility']:
        for original in additions[group]:
            if original['id']=='period-010': continue
            e = rewrite(copy.deepcopy(original)); e['id']=mapping[original['id']];e['chapter_id']='private'
            old[e['id']] = e
    for eid, edit in read(HERE/'reader-edits.json').items():
        for key,value in edit.items():
            if key=='plain': old[eid]['fields']['plain']=value
            else: old[eid][key]=value
    # One urgent abdominal/pregnancy entry; retain its previous broad warning.
    ectopic = next(e for e in additions['period'] if e['id']=='period-010')
    old['private-002']['fields']['plain'] += '\n\n'+ectopic['fields']['plain']
    old['private-002']['fields']['sources'] += '\n宫外孕专门分流。'+ectopic['fields']['sources']
    old['private-002']['audience']['safety_pin']=True
    old['private-002']['fields']['plain'] = (
        '**骨盆或下腹痛严重、越来越重，或伴晕厥、呼吸困难、大量阴道出血，立即急诊。** '
        '骨盆是下腹内容纳膀胱、直肠和部分生殖器官的区域；不同问题可有相似疼痛，不能仅凭位置自诊。[@PRIVATE-S02]\n\n'
        + ectopic['fields']['plain'] + '\n\n'
        '没有前述严重信号，但疼痛伴发热、异常分泌物或尿痛，也应及时检查。记录开始时间、哪侧明显、末次月经、出血与用药，说明妊娠可能；检查据此选择，而不是一律用消炎药。[@PRIVATE-S02]')
    old['private-009']['fields']['plain'] = old['private-009']['fields']['plain'].replace(
        '突然发热并明显不适、呕吐腹泻、皮疹或头晕',
        '突然发热，或出现呕吐腹泻、皮疹、明显头晕等全身异常')
    # Overview stays short; the new entries carry the actual operating steps.
    old['private-008']['title']='先按经量、舒适度和换洗条件选经期用品，再看各自操作方法'
    old['private-008']['summary']='卫生巾和经期内裤在体外吸收，棉条在阴道内吸收，月经杯和月经碟则收集经血，放置位置与取法不同。没有哪种必须人人用，先看经量、舒适度和是否方便及时更换清洁。想换用品时，先读对应操作和风险，不因香味、清凉或医用材料宣传，就把它当成预防感染的工具。'
    old['private-008']['fields']['plain']='**先看自己能否安全、舒服地使用和维护，再决定换不换用品。** 卫生巾、经期内裤在体外吸收；棉条在阴道内吸收；杯碟收集经血，放置位置不同。不能因为一种产品更流行，就当所有人都该升级。[@PRIVATE-S12][@PERIOD-S03][@PERIOD-S04]\n\n按实际场景往下读：[卫生巾与护垫](#/entry/'+mapping['period-002']+')、[棉条](#/entry/'+mapping['period-003']+')、[杯碟区别与放取](#/entry/'+mapping['period-004']+')、[排空与清洁](#/entry/'+mapping['period-005']+')。有宫内器械时先看[合用风险](#/entry/'+mapping['period-006']+')；出现突然全身不适则看[紧急处理](#/entry/private-009)。\n\n香味、草本、清凉感和抗菌包装不等于预防阴道炎的临床证据；反复闷痒或痛要找原因，不靠更强香味遮盖。[@PRIVATE-S11]'
    # The sources for device definitions in the period draft are selected below
    # from actual reference tokens, rather than guessed by source numbering.
    definition_refs = next(e for e in additions['period'] if e['id']=='period-004')['source_ids']
    old['private-008']['fields']['plain'] = old['private-008']['fields']['plain'].replace('[@PERIOD-S03][@PERIOD-S04]', ''.join('[@'+s+']' for s in definition_refs))
    old['private-008']['fields']['benefit']='按自己能维护的场景选用品，随后直接找到对应操作与异常处理。'
    old['private-008']['fields']['sources']='FDA/CDC经期指导及杯碟使用来源。[@PRIVATE-S12][@PRIVATE-S11]'+''.join('[@'+s+']' for s in definition_refs)
    # Keep the test operation entry focused, cross-link the complete urgent branch.
    test = old[mapping['fertility-009']]
    test['fields']['plain'] += '\n\n出现上述危险症状，直接按[下腹痛与可能妊娠的急症入口](#/entry/private-002)处理，不等待复测。'

    units=[]
    def unit(identifier,title,intro,ids):
        units.append(dict(id=identifier,title=title,intro=intro,order=len(units)+1,
            entry_ids=[mapping.get(e,e) for e in ids]))
    unit('private-u1','先认急症，别让清洗、试药或验孕拖延处理',
        '睾丸痛、严重下腹症状、置入用品后的全身异常、持续勃起与近期暴露，都有单独的紧急入口。',
        ['private-001','private-002','private-009','reader-009','private-019'])
    unit('private-u2','把日常清洁做好，减少过度清洗、刺激和闷湿',
        '外阴、阴道、包皮和阴囊不采用同一套清洁动作；衣物先看合身干爽。',
        ['private-003','private-004','private-005','private-006','private-007'])
    unit('private-u3','先选合适的经期用品，再学会放取、更换和清洁',
        '从体外巾垫到体内棉条、杯碟，各有维护要求；最长佩戴和清洁方式按实际型号。',
        ['private-008','period-002','period-003','period-004','period-005','period-006'])
    unit('private-u7','看经血、周期与疼痛的变化，别把异常都当体寒',
        '颜色不是健康成绩；经量、出现时点、疼痛和妊娠可能一起影响行动。',
        ['period-007','period-008','period-009'])
    unit('private-u4','分清正常白带与异常，再决定检查和治疗',
        '先认正常变化，阴道炎、外阴皮病和伴侣管理各按真实病因处理。',
        ['private-010','private-011','reader-001','private-012'])
    unit('private-u8','男性分泌物、皮肤疙瘩、硬块和血精分别查因',
        '先看异常在皮肤、尿道还是睾丸，不以一个“上火”或“前列腺问题”解释全部。',
        ['private-013','reader-002','reader-003','reader-004'])
    unit('private-u5','尿路不适和漏尿分开，盆底训练先找对方向',
        '感染、刺激和控尿问题需要不同处理；盆底不总是越紧越好。',
        ['private-014','private-017'])
    unit('private-u6','让性接触更安全舒服，持续困扰有正规处理',
        '把感染预防、干涩疼痛、勃起射精和自我照护分开，不靠紧致、壮阳和延时营销包治。',
        ['private-015','reader-008','private-016','reader-005','reader-006','reader-007','private-018'])
    contra = read(HERE/'contraception-entries.json')
    for i,u in enumerate(contra['proposed_units'],9):
        unit('private-u'+str(i),u['title'],u['intro'],u['entry_ids'])
    fertility = read(HERE/'fertility-audit.json')
    for i,u in enumerate(fertility['unit_suggestions'],13):
        unit('private-u'+str(i),u['title'],u['intro'],u['entry_ids'])
    order=[eid for u in units for eid in u['entry_ids']]
    if set(order)!=set(old) or len(order)!=len(old):raise ValueError('Entries lost or repeated in new units')
    private['units']=units;private['entries']=[old[eid] for eid in order]
    private['subtitle']='从清洁、经期与男女常见困扰，到避孕、备孕和需要检查的时点'
    private['summary']='先找到身体部位和生活场景，再看怎么清洁、怎样选经期用品、哪些变化该检查，以及如何避孕或准备妊娠。'
    private['intro']='私密护理不只是一瓶洗液。先把日常清洁、经期用品和正常变化弄清楚；遇到疼痛、分泌物或出血，再按具体情况查因。没有不适但想避免妊娠，可以直接读避孕；准备生育则从双方的健康准备开始。\n\n不必从头背到尾。用品条目写放取、更换和维护，疾病条目写下一步怎样做，所有判断保留来源与适用条件。遇到紧急症状先看第一单元，不因年龄、性别或验孕结果自行排除风险。'
    sources=read(HISTORY/'evidence/private-sources.json')
    for group in ['period','reader','contraception','fertility']:
        sources+=array(read(HERE/(group+'-sources.json')),'sources')
    for i,e in enumerate(private['entries'],1):
        e['ordinal']=i;e['unit_id']=next(u['id'] for u in units if e['id'] in u['entry_ids'])
        e['source_ids']=list(dict.fromkeys(re.findall(r'\[@([^\]]+)\]', '\n'.join(e['fields'].values()))))
        if not 110<=len(e['summary'])<=170:raise ValueError(('summary',e['id'],len(e['summary'])))
    write(BASE/'chapters/private.json',private)
    write(BASE/'evidence/private-sources.json',sources)

    skin=read(HISTORY/'chapters/bodyskin.json'); skin_map={}
    for i,e in enumerate(additions['body-gaps'],23):
        e=copy.deepcopy(e);skin_map[e['id']]='bodyskin-'+str(i).zfill(3);e['id']=skin_map[e['id']];
        e['chapter_id']='bodyskin';e['ordinal']=i;skin['entries'].append(e)
    existing={u['id']:u for u in skin['units']}
    # Common rashes follow the existing body skin symptoms; bites follow wounds.
    rash=next(u for u in skin['units'] if 'bodyskin-007' in u['entry_ids'])
    wound=next(u for u in skin['units'] if 'bodyskin-012' in u['entry_ids'])
    rash['entry_ids'] += ['bodyskin-023','bodyskin-024'];wound['entry_ids'].append('bodyskin-025')
    for e in skin['entries']: e['unit_id']=next(u['id'] for u in skin['units'] if e['id'] in u['entry_ids'])
    skin_sources=read(HISTORY/'evidence/bodyskin-sources.json')+read(HERE/'body-gaps-sources.json')
    write(BASE/'chapters/bodyskin.json',skin);write(BASE/'evidence/bodyskin-sources.json',skin_sources)

    for key,groups_used in [('private',['period','contraception','fertility','reader']),('bodyskin',['body-gaps'])]:
        old_audit=read(HISTORY/'evidence'/(key+'-audit.json'))
        audit=dict(status='merged_reviewed_extension_not_clinically_reviewed',clinical_review_status='not_clinically_reviewed',
            content_checked_at='2026-10-29',previous_version_audit=old_audit,
            entries=len(private['entries'] if key=='private' else skin['entries']),
            extensions={g:read(HERE/(g+'-audit.json')) for g in groups_used},
            integration='Existing stable IDs retained; period-001 expands private-009; period-010 joins private-002; other new IDs explicit in integration report.')
        write(BASE/'evidence'/(key+'-audit.json'),audit)
        review=dict(status='independent_reviews_merged_not_clinical_review',blocking_unresolved=[],clinical_review_status='not_clinically_reviewed',
            baseline=read(HISTORY/'evidence'/(key+'-independent-review.json')),
            extension_reviews={g:read(HERE/(g+'-independent-review.json')) for g in groups_used},
            integration_note='已分别核新增临床分支；随后校验合并后引用、单元、人群与实际输出，不能冒充重新逐篇临床签审。')
        if key=='private':
            review['root_integration_edits']=['保留private002严重下腹症状，将宫外孕细节合并并删重复分流语句','private009按独立编辑建议将首句写成发热或其他明显全身异常，不要求合并发热','private008简短总览链接具体用品操作；既有ID与已核临床条件保留']
        write(BASE/'evidence'/(key+'-independent-review.json'),review)
    plan=read(BASE/'plan.json')
    for part in plan['parts']:
        if part['id']=='private':
            part['delivery_suffix']='经期与生育健康增补版'
            part['description']='清洁与男女症状、经期用品实际操作、分泌物与经血、避孕与紧急补救、双方备孕。'
        if part['id']=='bodyskin':part['delivery_suffix']='查漏增补版'
    plan['extension_status']='reviewed_ready_to_build';write(BASE/'plan.json',plan)
    write(HERE/'integration-report.json',dict(status='merged_ready_for_build_checks',inputs=provenance,private_entries=len(private['entries']),
        bodyskin_entries=len(skin['entries']),temporary_to_stable_ids={**mapping,**skin_map},
        preserved_version=str(HISTORY),clinical_review_status='not_clinically_reviewed'))
    print(json.dumps(dict(private=len(private['entries']),bodyskin=len(skin['entries'])),ensure_ascii=False))


if __name__=='__main__': main()
