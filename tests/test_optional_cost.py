"""Unverified cost material can be omitted consistently in every reader export."""
import unittest
import test_card_summaries as cards_test_support

from scripts.build import book_markdown, pack_data
from scripts.content_model import ContentError, validate_content
from scripts.static_pages import render_entry_html
from test_content import fixture, install_fixture, migrate, workspace_temp


class OptionalCostTests(unittest.TestCase):
    def test_empty_cost_is_allowed_but_other_empty_fields_still_fail(self):
        text, sources, audits = fixture()
        book, chapters, sources, registry, _ = migrate(text, sources, audits)
        chapters[0]['entries'][0]['fields']['cost'] = ''
        validate_content(book, chapters, sources, registry)
        chapters[0]['entries'][0]['fields']['benefit'] = ''
        with self.assertRaisesRegex(ContentError, 'six fields'):
            validate_content(book, chapters, sources, registry)

    def test_markdown_and_static_share_page_do_not_show_empty_cost_heading(self):
        text, sources, audits = fixture()
        result = migrate(text, sources, audits)
        result[1][0]['entries'][0]['fields']['cost'] = ''
        with workspace_temp() as root:
            install_fixture(root, result)
            data = pack_data(root)
            entry = data['entries'][0]
            self.assertNotIn('id="field-cost"', render_entry_html(data, entry))
            self.assertIn('id="field-plain"', render_entry_html(data, entry))
            data['chapters'] = data['chapters'][:1]
            data['entries'] = data['entries'][:1]
            self.assertNotIn('**成本：**', book_markdown(data))

    def test_interactive_reader_keeps_other_fields_without_empty_cost_label(self):
        harness = cards_test_support.CardSummaryTests()
        entry = harness.entry(plain='具体正文，不显示空的费用段。')
        entry['fields']['cost'] = ''
        view = harness.render([entry], route='#/entry/eyes-001')
        self.assertNotIn('成本', view['text'])
        self.assertIn('具体正文', view['text'])
        self.assertIn('证据等级', view['text'])


if __name__ == '__main__':
    unittest.main()
