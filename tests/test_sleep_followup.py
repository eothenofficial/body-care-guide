"""Sleep-scenario release: migration, citation scope and actual-reader routing."""
import importlib.util
import json
import re
import shutil
import subprocess
import uuid
import unittest
from pathlib import Path

from scripts.content_model import validate_content,STABLE_REF
from test_whole_book_audience import HARNESS

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'drafts/whole-body/sleep-followup-20261030'


class SleepFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('sleep_followup_contracts',HERE/'build_release.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        cls.module=module
        cls.book,cls.chapters,cls.sources,cls.registry=module.make_data()
        _,old,_,_=module.previous()
        cls.previous={e['id']:e for c in old for e in c['entries']}
        cls.by_id={e['id']:e for c in cls.chapters for e in c['entries']}
        cls.new={f'sleep-{i:03d}' for i in range(9,17)}
        cls.sleep=next(c for c in cls.chapters if c['id']=='sleep')
        cls.data=dict(manifest={**cls.book,'book':cls.book},chapters=cls.chapters,entries=list(cls.by_id.values()),sources=cls.sources)

    def render(self,route):
        p=subprocess.run([shutil.which('node'),'-e',HARNESS],input=json.dumps(dict(data=self.data,hash=route,
            app=(ROOT/'web/app.js').read_text(encoding='utf-8'))),text=True,encoding='utf-8',capture_output=True,check=True)
        return json.loads(p.stdout)

    def test_previous_330_entries_remain_and_only_eight_stable_ids_are_added(self):
        validate_content(self.book,self.chapters,self.sources,self.registry)
        self.assertEqual(set(self.by_id)-self.previous.keys(),self.new)
        self.assertEqual(len(self.by_id),338)
        self.assertEqual(len(self.chapters),29)
        for eid,old in self.previous.items():
            # Only chapter placement/ordinal and source display numbering may change.
            for field in ('title','summary','fields','audience'):
                self.assertEqual(self.by_id[eid][field],old[field],(eid,field))

    def test_sleep_order_follows_problem_habits_treatment_and_next_day_decisions(self):
        self.assertEqual(len(self.sleep['entries']),18)
        self.assertEqual([u['id'] for u in self.sleep['units']],['sleep-u1','sleep-u2','sleep-u3','sleep-u4','sleep-u5'])
        self.assertEqual(self.sleep['units'][-1]['entry_ids'],['sleep-012','sleep-013'])
        self.assertEqual(self.sleep['units'][2]['entry_ids'],['sleep-014','sleep-002','sleep-003','sleep-004','sleep-015'])
        self.assertEqual({e['id'] for e in self.sleep['entries']},
            {f'sleep-{i:03d}' for i in range(1,17)}|{'basics-001','basics-002'})

    def test_new_summaries_population_and_all_link_targets_resolve(self):
        known={s['id'] for s in self.sources}
        for eid in self.new:
            e=self.by_id[eid]
            self.assertTrue(100<=len(e['summary'])<=180,eid)
            self.assertIsNone(re.search(r'[\n\r|]|\[@|\]\(',e['summary']),eid)
            self.assertEqual(e['audience']['age_groups'],['adult','older'])
            self.assertEqual(e['audience']['sexes'],['all'])
            self.assertEqual(e['clinical_review_status'],'not_clinically_reviewed')
            self.assertEqual(e['fields']['cost'],'')
            self.assertEqual(set(STABLE_REF.findall('\n'.join(e['fields'].values()))),set(e['source_ids']))
            self.assertTrue(set(e['source_ids'])<=known)
            for value in e['fields'].values():
                self.assertTrue(set(re.findall(r'\]\(#/entry/([a-z][a-z0-9-]+)\)',value))<=self.by_id.keys())

    def test_formal_publication_metadata_does_not_take_doi_year_as_issue_year(self):
        s=next(s for s in self.sources if s.get('doi')=='10.1016/j.jbct.2025.100542')
        self.assertIn('2026;36(2):100542.',s['citation'])
        self.assertNotIn('ahead of print',s['citation'].lower())
        self.assertEqual(s['doi_url'],'https://doi.org/10.1016/j.jbct.2025.100542')

    def test_review_gate_rejects_changed_author_input(self):
        scratch=ROOT/'.draft-preview/test-temporary'
        scratch.mkdir(parents=True,exist_ok=True)
        temp=scratch/('review-'+uuid.uuid4().hex)
        self.assertTrue(temp.resolve().is_relative_to(scratch.resolve()))
        temp.mkdir()
        names=[name+'-'+kind+'.json' for name in ('exercise','meals','screen','recovery') for kind in ('entries','sources')]
        names += [name+'.json' for name in ('exercise-independent-review','meals-screen-independent-review','recovery-independent-review')]
        try:
            for name in names:shutil.copyfile(HERE/name,temp/name)
            self.assertEqual(len(self.module.verify_reviews(temp)),8)
            target=temp/'screen-sources.json'
            target.write_bytes(target.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'Independent review input changed'):
                self.module.verify_reviews(temp)
        finally:
            # Delete only the files this test named; no recursive directory delete.
            for name in names:(temp/name).unlink(missing_ok=True)
            temp.rmdir()

    @unittest.skipUnless(shutil.which('node'),'Node.js executes the actual reader')
    def test_new_sleep_entries_do_not_leak_into_under18_and_remain_for_older_both_sexes(self):
        self.assertFalse(set(self.render('#/chapter/sleep?band=child')['cards'])&self.new)
        self.assertEqual(set(self.render('#/chapter/sleep?band=under18')['cards']),{'sleep-007'})
        for sex in ('female','male'):
            with self.subTest(sex=sex):
                view=self.render('#/chapter/sleep?band=older&sex='+sex)
                self.assertEqual(len(view['cards']),18)
                self.assertTrue(self.new<=set(view['cards']))

    @unittest.skipUnless(shutil.which('node'),'Node.js executes the actual reader')
    def test_original_unit_and_basics_group_urls_resolve_new_content(self):
        old_unit=self.render('#/chapter/sleep?unit=sleep-u3')
        self.assertEqual(set(old_unit['cards']),{'sleep-014','sleep-002','sleep-003','sleep-004','sleep-015'})
        group=self.render('#/chapter/basics')
        self.assertEqual(len(group['cards']),48)
        self.assertTrue(self.new<=set(group['cards']))


if __name__=='__main__':unittest.main()
