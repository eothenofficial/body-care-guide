"""Build individually reviewed body parts and a cumulative local reader."""
import argparse
import copy
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build import build
from scripts.content_model import (FIELD_NAMES, STABLE_REF, editorial_tags, evidence_labels,
    read_json, write_json, source_id, source_identity)

DATE = '2026-10-29'
HEAD = ['hair', 'eyes', 'nose', 'ears', 'oral', 'lips', 'skin']


def fingerprints():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / 'content').rglob('*.json'))}


def normalize_source(raw):
    s = copy.deepcopy(raw)
    citation = re.sub(r'\s+', ' ', s['citation']).strip()
    doi = re.search(r'\bdoi\s*:\s*(10\.\d{4,9}/\S+)', citation, re.I)
    if doi:
        value = doi.group(1).rstrip('.,;，。；')
        if not re.fullmatch(r'10\.\d{4,9}/[^\s<>]+', value):
            raise ValueError('Malformed DOI: ' + value)
        s['doi'] = value; s['doi_url'] = 'https://doi.org/' + value
        citation = citation[:doi.start()].rstrip(' .;') + '. doi:' + value + '.'
    elif '[Internet]' in citation:
        prefix, tail = citation.split('[Internet]', 1)
        date = tail.split('[cited', 1)[0].strip(' .;')
        if not re.fullmatch(r'(?:19|20)\d{2}(?: (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?: \d{1,2})?)?', date):
            date = ''
        citation = prefix.rstrip(' .') + ' [Internet]. ' + (date + '. ' if date else '') + '[cited 2026 Oct 29]. Available from: ' + s['url']
    else:
        raise ValueError('Source lacks normalized citation: ' + citation)
    s['citation'] = citation
    for key in ('support', 'limitations', 'reading_depth'):
        if not s.get(key): raise ValueError('Source lacks ' + key + ': ' + raw['id'])
    return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--part', help='Build one standalone part, leaving the cumulative reader alone')
    args = parser.parse_args()
    plan = read_json(HERE / 'plan.json')
    known = {p['id']: p for p in plan['parts']}
    delivered = plan['delivered']
    if args.part and args.part not in known: raise ValueError('Unknown body part')
    keys = [args.part] if args.part else HEAD + [p['id'] for p in plan['parts'] if p['id'] in delivered]
    key = args.part or 'master'
    before = fingerprints()
    chapters = [read_json(HERE / ('baseline/chapters' if k in HEAD else 'chapters') / (k + '.json')) for k in keys]
    sources_raw = read_json(HERE / 'baseline/sources.json')
    for k in keys:
        if k not in HEAD:
            records = read_json(HERE / 'evidence' / (k + '-sources.json'))
            sources_raw.extend(records['sources'] if isinstance(records, dict) else records)
    ledger, aliases, collisions = {}, {}, []
    for raw in sources_raw:
        s = normalize_source(raw); identity = source_identity(s); sid = source_id(identity)
        if raw['id'] in aliases and aliases[raw['id']] != sid: raise ValueError('Ambiguous source alias')
        aliases[raw['id']] = sid; aliases[sid] = sid; s['id'] = sid
        if sid in ledger:
            for field in ('support', 'limitations', 'reading_depth'):
                if s[field] not in ledger[sid][field]: ledger[sid][field] += '；' + s[field]
            if ledger[sid]['citation'] != s['citation']:
                collisions.append(dict(id=sid, selected=ledger[sid]['citation'], alternate=s['citation']))
        else: ledger[sid] = s
    seen = []
    def refs(value):
        def replace(match):
            token = match.group(1)
            if token not in aliases: raise ValueError('Unknown source alias: ' + token)
            sid = aliases[token]
            if sid not in seen: seen.append(sid)
            return '[@' + sid + ']'
        return re.sub(r'\[@([^\]]+)\]', replace, str(value))
    ids = set(); empty_cost = 0
    for order, ch in enumerate(chapters, 1):
        ch['order'] = order; ch['intro'] = refs(ch['intro'])
        ch['summary'] = ch.get('summary') or ch['subtitle']
        memberships = {}
        for number, unit in enumerate(ch['units'], 1):
            unit['order'] = number; unit['intro'] = refs(unit['intro'])
            for eid in unit['entry_ids']:
                if eid in memberships: raise ValueError('Repeated unit membership: ' + eid)
                memberships[eid] = unit['id']
        byid = {e['id']: e for e in ch['entries']}
        if set(byid) != set(memberships) or len(byid) != len(ch['entries']): raise ValueError('Unit mismatch: ' + ch['id'])
        arranged = []
        for n, eid in enumerate(memberships, 1):
            e = byid[eid]
            if eid in ids: raise ValueError('Duplicate entry: ' + eid)
            ids.add(eid); e['chapter_id'] = ch['id']; e['unit_id'] = memberships[eid]; e['ordinal'] = n
            e['fields'] = {field: refs(e['fields'].get(field, '')) for field in FIELD_NAMES.values()}
            if not e.get('audience'): raise ValueError('Missing reviewed audience: ' + eid)
            if not 100 <= len(e.get('summary', '')) <= 180 or re.search(r'[\r\n|]|\[@|\]\(', e['summary']): raise ValueError('Invalid edited summary: ' + eid)
            e['source_ids'] = list(dict.fromkeys(STABLE_REF.findall('\n'.join(e['fields'].values()))))
            if not e['source_ids']: raise ValueError('No references: ' + eid)
            e['evidence_labels'] = evidence_labels(e['fields']['evidence']); e['tags'] = editorial_tags(e['title'], e['fields'])
            e['clinical_review_status'] = 'not_clinically_reviewed'; e['content_checked_at'] = DATE
            empty_cost += not bool(e['fields']['cost']); arranged.append(e)
        ch['entries'] = arranged
    for ch in chapters:
        texts = [ch['intro']] + [u['intro'] for u in ch['units']] + [value for e in ch['entries'] for value in e['fields'].values()]
        for value in texts:
            missing = set(re.findall(r'\]\(#/entry/([a-z][a-z0-9]*(?:-[a-z0-9]+)*-\d{3})\)', value)) - ids
            if missing: raise ValueError('Standalone part has missing cross-links: ' + str(missing))
    sources = []
    for number, sid in enumerate(seen, 1):
        s = ledger[sid]; s['number'] = number; sources.append(s)
    version = '2026.10.29-whole-body-' + key + '-' + str(len(ids))
    title = known[key]['title'] if args.part else '身体护理指南'
    target = ROOT / '.draft-preview/whole-body' / key
    shutil.copytree(ROOT / 'web', target / 'web', dirs_exist_ok=True)
    app_path = target / 'web/app.js'; app = app_path.read_text(encoding='utf-8')
    # Reader wording is now driven by the book manifest. Keep only the
    # edition-specific bookmark namespace; no string patching of public labels.
    app = app.replace("'body-care-guide:bookmarks:v1'", "'body-care-guide:whole-body" + (':part:'+key if args.part else '') + ":bookmarks:v1'")
    app_path.write_text(app, encoding='utf-8')
    index_path = target / 'web/index.html'; index = index_path.read_text(encoding='utf-8')
    index = index.replace('五官与头部 · 研究修订版', title).replace('五官与头部研究修订版', title)
    index_path.write_text(index, encoding='utf-8')
    layout = [] if args.part else [dict(title='头面与五官篇', description='头皮头发、眼鼻耳、牙齿牙周、嘴唇黏膜与面部皮肤。', chapters=[dict(id=k, title=next(c['title'] for c in chapters if c['id'] == k)) for k in HEAD])]
    if not args.part:
        layout += [dict(title=p['title'], description=p['description'], chapters=[dict(id=p['id'], title=p['title'])] if p['id'] in delivered else []) for p in plan['parts']]
    book = dict(schema_version='1.0.0', audience_schema_version='1.0.0', content_version=version, title=title, language='zh-CN',
        content_checked_at=DATE, clinical_review_status='not_clinically_reviewed', chapter_ids=keys, body_layout=layout,
        front_matter='# 阅读导览\n\n' + ('本文件为独立篇，先按症状和生活场景找条目，再看具体动作、产品选择和依据。' if args.part else '主目录顺着身体从上到下排列。症状、用品、年龄和男女筛选是辅助入口；全身体表护理与生活基础放在末尾。按身体位置选择具体部位，跨部位主题单列。') + '\n\n标题和独立摘要帮助选读，全文、比较表和引用在详情。没有可靠依据的费用省略，不为保养增加无意义任务。人群筛选反映已核对的阅读侧重，不判断药物或手术资格；急症条目也遵守年龄和男女筛选。\n\n本指南用于一般健康科普，尚未经过临床医生逐条审核，不能替代个人诊疗。',
        back_matter='# 证据与引用\n\n使用Vancouver顺序编号，稳定来源ID和条目ID不随篇目排序改变。期刊核作者、正式年卷期页或文章号与DOI；官网记录真实日期、访问日、支持范围、局限和实际读取深度。\n\nA/B/C为项目自定分级，并非GRADE。机构指导不自动等于疗效强证据，C级急症仍需及时处理；没有找到证据也不等于已经证明无效。来源与AI编辑核对不等于临床签审，工程测试只验证数据和阅读功能。',
        tags_note='标签用于查找，不能用于自我诊断。', review_note='健康科普；尚未经过临床医生逐条审核。')
    examples = dict(neck=['落枕','筋膜枪','针灸','按摩','手麻'], chest=['文胸','钢圈','止汗','腋下','肿块'],
        hands=['护手霜','倒刺','美甲','指甲','脱皮'], abdomen=['肚脐','鼓包','胀气','反酸','排毒'],
        private=['月经碟','白带','卫生巾','避孕','备孕','包皮'], anal=['湿厕纸','便秘','肛裂','便血','冲洗器'],
        legs=['腰痛','膝痛','氨糖','压力袜'], feet=['脚气','脚臭','嵌甲','足跟'],
        bodyskin=['脱毛','鸡皮肤','瘢痕疙瘩','康复新液','风团'], basics=['睡眠','疲劳','补剂','打鼾','情绪'])
    book['search_examples'] = examples[key] if args.part else ['眼睛干涩','发膜','文胸','湿厕纸','月经碟','瘢痕疙瘩','脚气','牙线']
    config = dict(title=title, repository_url='', site_url='', planned_parts=[dict(id=p['id'], title=p['title'], status='planned') for p in plan['parts'] if p['id'] not in delivered])
    registry = dict(schema_version='1.0.0', edition=version,
        entries={'review:' + e['id']: dict(id=e['id'], import_title=e['title']) for ch in chapters for e in ch['entries']},
        units={u['id']: dict(id=u['id'], import_title=u['title']) for ch in chapters for u in ch['units']},
        sources={source_identity(s): dict(id=s['id'], identity=source_identity(s), legacy_number=s['number']) for s in sources})
    for name, value in [('book', book), ('config', config), ('sources', sources), ('id-registry', registry)]: write_json(target / 'content' / (name + '.json'), value)
    for ch in chapters: write_json(target / 'content/chapters' / (ch['id'] + '.json'), ch)
    build(root=target)
    if before != fingerprints(): raise ValueError('Published medical content changed')
    out = HERE / 'compiled' / key
    for ch in chapters: write_json(out / 'chapters' / (ch['id'] + '.json'), ch)
    write_json(out / 'sources.json', sources)
    report = dict(status='built_locally_not_published', part=key, content_version=version,
        entries=len(ids), sources=len(sources), doi_sources=sum(bool(s.get('doi')) for s in sources), empty_cost_sections_omitted=empty_cost,
        chapters={c['id']: len(c['entries']) for c in chapters}, canonical_fingerprints=before,
        source_collision_review=collisions, clinical_review_status='not_clinically_reviewed', output=str(target / 'dist'))
    write_json(out / 'build-report.json', report)
    print(json.dumps({k: v for k, v in report.items() if k not in ('canonical_fingerprints', 'source_collision_review')}, ensure_ascii=False))


if __name__ == '__main__': main()
