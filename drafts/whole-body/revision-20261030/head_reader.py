"""Read-only prepared text for the independent head chapter sentence review."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def read_prepared(chapter):
    rel = 'drafts/whole-body/baseline/chapters/' + chapter + '.json'
    value = json.loads((ROOT / rel).read_text(encoding='utf-8'))
    patches = json.loads((HERE / 'prose-patches.json').read_text(encoding='utf-8'))['patches']
    for patch in patches:
        if patch['file'] != rel:
            continue
        if patch['target'] == 'chapter':
            target = value
        else:
            collection = 'entries' if patch['target'] == 'entry' else 'units'
            target = next(e for e in value[collection] if e['id'] == patch['id'])
        fields = patch['field'].split('.')
        for key in fields[:-1]:
            target = target[key]
        key = fields[-1]
        if patch['old'] not in target[key]:
            raise ValueError('Patch not applicable: ' + str(patch))
        target[key] = target[key].replace(patch['old'], patch['new'])
    return value

def show(chapter, start=0, end=None):
    data = read_prepared(chapter)
    if start == 0:
        print('CHAPTER', data['title'], data['subtitle'], '\nINTRO', data['intro'])
        for u in data['units']:
            print('UNIT', u['id'], u['title'], '\n', u['intro'])
    for e in data['entries'][start:end]:
        print('\nENTRY', e['id'], e['title'])
        print('SUMMARY', e['summary'])
        for k in ('plain', 'benefit', 'notes'):
            print(k.upper(), e['fields'].get(k, ''))

if __name__ == '__main__':
    import sys
    show(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 0,
         int(sys.argv[3]) if len(sys.argv) > 3 else None)
