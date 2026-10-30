"""Read the remaining three fields after the frozen prose and head patches."""
import json
from head_reader import HERE, read_prepared

def prepared(chapter):
    data = read_prepared(chapter)
    rel = 'drafts/whole-body/baseline/chapters/' + chapter + '.json'
    for p in json.loads((HERE/'head-reader-patches.json').read_text(encoding='utf-8'))['patches']:
        if p['file'] != rel:
            continue
        if p['target']=='chapter':
            obj=data
        else:
            obj=next(e for e in data['entries' if p['target']=='entry' else 'units'] if e['id']==p['id'])
        bits=p['field'].split('.')
        for b in bits[:-1]:
            obj=obj[b]
        if p['old'] not in obj[bits[-1]]:
            raise ValueError(p)
        obj[bits[-1]]=obj[bits[-1]].replace(p['old'],p['new'])
    return data

def show(chapter,start=0,end=None):
    c=prepared(chapter)
    for e in c['entries'][start:end]:
        print('\nENTRY',e['id'],e['title'])
        for k in ['cost','evidence','sources']:
            print(k.upper(), e['fields'].get(k,''))

if __name__=='__main__':
    import sys
    show(sys.argv[1],int(sys.argv[2]) if len(sys.argv)>2 else 0,
         int(sys.argv[3]) if len(sys.argv)>3 else None)
