"""No-information notes can be omitted without weakening required evidence fields."""
import unittest
import test_card_summaries as reader_support
from scripts.build import book_markdown, pack_data
from scripts.content_model import ContentError, validate_content
from scripts.static_pages import render_entry_html
from test_content import fixture, install_fixture, migrate, workspace_temp


class OptionalNotesTests(unittest.TestCase):
    def test_empty_notes_are_allowed_but_action_and_evidence_remain_required(self):
        text, sources, audits = fixture()
        book, chapters, sources, registry, _ = migrate(text, sources, audits)
        entry = chapters[0]['entries'][0]
        entry['fields']['sources'] += '\n' + entry['fields']['notes']
        entry['fields']['notes'] = ''
        validate_content(book, chapters, sources, registry)
        entry['fields']['evidence'] = ''
        with self.assertRaisesRegex(ContentError, 'six fields'):
            validate_content(book, chapters, sources, registry)

    def test_exports_retain_empty_key_and_skip_meaningless_notes_heading(self):
        text, sources, audits = fixture()
        result = migrate(text, sources, audits)
        for chapter in result[1]:
            for entry in chapter['entries']:
                entry['fields']['sources'] += '\n' + entry['fields']['notes']
                entry['fields']['notes'] = ''
        with workspace_temp() as root:
            install_fixture(root, result)
            data = pack_data(root)
            self.assertEqual(data['entries'][0]['fields']['notes'], '')
            self.assertNotIn('id="field-notes"', render_entry_html(data, data['entries'][0]))
            self.assertNotIn('**备注：**', book_markdown(data))
        harness = reader_support.CardSummaryTests()
        entry = harness.entry()
        entry['fields']['notes'] = ''
        self.assertNotIn('备注', harness.render([entry], route='#/entry/eyes-001')['text'])


if __name__ == '__main__': unittest.main()
