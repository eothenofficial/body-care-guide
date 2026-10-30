"""Full-book editorial revision, explicit same-audience merges and stable aliases."""
import argparse,copy,hashlib,importlib.util,json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TARGET=ROOT/'.draft-preview/editorial-readability-20261030'
sys.path.insert(0,str(ROOT))
from scripts.build import build
from scripts.content_model import read_json,write_json,source_identity,source_id,STABLE_REF,FIELD_NAMES,evidence_labels,editorial_tags,validate_content

def previous():
    spec=importlib.util.spec_from_file_location('editorial_previous',HERE.parent/'nutrition-followup-20261030/build_release.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.make_data()

def verify_reviews(directory=HERE):
    checked={}
    for prefix in ['head','intimate','body','home']:
        review=read_json(directory/(prefix+'-independent-review.json'))
        if review.get('blocking_unresolved') or review.get('pending_patches'):raise ValueError('Independent editorial review unresolved: '+prefix)
        expected={prefix+'-'+suffix+'.json' for suffix in (['content','sources'] if prefix=='home' else ['rewrites','merges'])}
        final=review.get('final_input_sha256',review.get('input_sha256',{}))
        if not expected<=set(final):raise ValueError('Incomplete independent review hash binding: '+prefix)
        for filename in expected:
            if hashlib.sha256((directory/filename).read_bytes()).hexdigest()!=final[filename]:raise ValueError('Reviewed editorial input changed: '+filename)
            checked[filename]=final[filename]
    return checked

def make_data(preview=False):
    book,chapters,sources,_=previous()
    baseline={e['id']:copy.deepcopy(e) for c in chapters for e in c['entries']}
    entries=copy.deepcopy(baseline);merges=[];audits=[]
    for prefix in ['head','intimate','body']:
        expected={e['id'] for e in read_json(HERE/(prefix+'-input.json'))['entries']}
        if preview:continue
        rewrites=read_json(HERE/(prefix+'-rewrites.json'))
        if isinstance(rewrites,dict):rewrites=rewrites['entries']
        if len(rewrites)!=len(expected) or {e['id'] for e in rewrites}!=expected:raise ValueError('Incomplete full reading: '+prefix)
        for raw in rewrites:
            eid=raw['id'];old=baseline[eid]
            if not 60<=len(raw['summary'])<=140 or re.search(r'[\r\n|`]|\[@|\]\(',raw['summary']):raise ValueError('Invalid summary '+eid)
            fields={key:raw['fields'][key] for key in FIELD_NAMES.values()}
            old_refs=set(STABLE_REF.findall('\n'.join(old['fields'].values())))
            refs=list(dict.fromkeys(STABLE_REF.findall('\n'.join(fields.values()))))
            if set(refs)!=old_refs:raise ValueError('Evidence identity changed '+eid+': '+str(old_refs^set(refs)))
            if raw['title']==old['title'] and raw['summary']==old['summary'] and fields['plain']==old['fields']['plain']:raise ValueError('Entry not rewritten '+eid)
            entries[eid].update(title=raw['title'],summary=raw['summary'],fields=fields,source_ids=refs,evidence_labels=evidence_labels(fields['evidence']),tags=editorial_tags(raw['title'],fields),editorial_checked_at='2026-10-30')
            audits.append(dict(id=eid,read_and_rewritten=True,source_ids_preserved=True,original_title=old['title'],title=raw['title'],old_plain_chars=len(old['fields']['plain']),new_plain_chars=len(fields['plain'])))
        path=HERE/(prefix+'-merges.json')
        if not path.exists():raise ValueError('Merge review is not complete: '+prefix)
        values=read_json(path);values=values if isinstance(values,list) else values['merges']
        if len(values)!=3:raise ValueError('Unexpected merge scope: '+prefix)
        merges+=values
    aliases={};merge_audit=[]
    for merged in merges:
        target=merged['target'];retired=merged['retired'];members=[target,*retired]
        if not retired or any(i not in entries for i in members):raise ValueError('Invalid merge '+str(members))
        audience=entries[target]['audience']
        for eid in members:
            if any(entries[eid]['audience'][key]!=audience[key] for key in ['age_groups','sexes']):raise ValueError('Merge changes readership '+eid)
        required=set(sid for eid in members for sid in baseline[eid]['source_ids'])
        fields={key:merged['fields'][key] for key in FIELD_NAMES.values()}
        refs=list(dict.fromkeys(STABLE_REF.findall('\n'.join(fields.values()))))
        if set(refs)!=required:raise ValueError('Merged evidence missing '+target+': '+str(required^set(refs)))
        if not 60<=len(merged['summary'])<=140:raise ValueError('Invalid merged summary '+target)
        entries[target].update(title=merged['title'],summary=merged['summary'],fields=fields,source_ids=refs,evidence_labels=evidence_labels(fields['evidence']),tags=editorial_tags(merged['title'],fields),search_aliases=[baseline[eid]['title'] for eid in members],merged_from=retired)
        entries[target]['audience']['scope_note']='；'.join(dict.fromkeys(baseline[eid]['audience']['scope_note'] for eid in members))
        entries[target]['audience']['safety_pin']=any(baseline[eid]['audience'].get('safety_pin',False) for eid in members)
        for eid in retired:aliases[eid]=target;del entries[eid]
        merge_audit.append(dict(target=target,retired=retired,reason=merged['reason'],same_age_and_sex=True,all_original_sources_retained=True))
    def replace_links(text):
        return re.sub(r'\]\(#/entry/([a-z][a-z0-9-]+)\)',lambda m:'](#/entry/'+aliases.get(m[1],m[1])+')',text)
    for chapter in chapters:
        kept=[]
        for unit in chapter['units']:
            unit['entry_ids']=[eid for eid in unit['entry_ids'] if eid not in aliases]
            for eid in unit['entry_ids']:
                entry=entries[eid];entry.update(chapter_id=chapter['id'],unit_id=unit['id'],ordinal=len(kept)+1)
                entry['fields']={k:replace_links(v) for k,v in entry['fields'].items()};kept.append(entry)
        chapter['entries']=kept
        if not kept:raise ValueError('Empty chapter')
        # Keep old unit routes; an emptied unit offers the chapter's remaining entries.
    source_lookup={s['id']:s for s in sources};home_alias={}
    fatigue=next(s for s in sources if 'symptoms/tiredness-and-fatigue' in s['url'])
    home_alias['HOME-FATIGUE']=fatigue['id']
    for raw in read_json(HERE/'home-sources.json'):
        sid=source_id(source_identity(raw));home_alias[raw['id']]=sid
        if sid not in source_lookup:source_lookup[sid]={**raw,'id':sid}
    def home_refs(value):
        if isinstance(value,str):return re.sub(r'\[@(HOME-[A-Z]+)\]',lambda m:'[@'+home_alias[m[1]]+']',value)
        if isinstance(value,list):return [home_refs(v) for v in value]
        if isinstance(value,dict):return {k:home_refs(v) for k,v in value.items()}
        return value
    home=home_refs(read_json(HERE/'home-content.json'))
    book.update(content_version='2026.10.30-5',editorial_checked_at='2026-10-30',entry_aliases=aliases,home_content=home)
    book['front_matter']='# 身体护理指南\n\n'+home['audience']+'\n\n'+home['headline']+home['headline_end']+'\n\n'+home['lead']+'\n\n## '+home['why_title']+'\n\n'+home['why']+'\n\n## 读完能做什么\n\n'+'\n\n'.join('**'+d['title']+'** '+d['text'] for d in home['decisions'])+'\n\n## 怎么使用\n\n'+home['reader_guide']
    used=[]
    def remember(value):
        for sid in STABLE_REF.findall(value):
            if sid not in used:used.append(sid)
    remember(book['front_matter']);remember(book['back_matter'])
    for chapter in chapters:
        remember(chapter['intro'])
        for unit in chapter['units']:remember(unit['intro'])
        for entry in chapter['entries']:
            for value in entry['fields'].values():remember(value)
    sources=[source_lookup[sid] for sid in used]
    for number,source in enumerate(sources,1):source['number']=number
    registry=dict(schema_version='1.0.0',edition=book['content_version'],entries={e['id']:dict(id=e['id'],import_title=e['title']) for e in entries.values()},units={u['id']:dict(id=u['id'],import_title=u['title']) for c in chapters for u in c['units']},sources={source_identity(s):dict(id=s['id'],identity=source_identity(s),legacy_number=s['number']) for s in sources})
    validate_content(book,chapters,sources,registry)
    if set(entries)|set(aliases)!=set(baseline):raise ValueError('Lost published identity')
    write_json(HERE/('preview-report.json' if preview else 'editorial-coverage.json'),dict(preview=preview,reviewed=len(audits),original_entries=len(baseline),active_entries=len(entries),aliases=aliases,merges=merge_audit,entries=audits,original_plain_chars=sum(len(e['fields']['plain']) for e in baseline.values()),revised_plain_chars=sum(len(e['fields']['plain']) for e in entries.values()),clinical_review_status='not_clinically_reviewed'))
    return book,chapters,sources,registry

def main(preview=False):
    before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'content').rglob('*.json'))}
    book,chapters,sources,registry=make_data(preview)
    for name,value in [('book',book),('sources',sources),('id-registry',registry),('config',dict(title=book['title'],repository_url=read_json(ROOT/'content/config.json')['repository_url'],site_url='',planned_parts=[]))]:write_json(TARGET/'content'/(name+'.json'),value)
    for chapter in chapters:write_json(TARGET/'content/chapters'/(chapter['id']+'.json'),chapter)
    shutil.copytree(ROOT/'web',TARGET/'web',dirs_exist_ok=True)
    js=TARGET/'web/app.js';js.write_text(js.read_text(encoding='utf-8').replace("'body-care-guide:bookmarks:v1'","'body-care-guide:whole-body:bookmarks:v1'"),encoding='utf-8')
    build(root=TARGET)
    after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'content').rglob('*.json'))}
    if before!=after:raise ValueError('Public baseline changed')
    try:verify_reviews();review_complete=True
    except (FileNotFoundError,ValueError):review_complete=False
    report=dict(content_version=book['content_version'],editorial_preview=preview,independent_editorial_review_complete=review_complete,summary_min=100 if preview else 60,summary_max=180 if preview else 140,entries=sum(len(c['entries']) for c in chapters),merged_entries=len(book['entry_aliases']),sources=len(sources),doi_sources=sum(bool(s.get('doi')) for s in sources),chapters={c['id']:len(c['entries']) for c in chapters},canonical_fingerprints=before,clinical_review_status='not_clinically_reviewed',output=str(TARGET/'dist'))
    write_json(HERE/'build-report.json',report);print(json.dumps({k:v for k,v in report.items() if k!='canonical_fingerprints'},ensure_ascii=False))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview-original',action='store_true');args=parser.parse_args();main(args.preview_original)
