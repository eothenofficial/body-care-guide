"""Withdrawn font settings stay inactive; merged URLs and bookmarks still work."""
import copy,json,shutil,subprocess,unittest
from pathlib import Path
from test_audience_reader import NODE_AUDIENCE
from test_internal_links import reader_fixture
from test_lifestyle_reader import NODE_LIFESTYLE,bookmark_payload
ROOT=Path(__file__).resolve().parents[1]
BASE=NODE_AUDIENCE.split("let validationMessage=''",1)[0].replace('downloads=[]','downloads=[],writes=[]').replace('localStorage:{getItem:()=>null}',"localStorage:{getItem:key=>key==='body-care-guide:reading:v1'?JSON.stringify(input.preferences||null):key.includes('bookmarks')?JSON.stringify(input.saved||[]):null,setItem(key,value){if(input.storageBlocked)throw new Error('blocked');writes.push({key,value});}}")
HARNESS=BASE+r'''
for(const step of input.actions||[]){
 if(step==='open'){doc.getElementById('reading-toggle').focus();doc.getElementById('reading-toggle').emit('click');}
 else if(step==='close')doc.getElementById('reading-close').emit('click');
 else if(step==='escape'){for(const fn of documentHandlers.get('keydown')||[])fn({key:'Escape'});}
 else walk(doc.getElementById('reading-dialog-body')).find(n=>n.tag==='button'&&n.textContent===step).emit('click');
}
process.stdout.write(JSON.stringify({size:doc.body.getAttribute('data-reading-size'),line:doc.body.getAttribute('data-reading-line'),open:doc.getElementById('reading-dialog').open,focusReturned:doc.activeElement===doc.getElementById('reading-toggle'),status:doc.getElementById('reading-dialog-body').textContent,route:location.hash,writes,warning:doc.getElementById('toast').textContent,text:doc.getElementById('main').textContent,saved:doc.getElementById('saved-count').textContent,cards:walk(doc.getElementById('main')).filter(n=>n.className==='entry-card').map(n=>n.attrs['data-entry'])}));
'''
@unittest.skipUnless(shutil.which('node'),'Node runs the actual reader')
class RestoredReadingDefaultsTests(unittest.TestCase):
 def run_reader(self,actions=None,**kwargs):
  payload=dict(data=reader_fixture(),actions=actions or [],app=(ROOT/'web/app.js').read_text(encoding='utf-8'));payload.update(kwargs)
  result=subprocess.run([shutil.which('node'),'-e',HARNESS],input=json.dumps(payload),text=True,encoding='utf-8',capture_output=True,check=True)
  return json.loads(result.stdout)
 def test_no_old_font_state_changes_new_default(self):
  for pref in [None,{'size':24,'line':'relaxed'},{'size':100,'line':'bad'}]:
   result=self.run_reader(preferences=pref,hash='#/chapter/eyes?band=adult&sex=female')
   self.assertIsNone(result['size']);self.assertIsNone(result['line'])
   self.assertEqual(result['route'],'#/chapter/eyes?band=adult&sex=female')
   self.assertFalse(any(w['key']=='body-care-guide:reading:v1' for w in result['writes']))
 def test_reading_settings_have_no_public_controls_or_app_storage_dependency(self):
  app=(ROOT/'web/app.js').read_text(encoding='utf-8');html=(ROOT/'web/index.html').read_text(encoding='utf-8')
  self.assertNotIn('body-care-guide:reading:v1',app)
  for value in ['reading-toggle','reading-dialog','阅读设置']:
   self.assertNotIn(value,app);self.assertNotIn(value,html)
 def test_unavailable_storage_does_not_prevent_reading(self):
  r=self.run_reader(storageBlocked=True,preferences={'size':24,'line':'relaxed'})
  self.assertIsNone(r['size']);self.assertTrue(r['text']);self.assertEqual(r['warning'],'')
 def test_alias_deep_link_preserves_filter_and_bookmark_migrates_once(self):
  data=reader_fixture();data['entries'][0]['title']='完整合并条目';data['entries'][0]['audience']={'age_groups':['adult'],'sexes':['all'],'scope_note':'成人','safety_pin':False}
  data['manifest']['entry_aliases']={'eyes-099':'eyes-001'}
  r=self.run_reader(hash='#/entry/eyes-099?band=adult',data=data,saved=['eyes-099','eyes-001'])
  self.assertEqual(r['route'],'#/entry/eyes-001?band=adult');self.assertEqual(r['saved'],'1');self.assertIn('完整合并条目',r['text'])
  hidden=self.run_reader(hash='#/entry/eyes-099?band=child',data=data)
  self.assertNotIn('完整合并条目',hidden['text']);self.assertIn('已隐藏标题和正文',hidden['text'])
 def test_imported_alias_and_current_bookmark_merge_without_duplicates(self):
  data=reader_fixture();data['manifest']['entry_aliases']={'eyes-099':'eyes-001'}
  payload=dict(data=data,hash='#/saved',saved=['eyes-001'],steps=[dict(action='import',text=bookmark_payload(['eyes-099','eyes-001','eyes-002'])),dict(action='export')],app=(ROOT/'web/app.js').read_text(encoding='utf-8'))
  result=subprocess.run([shutil.which('node'),'-e',NODE_LIFESTYLE],input=json.dumps(payload),text=True,encoding='utf-8',capture_output=True,check=True)
  view=json.loads(result.stdout)
  self.assertEqual(view['savedCount'],2)
  self.assertEqual(json.loads(view['downloads'][0])['entry_ids'],['eyes-001','eyes-002'])
  self.assertNotIn('跳过',view['toast'])
if __name__=='__main__':unittest.main()
