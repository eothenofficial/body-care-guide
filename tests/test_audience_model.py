"""Readership metadata must survive exports without becoming medical eligibility."""
import copy
import unittest

from scripts.build import book_markdown, pack_data
from scripts.content_model import ContentError, validate_audience, validate_content
from scripts.static_pages import render_entry_html
from test_content import fixture, install_fixture, migrate, workspace_temp


class AudienceModelTests(unittest.TestCase):
    def audience(self):
        return dict(age_groups=['child', 'teen'], sexes=['all'],
                    scope_note='供学生和照护者阅读，具体方案仍需按检查判断。', safety_pin=False)

    def test_rejects_unknown_empty_duplicate_or_ambiguous_metadata(self):
        for replacement in [dict(age_groups=[]), dict(age_groups=['baby']),
                            dict(age_groups=['child', 'child']), dict(sexes=['all', 'male']),
                            dict(sexes=['woman']), dict(safety_pin=1),
                            dict(scope_note='参见[@src-123456789abc]')]:
            with self.subTest(replacement=replacement):
                a = self.audience()
                a.update(replacement)
                with self.assertRaises(ContentError):
                    validate_audience(dict(id='eyes-001', audience=a))

    def test_old_content_is_compatible_but_new_schema_requires_every_entry(self):
        text, sources, audits = fixture()
        book, chapters, sources, registry, _ = migrate(text, sources, audits)
        validate_content(book, chapters, sources, registry)
        book['audience_schema_version'] = '1.0.0'
        with self.assertRaisesRegex(ContentError, 'audience'):
            validate_content(book, chapters, sources, registry)
        for chapter in chapters:
            for entry in chapter['entries']:
                entry['audience'] = self.audience()
        validate_content(book, chapters, sources, registry)

    def test_readership_survives_json_markdown_and_non_javascript_share_page(self):
        text, sources, audits = fixture()
        result = migrate(text, sources, audits)
        result[0]['audience_schema_version'] = '1.0.0'
        for chapter in result[1]:
            for entry in chapter['entries']:
                entry['audience'] = self.audience()
        with workspace_temp() as root:
            install_fixture(root, result)
            data = pack_data(root)
            entry = data['entries'][0]
            self.assertEqual(entry['audience'], self.audience())
            self.assertEqual(data['manifest']['audience_schema_version'], '1.0.0')
            for rendered in [book_markdown(data), render_entry_html(data, entry)]:
                self.assertIn('儿童（0–11岁）', rendered)
                self.assertIn(self.audience()['scope_note'], rendered)
                self.assertIn('不代表治疗资格', rendered)

    def test_safety_preservation_is_explicit_not_inferred_from_gender_or_keywords(self):
        entry = dict(id='oral-001', title='急诊与女性只是合成测试文字', audience=self.audience())
        original = copy.deepcopy(entry)
        validate_audience(entry)
        self.assertEqual(entry, original)
        self.assertFalse(entry['audience']['safety_pin'])


if __name__ == '__main__':
    unittest.main()
