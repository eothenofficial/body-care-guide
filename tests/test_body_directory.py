"""New body chapters are discoverable without adding per-part UI code."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

import test_card_summaries as support
from test_internal_links import reader_fixture

ROOT = Path(__file__).resolve().parents[1]
HARNESS = support.NODE_CARDS.split('process.stdout.write(', 1)[0] + r'''
const positionLinks=[];
function positionWalk(n){
  if(n.tag==='a')positionLinks.push({href:n.attrs.href,label:n.textContent});
  n.children.forEach(positionWalk);
}
const positionSection=nodes.find(n=>n.className==='body-position-map');
if(positionSection)positionWalk(positionSection);
process.stdout.write(JSON.stringify({
  documentTitle:doc.title,
  text:doc.getElementById('main').textContent,
  cards:nodes.filter(n=>n.className==='entry-card').map(n=>n.textContent),
  positionLinks,
  links:nodes.filter(n=>n.tag==='a').map(n=>({href:n.attrs.href,label:n.textContent}))
}));
'''


@unittest.skipUnless(shutil.which('node'), 'Node.js executes the actual reader')
class BodyDirectoryTests(unittest.TestCase):
    def data(self):
        data = reader_fixture()
        chapter = data['chapters'][0]
        chapter.update(id='abdomen', title='腹部与肚脐篇', summary='清洁与不适处理。')
        for entry in data['entries']:
            entry.update(chapter_id='abdomen', title='洗后轻轻吸干，不反复抠抓', summary='独立摘要。')
        return data

    def render(self, data, route):
        result = subprocess.run(
            [shutil.which('node'), '-e', HARNESS],
            input=json.dumps(dict(data=data, hash=route, protocol='file:',
                pathname='/guide-offline.html', app=(ROOT/'web/app.js').read_text(encoding='utf-8'))),
            text=True, encoding='utf-8', capture_output=True, check=True)
        return json.loads(result.stdout)

    def test_new_chapter_has_human_label_and_is_searchable_by_body_name(self):
        view = self.render(self.data(), '#/read?q=腹部')
        self.assertEqual(len(view['cards']), 2)
        self.assertTrue(all('腹部与肚脐篇' in text for text in view['cards']))
        self.assertNotIn('undefined', view['text'])

    def test_position_directory_orders_parts_and_does_not_link_unwritten_content(self):
        data = self.data()
        data['manifest']['body_layout'] = [
            dict(title='腹部与肚脐篇', chapters=[dict(id='abdomen', title='腹部与肚脐篇')]),
            dict(title='未来足部篇', chapters=[dict(id='feet', title='足部')])]
        view = self.render(data, '#/')
        self.assertLess(view['text'].index('腹部与肚脐篇'), view['text'].index('未来足部篇'))
        self.assertIn('内容准备中', view['text'])
        self.assertEqual(view['positionLinks'], [dict(href='#/chapter/abdomen', label='腹部与肚脐篇')])

    def test_legacy_book_without_body_layout_still_opens(self):
        view = self.render(reader_fixture(), '#/')
        self.assertIn('眼睛', view['text'])
        self.assertNotIn('按身体位置找篇目', view['text'])
        self.assertNotIn('null', view['text'])

    def test_chapter_title_does_not_repeat_care_or_append_to_part_name(self):
        self.assertEqual(self.render(self.data(), '#/chapter/abdomen')['documentTitle'],
                         '腹部与肚脐篇 · '+self.data()['manifest']['title'])

    def test_standalone_part_uses_its_own_search_examples(self):
        data = self.data()
        data['manifest']['search_examples'] = ['肚脐', '胀气']
        view = self.render(data, '#/')
        query_links = [link for link in view['links'] if link['href'].startswith('#/read?q=')]
        self.assertEqual([link['label'] for link in query_links], ['肚脐', '胀气'])
        self.assertNotIn('眼睛干涩', view['text'])


if __name__ == '__main__': unittest.main()
