"""Reader release contracts: anatomy, public copy, references and stable links."""
import importlib.util
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from scripts.content_model import validate_content, STABLE_REF
from test_audience_reader import NODE_AUDIENCE

ROOT=Path(__file__).resolve().parents[1]
REV=ROOT/'drafts/whole-body/revision-20261030'


class ReleaseContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('release_contracts',REV/'build_release.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        cls.book,cls.chapters,cls.sources,cls.registry=module.make_data()
        cls.entries=[e for c in cls.chapters for e in c['entries']]

    def test_taxonomy_preserves_every_registered_entry_once_and_all_references(self):
        validate_content(self.book,self.chapters,self.sources,self.registry)
        original=json.loads((ROOT/'drafts/whole-body/compiled/master/build-report.json').read_text(encoding='utf-8'))
        self.assertEqual(len(self.entries),original['entries'])
        self.assertEqual(len(self.chapters),26)
        previous={e['id'] for p in (ROOT/'drafts/whole-body/compiled/master/chapters').glob('*.json')
                  for e in json.loads(p.read_text(encoding='utf-8'))['entries']}
        self.assertEqual(previous,{e['id'] for e in self.entries})
        self.assertEqual(len(self.entries),len(previous))
        known={s['id'] for s in self.sources}
        for e in self.entries:
            self.assertTrue(set(e['source_ids'])<=known)
            self.assertTrue(100<=len(e['summary'])<=180,e['id'])
            self.assertEqual(e['clinical_review_status'],'not_clinically_reviewed')
            self.assertIn(e['legacy_chapter_id'],['hair','eyes','nose','ears','oral','lips','skin','neck','chest','hands','abdomen','private','anal','legs','feet','bodyskin','basics'])

    def test_every_anatomical_chapter_has_a_defined_dedicated_icon_and_group(self):
        html=(ROOT/'web/index.html').read_text(encoding='utf-8')
        symbols=set(re.findall(r'<symbol id="i-([^\"]+)"',html))
        for c in self.chapters:
            with self.subTest(chapter=c['id']):
                self.assertTrue(c['body_group'])
                self.assertNotEqual(c['icon'],'book')
                self.assertIn(c['icon'],symbols)
        icons=[c['icon'] for c in self.chapters]
        self.assertEqual(len(icons),len(set(icons)))

    def test_public_copy_has_no_internal_deliverable_labels_or_phantom_figures(self):
        forbidden=re.compile(r'本地校对稿|校对稿|交付稿|初稿研究|出片|待用户确认|按用户要求|按本款图示|如图所示|见上图|点击下方视频')
        texts=[self.book['title'],self.book['front_matter'],self.book['back_matter']]
        for c in self.chapters:
            texts += [c['title'],c['subtitle'],c['intro']]
            texts += [u['title']+'\n'+u['intro'] for u in c['units']]
        for e in self.entries:texts += [e['title'],e['summary'],e['audience']['scope_note'],*e['fields'].values()]
        for s in self.sources:texts += [s.get(k,'') for k in ['support','limitations','reading_depth']]
        for text in texts:self.assertIsNone(forbidden.search(str(text)),str(text)[:180])
        self.assertNotIn('heroArt()', (ROOT/'web/app.js').read_text(encoding='utf-8'))

    def test_cup_disc_operations_identify_external_official_instructions(self):
        e=next(e for e in self.entries if e['id']=='private-022')
        self.assertIn('品牌官网',e['fields']['plain'])
        self.assertIn('说明书',e['fields']['plain'])
        self.assertNotIn('本款图示',e['fields']['plain'])

    @unittest.skipUnless(shutil.which('node'),'Node.js executes the actual reader')
    def test_old_group_url_resolves_split_parts_without_losing_entries(self):
        data=dict(manifest=dict(title=self.book['title'],chapter_aliases=self.book['chapter_aliases']),
                  chapters=[{k:v for k,v in c.items() if k!='entries'} for c in self.chapters],
                  entries=self.entries,sources=self.sources)
        result=subprocess.run([shutil.which('node'),'-e',NODE_AUDIENCE],input=json.dumps(dict(
            data=data,hash='#/chapter/hands',app=(ROOT/'web/app.js').read_text(encoding='utf-8'))),
            encoding='utf-8',text=True,capture_output=True,check=True)
        view=json.loads(result.stdout)
        self.assertIn('手部皮肤',view['text'])
        self.assertIn('手指甲',view['text'])
        self.assertEqual(len(view['cards']),12)
        self.assertIn('#/chapter/hand-skin',view['links'])
        self.assertIn('#/chapter/fingernails',view['links'])


if __name__=='__main__':unittest.main()
