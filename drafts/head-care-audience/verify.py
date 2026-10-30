"""Verify the compiled review artifacts; this is not clinical validation."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIST = ROOT / '.draft-preview/head-care-audience/dist'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    report = read(HERE / 'build-report.json')
    sources = read(HERE / 'compiled/sources.json')
    chapters = [read(HERE / 'compiled/chapters' / (key + '.json'))
                for key in report['chapters']]
    entries = [entry for chapter in chapters for entry in chapter['entries']]
    ids = {entry['id'] for entry in entries}
    source_ids = {source['id'] for source in sources}
    assert len(ids) == len(entries) == report['entries']
    assert len(source_ids) == len(sources) == report['sources']
    assert [s['number'] for s in sources] == list(range(1, len(sources) + 1))
    used = set()
    doi_sources = []
    omitted = 0
    body = '\n'.join(str(c) for c in chapters)
    for word in ['九龙', 'kowloonhospital', 'haodf.com', '实际算账示例', '异常剧痛']:
        assert word not in body, word
    assert not re.search(r'\d+\s*元(?:/|／|每|一|\b)', body)
    for entry in entries:
        summary = entry['summary']
        assert 100 <= len(summary) <= 180, (entry['id'], len(summary))
        assert not any(x in summary for x in ['\n', '|', '[@', ']('])
        assert entry['clinical_review_status'] == 'not_clinically_reviewed'
        assert entry.get('audience', {}).get('age_groups'), entry['id']
        assert type(entry['audience'].get('safety_pin')) is bool, entry['id']
        refs = set(re.findall(r'\[@([^\]]+)\]', '\n'.join(entry['fields'].values())))
        assert refs == set(entry['source_ids'])
        assert refs <= source_ids
        used.update(refs)
        for target in re.findall(r'\]\(#/entry/([^\)]+)\)', '\n'.join(entry['fields'].values())):
            assert target in ids, target
        page = (DIST / 'read' / entry['id'] / 'index.html').read_text(encoding='utf-8')
        assert entry['audience']['scope_note'] in page, entry['id']
        has_cost_heading = bool(re.search(r'<h2\b[^>]*>成本</h2>', page))
        assert has_cost_heading == bool(entry['fields']['cost']), entry['id']
        if not entry['fields']['cost']:
            omitted += 1
    assert used == source_ids
    assert omitted == report['omitted_cost_sections']
    for source in sources:
        assert all(source.get(key) for key in ['citation', 'url', 'support', 'limitations', 'reading_depth'])
        if source.get('doi'):
            assert re.fullmatch(r'10\.\d{4,9}/[^\s<>]+', source['doi'])
            assert source['citation'].endswith('doi:' + source['doi'] + '.')
            assert source['doi_url'] == 'https://doi.org/' + source['doi']
            doi_sources.append(source)
        else:
            assert '[Internet].' in source['citation']
            assert '[cited 2026 Oct 29]. Available from: ' + source['url'] in source['citation']
    assert len({s['doi'].lower() for s in doi_sources}) == len(doi_sources) == report['doi_sources']
    for relative, expected in report['canonical_fingerprints'].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    api_entries = read(DIST / 'api/v1/entries.json')
    # APIs retain the existing public shape; compare the actual record IDs.
    records = api_entries if isinstance(api_entries, list) else api_entries['entries']
    assert {entry['id'] for entry in records} == ids
    assert {e['id']:e['audience'] for e in records} == {e['id']:e['audience'] for e in entries}
    placements={e['id']:e['chapter_id'] for e in entries}
    assert all(placements[eid]=='lips' for eid in ('oral-014','oral-015','oral-008'))
    assert placements['oral-012']=='oral'
    validation = {
        'checked_on': '2026-10-29', 'status': 'passed_structural_checks',
        'entries': len(entries), 'sources': len(sources), 'doi_sources': len(doi_sources),
        'empty_cost_sections_omitted': omitted,
        'summary_length_range': [min(len(e['summary']) for e in entries), max(len(e['summary']) for e in entries)],
        'all_references_resolve': True, 'all_cross_entry_links_resolve': True,
        'static_entry_pages': len(entries), 'published_medical_content_unchanged': True,
        'clinical_review_status': 'not_clinically_reviewed',
        'audience_metadata_complete': True, 'moved_entry_urls_preserved': True,
        'age_groups': {group:sum(group in e['audience']['age_groups'] for e in entries) for group in ['child','teen','adult','older']},
        'limits': '结构、引用格式与导出检查通过不等于临床结论已获专业签审；题录和支持范围另看独立复核及来源记录。'
    }
    (HERE / 'validation.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [
        '# 五官与头皮头发引用核对报告', '',
        '核对日期：2026年10月29日。本版在116条五官与头皮头发稿上，补耳廓耳饰、儿童视力、换牙与分龄正畸、地包天、缺牙修复；口腔分为牙齿与牙周、嘴唇与口腔黏膜。', '',
        f"七个模块共{len(entries)}条建议，{len(sources)}项实际引用来源，{len(doi_sources)}篇带DOI的期刊资料；{omitted}条省略空成本栏。", '',
        '## 来源与推论控制', '',
        '已排除历史收费资料、个人转载、假设金额和无法支持具体结论的营销材料。现行指南、原始监管安全信息、专业机构患者指导与临床研究分别使用，不把机构名当作疗效等级。旧试验按实际人群和结局使用，不因年份旧一概删除。', '',
        '新增视力内容核查国家标准、2026近视防治指南、成人近视与集合不足综述，以及监管机构和专业学会屈光手术材料。儿童控制数据不推为成人同效；术式选择不按广告名称排序。', '',
        '头发内容把头皮、发纤维与毛囊生长分开。离体发束实验保留为C类依据，不冒称人体生发证据；补充剂、口服或外用生发药、设备与植发分别核适用性。非那雄胺安全采用2025EMA及2026MHRA更新，不承诺风险停药后必然消失。', '',
        '面部补充以2026黄褐斑共识核对处理顺序；肉毒安全采用2026CDC原页，排除学会旧页与新警示冲突的绝对安全概括。处方激素与未经指导自用激素分开，避免笼统停所有鼻喷或吸入处方。', '',
        '## 引用和实际读取深度', '',
        '期刊统一Vancouver格式，核作者前6人及et al.、正式年卷期页或文章号、DOI；普通机构网页写真实可核日期与访问日，不补造DOI。源记录保留支持、局限、实际读取范围；摘要和全文不混称。', '',
        '各领域原稿和独立复核记录位于evidence目录。旧审计仅代表其标明的历史范围；本轮增加ears-audience、dental-age、child-vision及audience-scope核对，独立复核分别记录实际读取范围。AI编辑复核不等于持证临床人员签审，工程测试也不证明医学正确。', '',
        '本轮通过交叉复核补足窝沟封闭防龋句的直接NIDCR来源，并把缺牙比较表中的固定桥限定为天然牙支持桥；新旧来源有不同护理口径时不拼凑统一疗程。', '',
        '## 本版DOI文献', ''
    ]
    for source in doi_sources:
        lines.extend([f"### 文献[{source['number']}]", '', source['citation'], '',
                      f"[DOI]({source['doi_url']}) · [核查记录]({source['url']})", '',
                      '实际读取范围：' + source['reading_depth'], '',
                      '适用限制：' + source['limitations'], ''])
    (HERE / '引用与证据核对报告.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == '__main__':
    main()
