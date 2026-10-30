"""Contracts for the physical-care lifestyle extension, using the real reader."""
import importlib.util
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from scripts.content_model import STABLE_REF, validate_content
from test_whole_book_audience import HARNESS, CHILD, TEEN, NOT_ADULT, NOT_OLDER, MALE, FEMALE

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'drafts/whole-body/lifestyle-20261030'


class LifestyleContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('lifestyle_contracts',HERE/'build_release.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        cls.book,cls.chapters,cls.sources,cls.registry=module.make_data()
        cls.entries=[e for c in cls.chapters for e in c['entries']]
        cls.ids={e['id'] for e in cls.entries}
        cls.new={e['id'] for e in cls.entries if e['id'].startswith(('sleep-','nutrition-','activity-','energy-'))}
        cls.data=dict(manifest={**cls.book,'book':cls.book},chapters=cls.chapters,entries=cls.entries,sources=cls.sources)

    def render(self,route):
        result=subprocess.run([shutil.which('node'),'-e',HARNESS],input=json.dumps(dict(
            data=self.data,hash=route,app=(ROOT/'web/app.js').read_text(encoding='utf-8'))),
            text=True,encoding='utf-8',capture_output=True,check=True)
        return json.loads(result.stdout)

    def test_every_previous_id_is_preserved_and_thirty_unique_entries_added(self):
        validate_content(self.book,self.chapters,self.sources,self.registry)
        old={e['id'] for p in (ROOT/'drafts/whole-body/compiled/master/chapters').glob('*.json')
             for e in json.loads(p.read_text(encoding='utf-8'))['entries']}
        self.assertEqual(self.ids-old,self.new)
        self.assertEqual(len(self.new),30)
        self.assertEqual(len(self.entries),330)
        self.assertEqual(len(self.chapters),29)
        self.assertEqual(self.book['chapter_aliases']['basics']['chapter_ids'],['sleep','nutrition','activity','energy'])
        self.assertEqual({c['id']:len(c['entries']) for c in self.chapters[-4:]},dict(sleep=10,nutrition=15,activity=10,energy=5))

    def test_new_sources_summaries_icons_and_honest_review_status(self):
        symbols=set(re.findall(r'<symbol id="i-([^\"]+)"',(ROOT/'web/index.html').read_text(encoding='utf-8')))
        for chapter in self.chapters:
            self.assertIn(chapter['icon'],symbols)
        self.assertEqual(len({c['icon'] for c in self.chapters}),29)
        sources={s['id']:s for s in self.sources}
        for e in self.entries:
            self.assertTrue(100<=len(e['summary'])<=180,e['id'])
            self.assertIsNone(re.search(r'[\n\r|]|\[@|\]\(',e['summary']),e['id'])
            self.assertEqual(e['clinical_review_status'],'not_clinically_reviewed')
            self.assertEqual(set(STABLE_REF.findall('\n'.join(e['fields'].values()))),set(e['source_ids']))
            self.assertTrue(set(e['source_ids'])<=sources.keys())
        for s in self.sources:
            if s.get('doi'):
                self.assertEqual(s['doi_url'],'https://doi.org/'+s['doi'])
                self.assertIn('doi:'+s['doi']+'.',s['citation'])

    @unittest.skipUnless(shutil.which('node'),'Node.js executes the actual reader')
    def test_full_book_age_and_sex_filters_keep_reviewed_editorial_cohorts(self):
        # Diet/supplement plans stay adult. Exertional emergencies include
        # children; safe earbud habits include teens. These are reviewed actions,
        # not memberships inferred from app metadata or a matching algorithm.
        child_new={'activity-001','activity-002','activity-003'}
        teen_new=child_new|{'sleep-007'}
        older_new=self.new-{'nutrition-006','nutrition-007'}
        golden=dict(child=CHILD|child_new,teen=TEEN|teen_new,under18=CHILD|TEEN|teen_new,
                    adult=(self.ids-self.new)-NOT_ADULT|self.new,
                    older=(self.ids-self.new)-NOT_OLDER|older_new)
        for band in golden:
            for sex in ('','female','male'):
                with self.subTest(band=band,sex=sex):
                    expected=golden[band]-(MALE if sex=='female' else FEMALE if sex=='male' else set())
                    self.assertEqual(set(self.render(f'#/read?band={band}&sex={sex}')['cards']),expected)

    @unittest.skipUnless(shutil.which('node'),'Node.js executes the actual reader')
    def test_old_basics_route_includes_all_four_topics_and_all_forty_entries(self):
        view=self.render('#/chapter/basics')
        self.assertEqual(len(view['cards']),40)
        for name in ('睡眠与作息','饮食与体重','运动与恢复','疲劳与日常风险'):
            self.assertIn(name,view['text'])


if __name__=='__main__':unittest.main()
