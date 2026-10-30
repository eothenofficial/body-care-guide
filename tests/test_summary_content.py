"""The optional list synopsis must survive export without becoming body markup."""
import copy
import json
import unittest

from scripts.build import build, pack_data
from scripts.content_model import ContentError, load_content, validate_content
from test_content import fixture, install_fixture, migrate, workspace_temp


class SummaryContentTests(unittest.TestCase):
    def data(self):
        text, sources, audits = fixture()
        return migrate(text, sources, audits)

    def test_old_content_remains_valid_without_summary(self):
        book, chapters, sources, registry, _ = self.data()
        validate_content(book, chapters, sources, registry)
        self.assertNotIn('summary', chapters[0]['entries'][0])

    def test_optional_summary_is_preserved_in_api_and_offline_export(self):
        result = self.data()
        entry = result[1][0]['entries'][0]
        entry['summary'] = '这是单独编辑的列表摘要，完整说明仍留在正文。'
        with workspace_temp() as root:
            install_fixture(root, result)
            build(root=root)
            api = json.loads((root/'dist/api/v1/entries.json').read_text(encoding='utf-8'))
            self.assertEqual(api['entries'][0]['summary'], entry['summary'])
            offline = (root/'dist/downloads/guide-offline.html').read_text(encoding='utf-8')
            self.assertIn(entry['summary'], offline)
            self.assertEqual(load_content(root)[1][0]['entries'][0]['fields'], entry['fields'])

    def test_body_markup_or_non_text_cannot_be_pasted_as_summary(self):
        result = self.data()
        for invalid in [None, [], '', '两段\n\n正文', '| 项目 | 结果 |',
                        '**正文标题**', '引用[1]', '[链接](https://example.org)']:
            book, chapters, sources, registry, _ = copy.deepcopy(result)
            chapters[0]['entries'][0]['summary'] = invalid
            with self.subTest(summary=invalid), self.assertRaisesRegex(ContentError, 'Summary'):
                validate_content(book, chapters, sources, registry)


if __name__ == '__main__':
    unittest.main()
