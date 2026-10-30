"""Contracts for the nutrition extension and actual-reader audience behavior."""
import hashlib,importlib.util,json,re,shutil,subprocess,unittest,uuid
from pathlib import Path
from scripts.content_model import STABLE_REF,validate_content
from test_whole_book_audience import HARNESS
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'drafts/whole-body/nutrition-followup-20261030'
class NutritionFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('nutrition_contracts',HERE/'build_release.py')
        cls.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.module)
        cls.book,cls.chapters,cls.sources,cls.registry=cls.module.make_data()
        _,old,_,_=cls.module.previous()
        cls.previous={e['id']:e for c in old for e in c['entries']}
        cls.by_id={e['id']:e for c in cls.chapters for e in c['entries']}
        cls.new={f'nutrition-{i:03d}' for i in range(12,24)}
        cls.chapter=next(c for c in cls.chapters if c['id']=='nutrition')
        cls.data=dict(manifest={**cls.book,'book':cls.book},chapters=cls.chapters,entries=list(cls.by_id.values()),sources=cls.sources)
    def render(self,route):
        p=subprocess.run([shutil.which('node'),'-e',HARNESS],input=json.dumps(dict(data=self.data,hash=route,app=(ROOT/'web/app.js').read_text(encoding='utf-8'))),text=True,encoding='utf-8',capture_output=True,check=True)
        return json.loads(p.stdout)
    def test_all_previous_stable_entries_preserved_except_declared_drug_revision(self):
        validate_content(self.book,self.chapters,self.sources,self.registry)
        self.assertEqual(set(self.by_id)-self.previous.keys(),self.new)
        self.assertEqual(len(self.by_id),350);self.assertEqual(len(self.chapters),29)
        for eid,old in self.previous.items():
            if eid=='nutrition-009':continue
            for key in ['title','summary','fields','audience']:
                self.assertEqual(self.by_id[eid][key],old[key],(eid,key))
    def test_old_unit_ids_retained_and_every_nutrition_entry_has_one_home(self):
        self.assertEqual(len(self.chapter['entries']),27)
        units=self.chapter['units']
        self.assertEqual([u['id'] for u in units],['nutrition-u1','nutrition-u2','nutrition-u6','nutrition-u7','nutrition-u3','nutrition-u4','nutrition-u5'])
        assigned=[eid for u in units for eid in u['entry_ids']]
        self.assertEqual(len(assigned),len(set(assigned)))
        self.assertEqual(set(assigned),{e['id'] for e in self.chapter['entries']})
    def test_summaries_references_empty_cost_and_review_status(self):
        known={s['id'] for s in self.sources}
        for eid in self.new|{'nutrition-009'}:
            e=self.by_id[eid]
            self.assertTrue(100<=len(e['summary'])<=180,eid)
            self.assertIsNone(re.search(r'[\n\r|]|\[@|\]\(',e['summary']),eid)
            self.assertEqual(e['fields']['cost'],'')
            self.assertEqual(e['clinical_review_status'],'not_clinically_reviewed')
            self.assertEqual(set(STABLE_REF.findall('\n'.join(e['fields'].values()))),set(e['source_ids']))
            self.assertTrue(set(e['source_ids'])<=known)
            for value in e['fields'].values():
                self.assertTrue(set(re.findall(r'\]\(#/entry/([a-z][a-z0-9-]+)\)',value))<=self.by_id.keys())
    def test_specific_safety_boundaries_survive_export(self):
        k=self.by_id['nutrition-012']['fields']['plain']
        for token in ['肾','钾','孕','儿童']:self.assertIn(token,k)
        drug=self.by_id['nutrition-017']['fields']['plain']
        for token in ['30','27','28','24','司美格鲁肽','替尔泊肽','玛仕度肽']:self.assertIn(token,drug)
        self.assertIn('去脂体重',self.by_id['nutrition-021']['fields']['plain'])
        self.assertIn('不全',self.by_id['nutrition-021']['fields']['plain'])
        self.assertIn('2027',self.by_id['nutrition-014']['fields']['plain'])
        self.assertIn('2026;186(9):1182.',next(s['citation'] for s in self.sources if s.get('doi')=='10.1001/jamainternmed.2026.2769'))
    def test_review_gate_rejects_changed_inputs(self):
        base=ROOT/'.draft-preview/test-temporary';base.mkdir(parents=True,exist_ok=True)
        temp=base/('nutrition-review-'+uuid.uuid4().hex);temp.mkdir()
        names=[p+'-'+k+'.json' for p in ['foundation','glycemia','medications','management'] for k in ['entries','sources']]
        names += [p+'-audit.json' for p in ['foundation','glycemia','medications','management']]
        names += [p+'-independent-review.json' for p in ['foundation','glycemia','medications','management']]
        try:
            for name in names:shutil.copyfile(HERE/name,temp/name)
            self.assertEqual(len(self.module.verify_reviews(temp)),8)
            p=temp/'medications-sources.json';p.write_bytes(p.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'Independent review input changed'):self.module.verify_reviews(temp)
        finally:
            for name in names:(temp/name).unlink(missing_ok=True)
            temp.rmdir()
    @unittest.skipUnless(shutil.which('node'),'Node executes the actual reader')
    def test_adult_and_older_both_sexes_see_all_new_entries(self):
        for band in ['adult','older']:
            for sex in ['male','female']:
                with self.subTest(band=band,sex=sex):
                    self.assertTrue(self.new<=set(self.render('#/chapter/nutrition?band='+band+'&sex='+sex)['cards']))
    @unittest.skipUnless(shutil.which('node'),'Node executes the actual reader')
    def test_under18_sees_no_adult_only_drug_salt_or_body_composition_advice(self):
        child=set(self.render('#/chapter/nutrition?band=child')['cards'])
        teen=set(self.render('#/chapter/nutrition?band=under18')['cards'])
        self.assertFalse(child&self.new)
        self.assertEqual(teen&self.new,{'nutrition-023'})
        self.assertNotIn(self.by_id['nutrition-017']['title'],self.render('#/entry/nutrition-017?band=child')['text'])
    @unittest.skipUnless(shutil.which('node'),'Node executes the actual reader')
    def test_new_and_old_units_and_aggregate_links_resolve(self):
        self.assertEqual(len(self.render('#/chapter/nutrition')['cards']),27)
        self.assertEqual(set(self.render('#/chapter/nutrition?unit=nutrition-u6')['cards']),{'nutrition-015','nutrition-016'})
        self.assertIn('nutrition-017',self.render('#/chapter/nutrition?unit=nutrition-u5')['cards'])
        self.assertEqual(len(self.render('#/chapter/basics')['cards']),60)
if __name__=='__main__':unittest.main()
