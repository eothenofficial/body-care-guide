"""Full-book editorial coverage, evidence continuity and real-reader compatibility."""
import hashlib,importlib.util,json,re,shutil,subprocess,unittest,uuid
from pathlib import Path
from scripts.build import build
from scripts.content_model import STABLE_REF,validate_content
from scripts.static_pages import render_prose
from test_content import install_fixture,workspace_temp
from test_whole_book_audience import HARNESS
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'drafts/whole-body/editorial-readability-20261030'
@unittest.skipUnless(shutil.which('node'),'Node runs the actual reader')
class EditorialReadabilityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('editorial_contracts',HERE/'build_release.py');cls.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.module)
  cls.book,cls.chapters,cls.sources,cls.registry=cls.module.make_data()
  _,previous,old_sources,_=cls.module.previous()
  cls.old={e['id']:e for c in previous for e in c['entries']};cls.old_sources=old_sources
  cls.entries={e['id']:e for c in cls.chapters for e in c['entries']};cls.aliases=cls.book['entry_aliases']
  cls.data=dict(manifest={**cls.book,'book':cls.book},chapters=cls.chapters,entries=list(cls.entries.values()),sources=cls.sources)
 def render(self,route):
  p=subprocess.run([shutil.which('node'),'-e',HARNESS],input=json.dumps(dict(data=self.data,hash=route,app=(ROOT/'web/app.js').read_text(encoding='utf-8'))),text=True,encoding='utf-8',capture_output=True,check=True)
  return json.loads(p.stdout)
 def test_every_original_entry_is_rewritten_or_explicitly_merged(self):
  validate_content(self.book,self.chapters,self.sources,self.registry)
  coverage=json.loads((HERE/'editorial-coverage.json').read_text(encoding='utf-8'))
  self.assertEqual(coverage['reviewed'],350);self.assertEqual(len(coverage['entries']),350)
  self.assertEqual(set(self.entries)|set(self.aliases),set(self.old));self.assertFalse(set(self.entries)&set(self.aliases))
  self.assertEqual(len(self.chapters),29);self.assertEqual(len(self.aliases),9);self.assertEqual(len(self.entries),341)
  self.assertLess(coverage['revised_plain_chars'],coverage['original_plain_chars'])
 def test_all_original_evidence_ids_survive_in_each_standalone_or_combined_entry(self):
  for eid,e in self.entries.items():
   members=[eid]+[old for old,target in self.aliases.items() if target==eid]
   required={sid for member in members for sid in self.old[member]['source_ids']}
   self.assertEqual(set(e['source_ids']),required,eid)
   self.assertEqual(e['clinical_review_status'],'not_clinically_reviewed')
  self.assertTrue({s['id'] for s in self.old_sources}<={s['id'] for s in self.sources})
 def test_summaries_are_edited_pure_short_paragraphs_and_internal_links_resolve(self):
  for eid,e in self.entries.items():
   self.assertTrue(60<=len(e['summary'])<=140,eid)
   self.assertIsNone(re.search(r'[\n\r|`]|\[@|\]\(',e['summary']),eid)
   self.assertNotEqual(e['summary'],self.old[eid]['summary'],eid)
   for value in e['fields'].values():self.assertTrue(set(re.findall(r'\]\(#/entry/([a-z][a-z0-9-]+)\)',value))<=self.entries.keys(),eid)
 def test_merges_do_not_expand_demographic_scope_and_preserve_urgent_flag(self):
  for old,target in self.aliases.items():
   for key in ['age_groups','sexes']:self.assertEqual(self.old[old]['audience'][key],self.entries[target]['audience'][key])
   if self.old[old]['audience']['safety_pin']:self.assertTrue(self.entries[target]['audience']['safety_pin'])
  self.assertNotIn('nose-003',self.aliases);self.assertNotIn('bodyskin-014',self.aliases)
 def test_home_has_purpose_audience_outcomes_sources_and_no_reductive_medical_claim(self):
  home=self.book['home_content'];self.assertIn('各年龄',home['audience']);self.assertIn('所有性别',home['audience'])
  self.assertEqual(len(home['decisions']),3);self.assertIn('身体和情绪会彼此影响',home['why'])
  self.assertIn('及时寻求帮助',home['why']);self.assertTrue(STABLE_REF.search(home['why']))
  self.assertTrue(set(STABLE_REF.findall(self.book['front_matter']))<={s['id'] for s in self.sources})
 def test_old_merged_link_resolves_full_content_but_child_scope_still_hides_it(self):
  old='eyes-015';target=self.aliases[old]
  page=self.render('#/entry/'+old+'?band=adult&sex=female')
  self.assertEqual(page['hash'],'#/entry/'+target+'?band=adult&sex=female');self.assertIn(self.entries[target]['title'],page['text'])
  hidden=self.render('#/entry/'+old+'?band=child');self.assertNotIn(self.entries[target]['title'],hidden['text'])
 def test_female_and_older_filters_do_not_leak_opposite_sex_or_child_only_content(self):
  female=self.render('#/chapter/private?sex=female')['cards'];male=self.render('#/chapter/private?sex=male')['cards']
  self.assertNotIn('private-030',female);self.assertNotIn('private-022',male)
  older=self.render('#/chapter/private?band=older')['cards'];self.assertNotIn('private-005',older)
 def test_all_merged_static_shares_show_full_new_entry_and_canonical_reader_link(self):
  # Build this run's reviewed data; an old local preview must not satisfy the test.
  with workspace_temp() as root:
   install_fixture(root,(self.book,self.chapters,self.sources,self.registry,[]))
   shutil.copytree(ROOT/'web',root/'web',dirs_exist_ok=True)
   build(root,built_at='2026-10-30T00:00:00Z')
   dist=root/'dist';sources={s['id']:s for s in self.sources}
   self.assertEqual(len(list((dist/'read').glob('*/index.html'))),len(self.entries)+len(self.aliases))
   for old,target in self.aliases.items():
    with self.subTest(retired=old,target=target):
     text=(dist/'read'/old/'index.html').read_text(encoding='utf-8')
     self.assertEqual(text,(dist/'read'/target/'index.html').read_text(encoding='utf-8'))
     self.assertIn(self.entries[target]['title'],text);self.assertIn('../../#/entry/'+target,text)
     for value in self.entries[target]['fields'].values():
      if value.strip():self.assertIn(render_prose(value,sources,set(self.entries)),text)
 def test_final_review_gate_binds_all_four_groups_and_rejects_later_changes(self):
  base=ROOT/'.draft-preview/test-temporary';base.mkdir(parents=True,exist_ok=True)
  temp=base/('editorial-review-'+uuid.uuid4().hex);temp.mkdir()
  names=[p+'-'+suffix+'.json' for p in ['head','intimate','body'] for suffix in ['rewrites','merges']]+['home-content.json','home-sources.json']+[p+'-independent-review.json' for p in ['head','intimate','body','home']]
  try:
   for name in names:shutil.copyfile(HERE/name,temp/name)
   self.assertEqual(len(self.module.verify_reviews(temp)),8)
   target=temp/'head-merges.json';target.write_bytes(target.read_bytes()+b'\n')
   with self.assertRaisesRegex(ValueError,'Reviewed editorial input changed'):self.module.verify_reviews(temp)
  finally:
   for name in names:(temp/name).unlink(missing_ok=True)
   temp.rmdir()
if __name__=='__main__':unittest.main()
