"""Regression cases for the actual 300-entry book and browser-reader code.

The golden readership groups below are explicit editorial decisions, not the
JavaScript matcher translated into Python. A metadata change must be reviewed
and its corresponding golden clinical/reading scenario reconsidered.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import unittest
from pathlib import Path
from urllib.parse import urlencode

import test_audience_reader as reader_support

ROOT = Path(__file__).resolve().parents[1]
REVISION = ROOT / 'drafts/whole-body/revision-20261030'


def ids(prefix, *numbers):
    return {f'{prefix}-{number:03d}' for number in numbers}


# These reflect action subjects, including shared-partner actions. Do not infer
# sex from a lone occurrence of a body-part word inside a shared article.
MALE = (ids('private', 1,4,5,6,13,29,30,31,32,33,36,53)
        | ids('hair', 18) | ids('chest', 4))
FEMALE = (ids('private', 2,3,8,9,10,11,16,18,20,21,22,23,24,25,26,27,
              39,40,41,42,43,44,47,49,52,56)
          | ids('chest', 5,6,7))

# All ages here mean a reading/safety path, not a universal drug or operation.
CHILD = (ids('ears',1,5,8,9,10) | ids('eyes',8,20,21,23,30,31,32)
         | ids('oral',19,20,21) | ids('hands',1,2,7,10)
         | ids('anal',1,2,3,4,6,11,12)
         | ids('private',1,5,12,14,19,35,36)
         | ids('bodyskin',1,2,3,7,8,12,13,22,23,25))
TEEN = (CHILD | ids('ears',11) | ids('skin',6,8,18)
        | ids('chest',2,4,5,9,12) | ids('hands',3,5,6,8)
        | ids('legs',11) | ids('feet',4,7,9,12)
        | ids('bodyskin',4,5,6,9,14,24)
        | ids('private',2,3,6,7,8,9,10,13,15,20,21,22,23,24,25,26,27,
              29,30,34,37,38,39,40,41,42,43,44,45,47,56))
NOT_ADULT = ids('eyes',31,32) | ids('oral',19,20) | ids('private',5)
NOT_OLDER = (ids('eyes',8,24,27,28,29,31,32)
             | ids('hair',17,18,19,21,23) | ids('oral',19,20)
             | ids('private',5,8,9,20,21,22,23,24,27,37,39,40,41,42,43,44,
                   45,47,49,51,52,56))

# Extend only the existing DOM harness. The application under test is unmodified
# web/app.js; these extra observations expose relevant reader surfaces.
HARNESS = reader_support.NODE_AUDIENCE.replace(
    "localStorage:{getItem:()=>null}",
    "localStorage:{getItem:key=>key.includes('bookmark')?JSON.stringify(input.saved||[]):null,setItem(){}}",
).split('process.stdout.write(', 1)[0] + r'''
const articleNavigation=nodes.filter(n=>n.tag==='nav'&&n.className==='article-bottom');
const unitTabs=nodes.filter(n=>n.className==='unit-tabs');
const referenceCards=nodes.filter(n=>n.className==='source-card');
process.stdout.write(JSON.stringify({
  cards:nodes.filter(n=>n.className==='entry-card').map(n=>n.attrs['data-entry']),
  text:doc.getElementById('main').textContent,
  hash:location.hash,
  links:nodes.filter(n=>n.tag==='a').map(n=>({href:n.attrs.href,label:n.textContent})),
  adjacentLinks:articleNavigation.flatMap(n=>walk(n).filter(x=>x.tag==='a').map(x=>({href:x.attrs.href,label:x.textContent}))),
  unitTabs:unitTabs.map(n=>n.textContent).join(''),
  referenceCards:referenceCards.map(n=>n.textContent),
  sidebar:doc.getElementById('sidebar').textContent,
  sidebarLinks:walk(doc.getElementById('sidebar')).filter(n=>n.tag==='a').map(n=>n.getAttribute('href'))
}));
'''


@unittest.skipUnless(shutil.which('node'), 'Node.js executes the actual reader')
class WholeBookAudienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('whole_book_release', REVISION/'build_release.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        book, chapters, sources, _ = module.make_data()
        cls.data = dict(manifest={**book, 'book': book}, chapters=chapters,
                        entries=[entry for chapter in chapters for entry in chapter['entries']], sources=sources)
        cls.by_id = {entry['id']: entry for entry in cls.data['entries']}
        cls.all_ids = set(cls.by_id)
        cls.golden = dict(child=CHILD, teen=TEEN, under18=CHILD|TEEN,
                          adult=cls.all_ids-NOT_ADULT, older=cls.all_ids-NOT_OLDER)

    def render(self, route, *, steps=None, saved=None):
        completed = subprocess.run(
            [shutil.which('node'), '-e', HARNESS],
            input=json.dumps(dict(data=self.data, hash=route, steps=steps or [], saved=saved or [],
                app=(ROOT/'web/app.js').read_text(encoding='utf-8'))),
            text=True, encoding='utf-8', capture_output=True, check=True)
        return json.loads(completed.stdout)

    def test_reviewed_metadata_matches_explicit_editorial_partitions(self):
        self.assertEqual(len(self.by_id), 300)
        self.assertFalse(MALE & FEMALE)
        self.assertEqual({eid for eid,e in self.by_id.items() if e['audience']['sexes']==['male']}, MALE)
        self.assertEqual({eid for eid,e in self.by_id.items() if e['audience']['sexes']==['female']}, FEMALE)
        for band in ('child','teen','adult','older'):
            with self.subTest(band=band):
                self.assertEqual({eid for eid,e in self.by_id.items() if band in e['audience']['age_groups']}, self.golden[band])
        for eid in (ids('private',12,14,15,17,19,28,34,35,37,38,45,46,48,50,51,54,55)):
            self.assertEqual(self.by_id[eid]['audience']['sexes'], ['all'], eid)

    def test_all_300_entries_against_age_and_sex_matrix(self):
        # Fixed human-reviewed cohorts catch both a broken matcher and accidental
        # metadata broadening. Include safety pins: they do not get an exemption.
        for band in ('child','teen','under18','adult','older'):
            for sex in ('','female','male'):
                expected = self.golden[band] - (MALE if sex=='female' else FEMALE if sex=='male' else set())
                with self.subTest(band=band,sex=sex):
                    view = self.render('#/read?'+urlencode(dict(band=band,sex=sex)))
                    self.assertEqual(set(view['cards']), expected)

    def test_private_gender_and_age_counterexamples(self):
        female = self.render('#/chapter/private?sex=female')
        male = self.render('#/chapter/private?sex=male')
        older = self.render('#/chapter/private?band=older')
        self.assertIn('private-022', female['cards'])
        self.assertNotIn('private-001', female['cards'])
        self.assertNotIn('private-036', female['cards'])
        self.assertNotIn('private-002', male['cards'])
        self.assertFalse(set(male['cards']) & ids('private',*range(20,28),56))
        self.assertNotIn('private-005', older['cards'])
        self.assertIn('private-004', older['cards'])
        self.assertNotIn('男性分泌物、皮肤疙瘩、硬块和血精分别查因', female['unitTabs'])
        self.assertNotIn('先选合适的经期用品', male['unitTabs'])
        # This was a separate leak after cards were fixed: the mixed emergency
        # unit introduction still listed testicle pain and persistent erections.
        self.assertNotIn('睾丸痛、严重下腹症状', female['text'])
        self.assertNotIn('持续勃起与近期暴露', female['text'])

    def test_exact_age_boundaries_match_the_reviewed_life_stage(self):
        for age, band in ((0,'child'),(11,'child'),(12,'teen'),(17,'teen'),
                          (18,'adult'),(64,'adult'),(65,'older'),(120,'older')):
            with self.subTest(age=age):
                self.assertEqual(set(self.render(f'#/read?age={age}&sex=male')['cards']),
                                 self.golden[band]-FEMALE)
        self.assertIn('private-005',self.render('#/read?age=17&sex=male')['cards'])
        self.assertNotIn('private-005',self.render('#/read?age=18&sex=male')['cards'])
        child = self.render('#/read?band=child')['cards']
        self.assertFalse(set(child) & ids('hair',17,18,19,23))
        self.assertFalse(set(child) & ids('eyes',27,28,29))
        self.assertNotIn('oral-022',child)

    def test_direct_links_hide_excluded_title_and_body_then_clear_restores(self):
        for eid,query in (('private-001','sex=female'),('private-036','sex=female'),
                          ('private-022','sex=male'),('private-056','sex=male'),
                          ('private-005','band=older'),('hair-018','band=child')):
            with self.subTest(eid=eid):
                route=f'#/entry/{eid}?{query}'
                view=self.render(route)
                self.assertIn('已隐藏标题和正文',view['text'])
                self.assertNotIn(self.by_id[eid]['title'],view['text'])
                self.assertNotIn(self.by_id[eid]['fields']['plain'].split('\n')[0].replace('**',''),view['text'])
                restored=self.render(route,steps=[dict(action='clear')])
                self.assertIn(self.by_id[eid]['title'],restored['text'])
                self.assertNotIn('已隐藏标题和正文',restored['text'])

    def test_adjacent_links_never_reintroduce_the_excluded_sex_or_child_entry(self):
        for eid,query,excluded in (('private-002','sex=female',MALE),
                                  ('private-001','sex=male',FEMALE),
                                  ('private-004','band=older',NOT_OLDER)):
            view=self.render(f'#/entry/{eid}?{query}')
            for link in view['adjacentLinks']:
                if link['href'].startswith('#/entry/'):
                    linked_id=link['href'].split('/entry/',1)[1].split('?',1)[0]
                    self.assertNotIn(linked_id,excluded)
                    self.assertIn(query,link['href'])

    def test_bookmarks_are_filtered_without_deleting_saved_items(self):
        saved=['private-001','private-002','private-005','private-022','private-036','private-007']
        self.assertEqual(set(self.render('#/saved?sex=female',saved=saved)['cards']),
                         {'private-002','private-022','private-007'})
        self.assertEqual(set(self.render('#/saved?sex=male',saved=saved)['cards']),
                         {'private-001','private-005','private-036','private-007'})
        self.assertNotIn('private-005',self.render('#/saved?band=older',saved=saved)['cards'])
        self.assertEqual(set(self.render('#/saved',saved=saved)['cards']),set(saved))

    def test_filtering_a_previously_selected_opposite_sex_unit_returns_to_matching_content(self):
        # Switching sex inside a male-only unit must not falsely report that the
        # entire chapter lacks female content while 44 matching entries exist.
        view=self.render('#/chapter/private?unit=private-u8&sex=male',steps=[
            dict(action='open'),dict(action='value',id='audience-sex',value='female'),dict(action='submit')])
        self.assertIn('private-022',view['cards'])
        self.assertNotIn('private-001',view['cards'])
        self.assertNotIn('本章该年龄或人群内容尚未系统整理',view['text'])

    def test_filtered_sources_and_print_do_not_list_exclusive_male_references(self):
        excluded = MALE
        female_sources={sid for e in self.data['entries'] if e['id'] not in excluded for sid in e['source_ids']}
        priapism_only=set(self.by_id['private-036']['source_ids'])-female_sources
        self.assertTrue(priapism_only, 'The regression needs at least one exclusively male source')
        source_lookup={s['id']:s for s in self.data['sources']}
        source_view=self.render('#/sources?sex=female')
        printed=self.render('#/print?sex=female')
        for sid in priapism_only:
            self.assertNotIn(source_lookup[sid]['citation'],source_view['text'])
            self.assertNotIn(source_lookup[sid]['citation'],printed['text'])
        for eid in ('private-001','private-036'):
            self.assertNotIn(self.by_id[eid]['title'],printed['text'])
        self.assertIn(self.by_id['private-022']['title'],printed['text'])


if __name__=='__main__':
    unittest.main()
