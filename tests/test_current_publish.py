"""Acceptance contracts for the approved production release, built from a fresh stage."""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest
from xml.etree import ElementTree as ET

from scripts.build import build
from scripts.build_current import prepare
from test_audience_reader import NODE_AUDIENCE
from test_content import PageFacts, workspace_temp

ROOT = Path(__file__).resolve().parents[1]
TITLE = '少走弯路的人体保养指南'
SITE = 'https://eothenofficial.github.io/body-care-guide/'
PARAGRAPHS = [
    '我们从小认真学过怎么读书、怎么考试，却很少系统学过怎么照顾自己的身体。眼睛干涩、嘴唇起皮、口腔溃疡、肩腰酸痛、皮肤起疙瘩……这些不大不小的困扰，常常被一句“忍忍就好了”带过去。可到底该观察什么、怎么自护、什么时候需要就医，我们未必清楚。',
    '身体常识没学明白，保养的广告倒看了不少。叶黄素、护眼仪、蒸汽眼罩、漱口水……它们分别能解决什么问题，对谁有用，哪些可有可无？这份指南把日常不适、护理习惯和产品用途逐一查证，让你先弄清自己的需要，再决定怎么做、买不买。用更少的试错，把身体照顾好，少受罪，也少花冤枉钱。',
]
ALIASES = {
    'eyes-015': 'eyes-007', 'lips-002': 'lips-001', 'oral-006': 'oral-005',
    'private-023': 'private-022', 'anal-008': 'anal-007',
    'private-043': 'private-042', 'basics-004': 'nutrition-013',
    'basics-010': 'nutrition-020', 'sleep-013': 'sleep-012',
}


class CurrentPublishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This release must work in a clean checkout, without saved preview output.
        temporary = workspace_temp()
        cls.scratch = temporary.__enter__()
        cls.addClassCleanup(temporary.__exit__, None, None, None)
        cls.stage = cls.scratch / 'current'
        cls.config = prepare(cls.stage)
        build(root=cls.stage, built_at='2026-10-30T00:00:00Z')
        cls.dist = cls.stage / 'dist'
        cls.data = json.loads((cls.dist / 'downloads/guide.json').read_text(encoding='utf-8'))

    def test_approved_release_and_home_text_survive_production_preparation(self):
        manifest = self.data['manifest']
        self.assertEqual(manifest['title'], TITLE)
        self.assertEqual(manifest['content_version'], '2026.10.30-8')
        self.assertEqual((manifest['entry_count'], manifest['chapter_count'], manifest['source_count']), (341, 29, 638))
        self.assertEqual((len(self.data['entries']), len(self.data['chapters']), len(self.data['sources'])), (341, 29, 638))
        self.assertEqual(manifest['entry_aliases'], ALIASES)
        self.assertEqual(manifest['home_content']['lead'], '\n\n'.join(PARAGRAPHS))
        self.assertEqual(manifest['home_content']['headline'] + manifest['home_content']['headline_end'], '从头到脚，学会照顾自己。')
        self.assertEqual(manifest['book']['title'], TITLE)
        self.assertIn('\n\n'.join(PARAGRAPHS), manifest['book']['front_matter'])
        self.assertEqual(manifest['clinical_review_status'], 'not_clinically_reviewed')
        self.assertTrue(all(e['clinical_review_status'] == 'not_clinically_reviewed' for e in self.data['entries']))

    def test_public_urls_and_all_old_shares_resolve_to_current_content(self):
        manifest = self.data['manifest']
        self.assertEqual(manifest['site_url'], SITE)
        self.assertEqual(manifest['repository_url'], 'https://github.com/eothenofficial/body-care-guide')
        self.assertNotIn('noindex', (self.dist / 'index.html').read_text(encoding='utf-8'))
        ids = {e['id'] for e in self.data['entries']}
        pages = {p.parent.name: p for p in (self.dist / 'read').glob('*/index.html')}
        self.assertEqual(set(pages), ids | set(ALIASES))
        self.assertEqual(len(pages), 350)
        for identifier, path in pages.items():
            with self.subTest(identifier=identifier):
                target = ALIASES.get(identifier, identifier)
                text = path.read_text(encoding='utf-8')
                tags = PageFacts(text).tags
                self.assertIn(('link', {'rel': 'canonical', 'href': SITE + 'read/' + target + '/'}), tags)
                self.assertIn('../../#/entry/' + target, text)
                self.assertNotIn('noindex', text)
                if identifier in ALIASES:
                    self.assertEqual(text, pages[target].read_text(encoding='utf-8'))
        sitemap = ET.fromstring((self.dist / 'sitemap.xml').read_text(encoding='utf-8'))
        urls = {node.text for node in sitemap.findall('{*}url/{*}loc')}
        self.assertEqual(urls, {SITE} | {SITE + 'read/' + identifier + '/' for identifier in ids})

    def test_api_offline_and_downloads_contain_the_same_current_book(self):
        manifest = self.data['manifest']
        self.assertEqual(json.loads((self.dist / 'api/v1/manifest.json').read_text(encoding='utf-8')), manifest)
        for key in ('entries', 'chapters', 'sources'):
            value = json.loads((self.dist / 'api/v1' / (key + '.json')).read_text(encoding='utf-8'))
            self.assertEqual(value[key], self.data[key])
            self.assertEqual(value['content_version'], '2026.10.30-8')
        offline = (self.dist / 'downloads/guide-offline.html').read_text(encoding='utf-8')
        payload = re.search(r'window\.__GUIDE_DATA__=(.*?);\n', offline, re.S)
        self.assertIsNotNone(payload)
        self.assertEqual(json.loads(payload.group(1)), self.data)
        markdown = (self.dist / 'downloads/guide.md').read_text(encoding='utf-8')
        self.assertIn('# ' + TITLE, markdown)
        self.assertIn('\n\n'.join(PARAGRAPHS), markdown)
        self.assertNotRegex(markdown, r'\[@src-[0-9a-f]{12}\]')
        for entry in self.data['entries']:
            self.assertIn('### ' + str(entry['ordinal']) + ' ' + entry['title'], markdown)
        self.assertEqual((self.stage / 'web/app.js').read_bytes(), (ROOT / 'web/app.js').read_bytes())

    @unittest.skipUnless(shutil.which('node'), 'Node runs the actual production reader')
    def test_reader_keeps_two_full_paragraphs_and_existing_online_bookmarks(self):
        harness = NODE_AUDIENCE.split('process.stdout.write(', 1)[0]
        harness = harness.replace('const elements=', 'const storageReads=[];const elements=', 1)
        harness = harness.replace('localStorage:{getItem:()=>null}', "localStorage:{getItem(key){storageReads.push(key);return key==='body-care-guide:bookmarks:v1'?JSON.stringify(input.saved||[]):null;},setItem(){}}")
        harness += "process.stdout.write(JSON.stringify({paragraphs:nodes.filter(n=>n.className==='hero-description').map(n=>n.textContent),cards:nodes.filter(n=>n.className==='entry-card').map(n=>n.attrs['data-entry']),saved:doc.getElementById('saved-count').textContent,storageReads}));"
        app = (self.dist / 'app.js').read_text(encoding='utf-8')
        for route in ('#/', '#/saved'):
            result = subprocess.run([shutil.which('node'), '-e', harness],
                input=json.dumps(dict(data=self.data, hash=route, saved=['eyes-015', 'eyes-007'], app=app)),
                text=True, encoding='utf-8', capture_output=True, check=True)
            view = json.loads(result.stdout)
            with self.subTest(route=route):
                self.assertIn('body-care-guide:bookmarks:v1', view['storageReads'])
                self.assertNotIn('body-care-guide:whole-body:bookmarks:v1', view['storageReads'])
                self.assertEqual(view['saved'], '1')
                if route == '#/':
                    self.assertEqual(view['paragraphs'], PARAGRAPHS)
                else:
                    self.assertEqual(view['cards'], ['eyes-007'])


if __name__ == '__main__':
    unittest.main()
