"""Static comparison tables keep the existing safe prose and citation rules."""
from __future__ import annotations

import unittest
from html.parser import HTMLParser

from scripts.content_model import ContentError
from scripts.static_pages import render_prose


SOURCE = "src-0123456789ab"
SOURCES = {SOURCE: {"number": 7}}
ENTRY_IDS = {"eyes-001", "eyes-002"}


class TableFacts(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.tags = []
        self.data = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.data.append(data)


class StaticTableTests(unittest.TestCase):
    def test_valid_comparison_table_with_alignment_and_surrounding_prose(self):
        text = ("前言\n\n| 方案 | 投入 | 频次 |\n"
                "| :--- | ---: | :---: |\n"
                "| 方案甲 | 低 | 偶尔 |\n| 方案乙 | 高 | 经常 |\n\n后文")
        markup = render_prose(text, SOURCES, ENTRY_IDS)
        facts = TableFacts(markup)
        tags = [tag for tag, _ in facts.tags]
        self.assertEqual(tags.count("table"), 1)
        self.assertEqual(tags.count("thead"), 1)
        self.assertEqual(tags.count("tbody"), 1)
        self.assertEqual(tags.count("th"), 3)
        self.assertEqual(tags.count("td"), 6)
        self.assertEqual(tags.count("p"), 2)
        headers = [attrs for tag, attrs in facts.tags if tag == "th"]
        self.assertEqual([h["scope"] for h in headers], ["col"] * 3)
        self.assertEqual([h["style"] for h in headers],
                         ["text-align:left", "text-align:right", "text-align:center"])
        self.assertIn('class="table-wrap"', markup)
        self.assertIn("<p>前言</p>", markup)
        self.assertIn("<p>后文</p>", markup)

    def test_optional_outer_pipes_and_escaped_inner_pipe(self):
        markup = render_prose("项目 | 解释\n--- | ---\n甲\\|乙 | 值", SOURCES, ENTRY_IDS)
        facts = TableFacts(markup)
        self.assertEqual(sum(tag == "td" for tag, _ in facts.tags), 2)
        self.assertIn("甲|乙", facts.data)

    def test_table_cells_keep_citations_known_local_links_and_safe_external_links(self):
        text = ("| 来源 | 更多 |\n| --- | --- |\n"
                f"| **依据** [@{SOURCE}] | [本地](#/entry/eyes-002) "
                "[外部](https://example.org/?a=1&b=2) |")
        markup = render_prose(text, SOURCES, ENTRY_IDS)
        facts = TableFacts(markup)
        links = [attrs for tag, attrs in facts.tags if tag == "a"]
        self.assertTrue(any(link.get("href") == "#ref-" + SOURCE for link in links))
        local = next(link for link in links if "index.html" in link.get("href", ""))
        self.assertEqual(local["href"], "../../index.html#/entry/eyes-002")
        self.assertNotIn("target", local)
        external = next(link for link in links if link.get("href", "").startswith("https:"))
        self.assertEqual(external["href"], "https://example.org/?a=1&b=2")
        self.assertEqual(external["target"], "_blank")
        self.assertEqual(external["rel"], "noopener noreferrer")
        self.assertIn("<strong>依据</strong>", markup)

    def test_raw_html_and_dangerous_table_links_remain_inert_text(self):
        text = ('| <img src=x onerror="alert(1)"> | 操作 |\n| --- | --- |\n'
                '| <script>alert(2)</script> | [脚本](javascript:alert(3)) '
                '[数据](data:text/html,bad) [文件](file:///secret) '
                '[相对](//example.org) [缺失](#/entry/eyes-999) |')
        markup = render_prose(text, SOURCES, ENTRY_IDS)
        facts = TableFacts(markup)
        self.assertFalse({"script", "img", "svg", "a"} & {tag for tag, _ in facts.tags})
        self.assertIn('&lt;img src=x onerror=&quot;alert(1)&quot;&gt;', markup)
        self.assertIn("&lt;script&gt;alert(2)&lt;/script&gt;", markup)
        self.assertIn("[缺失](#/entry/eyes-999)", "".join(facts.data))

    def test_invalid_header_separator_does_not_create_a_table(self):
        cases = ["| 一 | 二 |\n| --- |\n| 甲 | 乙 |",
                 '| 一 | 二 |\n| --- onmouseover="bad" | --- |\n| 甲 | 乙 |',
                 "普通段落\n---\n下一行"]
        for text in cases:
            with self.subTest(text=text):
                markup = render_prose(text, SOURCES, ENTRY_IDS)
                self.assertNotIn("<table>", markup)
                self.assertTrue(markup.startswith("<p>"))

    def test_malformed_body_row_is_preserved_instead_of_silently_truncated(self):
        markup = render_prose("| 一 | 二 |\n| --- | --- |\n| 甲 | 乙 | 多余 |", SOURCES, ENTRY_IDS)
        self.assertIn("<table>", markup)
        self.assertIn("<p>| 甲 | 乙 | 多余 |</p>", markup)

    def test_unknown_citation_in_a_table_still_fails(self):
        with self.assertRaisesRegex(ContentError, "unknown source"):
            render_prose("| 来源 | 解释 |\n| --- | --- |\n| [@src-000000000000] | 值 |",
                         SOURCES, ENTRY_IDS)

    def test_ordinary_paragraphs_lists_and_inline_safety_are_unchanged(self):
        markup = render_prose(f"首段 **加粗** [@{SOURCE}]\n下一行\n\n[坏](javascript:bad)",
                              SOURCES, ENTRY_IDS)
        self.assertIn("<strong>加粗</strong>", markup)
        self.assertIn("<br>\n下一行", markup)
        self.assertIn('href="#ref-' + SOURCE + '"', markup)
        self.assertIn("<p>[坏](javascript:bad)</p>", markup)
        self.assertEqual(render_prose(["甲", "乙"], SOURCES), "<p>甲；乙</p>")
        self.assertEqual(render_prose(None, SOURCES), "")


if __name__ == "__main__":
    unittest.main()
