"""Apply only exact, reviewed text edits; retain prior inputs and an explicit log."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':
 log_path=HERE/'review-patch-application.json'
 log=load(log_path) if log_path.exists() else []
 applied={r['patch_identity'] for r in log}
 for prefix in ['head','intimate','body']:
  patch_path=HERE/(prefix+'-review-patches.json')
  if not patch_path.exists():continue
  patches=load(patch_path)
  if isinstance(patches,dict):patches=patches['patches']
  for patch in patches:
   identity=hashlib.sha256(json.dumps(patch,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
   if identity in applied:continue
   kind=patch.get('document','rewrites')
   if kind not in ['rewrites','merges']:raise ValueError('Unexpected patch document')
   target=HERE/(prefix+'-'+kind+'.json');values=load(target)
   entry=next(e for e in values if e.get('id',e.get('target'))==patch['id'])
   field=patch['field'];container=entry if field in ['title','summary'] else entry['fields']
   if field not in ['title','summary','cost','plain','benefit','evidence','sources','notes']:raise ValueError('Unexpected field')
   if container[field].count(patch['before'])!=1:raise ValueError('Patch context not unique: '+prefix+' '+patch['id']+' '+field)
   container[field]=container[field].replace(patch['before'],patch['after'],1)
   save(target,values)
   log.append({**patch,'prefix':prefix,'patch_identity':identity,'status':'applied_exactly'})
   applied.add(identity);save(log_path,log)
 print(json.dumps(dict(applied=len(log)),ensure_ascii=False))
