"""Compile the six-chapter review draft without changing published medical data."""
import copy
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from scripts.build import build
from scripts.content_model import (FIELD_NAMES, STABLE_REF, editorial_tags, evidence_labels,
                                   read_json, write_json, source_id, source_identity)

ORDER=['eyes','nose','oral','lips','ears','skin','hair']
VERSION='2026.10.29-head-care-audience-review-2'
DENIED=('kowloonhospital.com','haodf.com','thepaper.cn','people.com.cn','sciencenet.cn')

def fingerprints():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT/'content').rglob('*.json'))}

def bibliography(s):
    s=copy.deepcopy(s)
    citation=re.sub(r'\s+',' ',s['citation']).strip()
    m=re.search(r'\bdoi\s*:\s*(10\.\d{4,9}/\S+)',citation,re.I)
    if m:
        doi=m.group(1).rstrip('.,;，。；')
        if not re.fullmatch(r'10\.\d{4,9}/[^\s<>]+',doi):raise ValueError('Malformed DOI: '+doi)
        citation=citation[:m.start()].rstrip(' .;')+'. doi:'+doi+'.'
        s['doi']=doi;s['doi_url']='https://doi.org/'+doi
    elif '[Internet]' in citation:
        # Keep an explicitly supplied date, but make access syntax and URL uniform.
        prefix,tail=citation.split('[Internet]',1)
        date=tail.split('[cited',1)[0].strip(' .;')
        if not re.fullmatch(r'(?:19|20)\d{2}(?: (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?: \d{1,2})?)?',date):date=''
        citation=prefix.strip().rstrip('.')+' [Internet]. '+(date+'. ' if date else '')+'[cited 2026 Oct 29]. Available from: '+s['url']
    else:
        raise ValueError('Source needs journal DOI or Internet citation: '+citation)
    s['citation']=citation;s['content_checked_at']='2026-10-29'
    for key in ('support','limitations','reading_depth'):
        if not s.get(key):raise ValueError('Source lacks '+key+': '+citation)
    host=urlsplit(s['url']).hostname or ''
    if any(host==d or host.endswith('.'+d) for d in DENIED):raise ValueError('Excluded source domain: '+host)
    return s

def main():
    before=fingerprints()
    chapters=[read_json(HERE/'chapters'/f'{key}.json') for key in ORDER]
    source_lists=[read_json(HERE/'evidence'/name) for name in
                  ('eyes-sources.json','ent-sources.json','oral-lips-sources.json','skin-sources.json',
                   'eyes-vision-sources.json','hair-care-sources.json','hair-medical-sources.json','skin-expansion-sources.json',
                   'ears-audience-sources.json','dental-age-sources.json','child-vision-sources.json')]
    ledger={};aliases={};collisions=[]
    for records in source_lists:
        if isinstance(records,dict):records=records['sources']
        for raw in records:
            s=bibliography(raw);identity=source_identity(s);sid=source_id(identity)
            if raw['id'] in aliases and aliases[raw['id']]!=sid:raise ValueError('Ambiguous alias: '+raw['id'])
            aliases[raw['id']]=sid;aliases[sid]=sid;s['id']=sid
            if sid in ledger:
                prior=ledger[sid]
                for key in ('support','limitations','reading_depth'):
                    if s[key] not in prior[key]:prior[key]+='；'+s[key]
                if s['citation']!=prior['citation']:
                    collisions.append({'id':sid,'selected':prior['citation'],'alternate':s['citation']})
            else:ledger[sid]=s
    def refs(text):
        def replace(m):
            if m.group(1) not in aliases:raise ValueError('Unknown source token '+m.group(1))
            return '[@'+aliases[m.group(1)]+']'
        return re.sub(r'\[@([^\]]+)\]',replace,str(text))
    all_ids=set();seen=[];chapter_counts={};empty_cost=0
    for index,ch in enumerate(chapters,1):
        ch['order']=index;ch['intro']=refs(ch['intro'])
        for u in ch['units']:u['intro']=refs(u['intro'])
        byid={e['id']:e for e in ch['entries']}
        memberships={eid:u['id'] for u in ch['units'] for eid in u['entry_ids']}
        listed=[eid for u in ch['units'] for eid in u['entry_ids']]
        if set(listed)!=set(byid) or len(listed)!=len(byid):raise ValueError('Unit membership mismatch: '+ch['id'])
        for ordinal,eid in enumerate([x for u in ch['units'] for x in u['entry_ids']],1):
            e=byid[eid]
            if eid in all_ids:raise ValueError('Duplicate entry '+eid)
            all_ids.add(eid);e['ordinal']=ordinal;e['chapter_id']=ch['id'];e['unit_id']=memberships[eid]
            e['fields']={key:refs(e['fields'].get(key,'')) for key in FIELD_NAMES.values()}
            if not e['fields']['cost']:empty_cost+=1
            if not e.get('summary'):raise ValueError('Missing edited summary: '+eid)
            e['source_ids']=list(dict.fromkeys(STABLE_REF.findall('\n'.join(e['fields'].values()))))
            e['evidence_labels']=evidence_labels(e['fields']['evidence'])
            e['tags']=editorial_tags(e['title'],e['fields'])
            e['clinical_review_status']='not_clinically_reviewed';e['content_checked_at']='2026-10-29'
            for sid in e['source_ids']:
                if sid not in seen:seen.append(sid)
        ch['entries']=sorted(byid.values(),key=lambda e:e['ordinal'])
        chapter_counts[ch['id']]=len(ch['entries'])
    for ch in chapters:
        for value in [ch['intro']]+[u['intro'] for u in ch['units']]+[v for e in ch['entries'] for v in e['fields'].values()]:
            targets=re.findall(r'\]\(#/entry/([a-z]+-\d{3})\)',value)
            if set(targets)-all_ids:raise ValueError('Unknown cross-chapter links: '+str(set(targets)-all_ids))
    sources=[]
    for n,sid in enumerate(seen,1):
        s=ledger[sid];s['number']=n;sources.append(s)
    compiled=HERE/'compiled'
    for ch in chapters:write_json(compiled/'chapters'/f"{ch['id']}.json",ch)
    write_json(compiled/'sources.json',sources)

    target=ROOT/'.draft-preview/head-care-audience'
    target.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/'web',target/'web',dirs_exist_ok=True)
    app_path=target/'web/app.js';app=app_path.read_text(encoding='utf-8')
    replacements={
      '五官与头部护理 · 第一篇':'五官与头皮头发 · 待校对工作稿',
      "'从头开始，',node('br'),node('em',{},'学会照顾自己。')":"'从五官开始，',node('br'),node('em',{},'学会照顾自己。')",
      '没人系统教过的身体护理，在这里慢慢弄明白。从每天的小习惯，到值得花的钱，每条建议都带着理由、来源和适用条件。':'从看不清、眼干、鼻塞到牙龈出血、长斑、头屑和掉发，先找到遇到的困扰，再看具体做法、产品选择和依据。',
      '从五官与头部开始':'眼、鼻、唇、口腔、耳、面部皮肤与头皮头发',
      "['01','首篇内容','继续扩展到全身']":"['MVP','五官试点','校对确认后再扩展全身']",
      "['眼睛干涩','美瞳','牙线','电动牙刷','防晒','发膜','掏耳朵']":"['验光','摘镜手术','鼻塞','口腔溃疡','长斑','头屑','掉发','发膜']",
      "'五官与头部'),node('small',{},'研究修订 · 66条')":"'五官与头皮头发'),node('small',{},'待校对 · '+entries.length+'条')",
      '身体护理指南 · 五官与头部':'身体护理指南 · 五官与头皮头发',
      '研究修订版 · 尚未完成临床医生逐条审阅':'五官与头皮头发待校对工作稿 · 尚未完成临床专业审阅',
      "'body-care-guide:bookmarks:v1'":"'body-care-guide:head-care:bookmarks:v1'"
    }
    for old,new in replacements.items():
        if old not in app:raise ValueError('Reader wording changed; review: '+old[:40])
        app=app.replace(old,new)
    app=app.replace("hair:'头发'","hair:'头皮与头发'")
    app=app.replace("lips:'嘴唇'","lips:'嘴唇与口腔黏膜'").replace("oral:'口腔'","oral:'牙齿与牙周'")
    app=app.replace("lips:'减少干裂和刺激，再选润唇用品。'", "lips:'照顾干裂、溃疡、口干与舌面。'")
    app=app.replace("oral:'牙齿、牙龈和舌面，一起照顾好。'", "oral:'从换牙、牙周，到正畸与缺牙修复。'")
    app_path.write_text(app,encoding='utf-8')
    index_path=target/'web/index.html';index=index_path.read_text(encoding='utf-8')
    index=index.replace('五官与头部 · 研究修订版','五官与头皮头发 · 待校对工作稿').replace('五官与头部研究修订版','五官与头皮头发待校对工作稿').replace('内容核对 2026.10.28','案头核对 2026.10.29')
    index_path.write_text(index,encoding='utf-8')
    registry=read_json(ROOT/'content/id-registry.json')
    registry['entries']={k:v for k,v in registry['entries'].items() if v['id'] in all_ids}
    registered={v['id'] for v in registry['entries'].values()}
    for ch in chapters:
        for e in ch['entries']:
            if e['id'] not in registered:registry['entries']['review:'+e['id']]={'id':e['id'],'import_title':e['title']}
    registry['units']={u['id']:{'id':u['id'],'import_title':u['title']} for ch in chapters for u in ch['units']}
    registry['sources']={source_identity(s):{'id':s['id'],'identity':source_identity(s),'legacy_number':s['number']} for s in sources}
    registry['edition']=VERSION
    book={
      'schema_version':'1.0.0','content_version':VERSION,'title':'身体护理指南 五官与头皮头发待校对稿','language':'zh-CN',
      'content_checked_at':'2026-10-29','clinical_review_status':'not_clinically_reviewed','chapter_ids':ORDER,
      'front_matter':'# 五官与头皮头发阅读导览\n\n这份指南面向过去缺少护理常识的年轻人。眼睛、鼻子、嘴唇、口腔、耳朵、面部皮肤与头皮头发，从常见困扰、日常习惯到产品和美容选择，分别回答先做什么、为什么、何时需要换方案。\n\n可以从部位读，也可以搜索症状、用品或生活场景。列表用一段摘要帮你选读，具体做法、比较表与参考依据在点开后的正文。遇到突然的视力或听力变化、呼吸吞咽困难等，先按相应急症条目处理。\n\n护理的目标可以是健康、舒服、好看或方便。每种目标分别看证据；没有可靠依据的价格不写，没有信息量的成本栏不显示。你不需要把所有建议变成每天的任务。\n\n这是交给用户校对的工作稿，完成了案头资料与编辑复核，尚未由临床专业人员逐条签审。眼睛新增视力与摘镜讨论，头皮头发覆盖清洁、护发造型、掉发和生发选择。身体毛发、瘢痕及其他部位仍在全书规划中，本稿不自动替换公开网站。',
      'back_matter':'# 证据与引用说明\n\n正文采用Vancouver数字顺序编号，同一来源重复使用同号。期刊按作者、题名、期刊缩写、正式年卷期页或文章号、doi:10...记录；机构网页标访问日期，没有DOI就不补造。来源详情另列支持范围、局限和实际读取深度。\n\nA/B/C是本项目自定分级，不是GRADE：A表示较可靠的直接临床效果证据，B表示有限或间接人体资料，C表示共识、机制和护理安全实践。等级针对具体判断；C级急症分流也需要立即行动，权威机构名称不自动将建议升级为A。\n\n药品和器械的国内标签、处方属性与个体适用性不能从国外资料自动推出。具体产品的研究也不替全部同名成分或品牌背书。价格与临床证据分开，不使用历史收费表或虚构金额补满段落。\n\n完整研究流程与后续维护要求见随稿SOP、历史需求覆盖矩阵及来源审计。自动测试核对结构、引用和阅读功能，不代表临床验证。',
      'tags_note':'标签用于检索，不是诊断或个体风险评估。',
      'review_note':'待用户校对；案头与编辑复核，尚未临床专业签审。'}
    config={'title':'身体护理指南 五官与头皮头发待校对稿','repository_url':'','site_url':'','planned_parts':[{'id':'whole-body','title':'全身其他篇章，用户确认五官稿后再扩展','status':'planned'}]}
    book['audience_schema_version']='1.0.0'
    book['front_matter']+='\n\n本轮新增耳廓耳后与耳饰护理、换牙和分龄正畸、地包天与缺牙修复，并把口腔分成牙齿与牙周、嘴唇与口腔黏膜两条路线。读者可用右上角“年龄与男女”打开筛选，输入年龄或选年龄段。通用内容继续显示；急症入口在人群筛选中保留。原成人条目未经专门核对的儿童和老年应用会明确说明；筛选不是诊断、处方或治疗资格判断。'
    for name,value in [('book',book),('config',config),('sources',sources),('id-registry',registry)]:write_json(target/'content'/f'{name}.json',value)
    for ch in chapters:write_json(target/'content/chapters'/f"{ch['id']}.json",ch)
    manifest=build(root=target)
    if fingerprints()!=before:raise ValueError('Published medical content unexpectedly changed')
    shutil.copyfile(target/'dist/downloads/guide.md',HERE/'五官与头皮头发正文与参考文献.md')
    report={'status':'built_locally_not_published','content_version':VERSION,'chapters':chapter_counts,
            'entries':len(all_ids),'sources':len(sources),'doi_sources':sum(bool(s.get('doi')) for s in sources),
            'omitted_cost_sections':empty_cost,'canonical_content_unchanged':True,'canonical_fingerprints':before,
            'source_collisions_review':collisions,'clinical_review_status':'not_clinically_reviewed',
            'output':str(target/'dist')}
    write_json(HERE/'build-report.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('canonical_fingerprints','source_collisions_review')},ensure_ascii=False))

if __name__=='__main__':main()
