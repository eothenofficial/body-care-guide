"""Verify the actual exported part; no clinical efficacy assertions."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from scripts.content_model import load_content, STABLE_REF, read_json, write_json


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--part', default='master'); args = parser.parse_args()
    target = ROOT / '.draft-preview/whole-body' / args.part
    book, chapters, sources, _ = load_content(target)
    report = read_json(HERE / 'compiled' / args.part / 'build-report.json')
    dist = target / 'dist'; entries = [e for c in chapters for e in c['entries']]
    ids = {e['id'] for e in entries}; source_ids = {s['id'] for s in sources}
    assert len(ids) == report['entries'] and len(sources) == report['sources']
    data = read_json(dist / 'downloads/guide.json')
    offline = (dist / 'downloads/guide-offline.html').read_text(encoding='utf-8')
    embedded = json.loads(re.search(r'window\.__GUIDE_DATA__=(.*?);\n', offline, re.S).group(1))
    assert embedded == data
    api = read_json(dist / 'api/v1/entries.json'); api = api['entries'] if isinstance(api, dict) else api
    assert api == data['entries']
    assert {e['id'] for e in api} == ids
    used = set()
    for chapter in chapters:
        for text in [chapter['intro']] + [u['intro'] for u in chapter['units']]: used.update(STABLE_REF.findall(text))
    markdown = (dist / 'downloads/guide.md').read_text(encoding='utf-8')
    assert not STABLE_REF.search(markdown)
    for e in entries:
        assert 100 <= len(e['summary']) <= 180 and not re.search(r'[\r\n|]|\[@|\]\(', e['summary'])
        used.update(e['source_ids'])
        page = (dist / 'read' / e['id'] / 'index.html').read_text(encoding='utf-8')
        assert e['audience']['scope_note'] in page and e['audience']['scope_note'] in markdown
        assert bool(re.search(r'<h2\b[^>]*>成本</h2>', page)) == bool(e['fields']['cost'])
        assert e['title'] in markdown
        assert e['clinical_review_status'] == 'not_clinically_reviewed'
    assert used == source_ids
    assert [s['number'] for s in sources] == list(range(1, len(sources) + 1))
    for s in sources:
        assert all(s.get(k) for k in ['citation', 'url', 'support', 'limitations', 'reading_depth'])
        if s.get('doi'): assert s['doi_url'] == 'https://doi.org/' + s['doi'] and 'doi:' + s['doi'] in s['citation']
    current = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'content').rglob('*.json'))}
    assert current == report['canonical_fingerprints']
    result = dict(part=args.part, status='passed_structural_and_export_checks', entries=len(entries), sources=len(sources),
        standalone_html_sha256=hashlib.sha256((dist / 'downloads/guide-offline.html').read_bytes()).hexdigest(),
        source_graph_resolves=True, export_data_equal=True, all_audience_ranges_retained=True,
        canonical_content_unchanged=True, clinical_review_status='not_clinically_reviewed')
    write_json(HERE / 'compiled' / args.part / 'validation.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__': main()
