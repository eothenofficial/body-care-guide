"""Cards show edited summaries without flattening the detailed article tables."""
from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from test_internal_links import NODE_READER, reader_fixture

ROOT = Path(__file__).resolve().parents[1]
TABLE = "| 场景 | 选择 |\n| --- | --- |\n| 正文表格标记 | 详细方案 |"

# Run the actual complete reader against the shared tiny DOM. The extra query
# method is used by list filters; card extraction does not parse HTML strings.
NODE_CARDS = NODE_READER.split("process.stdout.write(", 1)[0].replace(
    "hash:'#/entry/eyes-001'", "hash:input.hash"
).replace(
    "const elements=new Map();",
    "N.prototype.querySelectorAll=function(){return [];};\nconst elements=new Map();"
).replace(
    "localStorage:{getItem:()=>null}",
    "localStorage:{getItem:()=>JSON.stringify(input.saved||[])}"
) + r"""
process.stdout.write(JSON.stringify({
  cards:nodes.filter(n=>n.className==='entry-card').map(n=>({
    id:n.attrs['data-entry'],
    summaries:n.children.filter(c=>c.className==='entry-summary').map(c=>c.textContent),
    text:n.textContent
  })),
  tableCount:nodes.filter(n=>n.tag==='table').length,
  imageCount:nodes.filter(n=>n.tag==='img').length,
  text:doc.getElementById('main').textContent
}));
"""


@unittest.skipUnless(shutil.which("node"), "Node.js is needed to execute the actual reader")
class CardSummaryTests(unittest.TestCase):
    def render(self, entries, route="#/chapter/eyes", protocol="https:"):
        data = reader_fixture()
        data["entries"] = entries
        result = subprocess.run(
            [shutil.which("node"), "-e", NODE_CARDS],
            input=json.dumps({"data": data, "hash": route,
                              "saved": [e["id"] for e in entries],
                              "protocol": protocol,
                              "pathname": "/guide-offline.html" if protocol == "file:" else "/index.html",
                              "app": (ROOT / "web/app.js").read_text(encoding="utf-8")}),
            text=True, encoding="utf-8", capture_output=True, check=True,
        )
        return json.loads(result.stdout)

    def entry(self, summary=None, plain=None):
        entry = reader_fixture()["entries"][0]
        entry["fields"]["plain"] = plain or "正文首段，只在没有摘要的旧条目中回退。\n\n" + TABLE + "\n\n完整正文尾段标记。"
        if summary is not None:
            entry["summary"] = summary
        return entry

    def test_edited_summary_is_used_on_chapter_search_and_saved_cards_online_and_offline(self):
        summary = "先按使用场景选方案，再比较日常护理和复查的投入。具体适用条件放在点开后的正文。"
        entry = self.entry(summary=summary)
        for protocol in ("https:", "file:"):
            for route in ("#/chapter/eyes", "#/read", "#/saved"):
                with self.subTest(protocol=protocol, route=route):
                    view = self.render([entry], route, protocol)
                    self.assertEqual(view["cards"][0]["summaries"], [summary])
                    self.assertNotIn("正文表格标记", view["cards"][0]["text"])
                    self.assertNotIn("完整正文尾段标记", view["cards"][0]["text"])
                    self.assertNotIn("|", view["cards"][0]["text"])
                    self.assertEqual(view["tableCount"], 0)

    def test_legacy_fallback_uses_one_plain_paragraph_and_omits_citations(self):
        entry = self.entry(plain="**起步动作**见[详细说明](#/entry/eyes-002)。[@src-000000000001]\n\n" + TABLE + "\n\n尾段不应出现在卡片。")
        view = self.render([entry])
        self.assertEqual(view["cards"][0]["summaries"], ["起步动作见详细说明。"])
        self.assertNotIn("尾段不应", view["cards"][0]["text"])

    def test_table_first_legacy_article_skips_to_first_prose_paragraph(self):
        entry = self.entry(plain="## 章节提示\n\n" + TABLE + "\n\n可读首段。\n\n后面的详细内容。")
        self.assertEqual(self.render([entry])["cards"][0]["summaries"], ["可读首段。"])

    def test_long_fallback_is_bounded_before_css_and_does_not_split_surrogate_pairs(self):
        first_sentence = "先保留这项完整建议。"
        entry = self.entry(plain=first_sentence * 40 + "正文末尾不可泄漏。")
        summary = self.render([entry])["cards"][0]["summaries"][0]
        self.assertLessEqual(len(summary), 220)
        self.assertTrue(summary.endswith("。"))
        self.assertNotIn("正文末尾", summary)
        emoji_entry = self.entry(plain="🙂" * 250)
        emoji_summary = self.render([emoji_entry])["cards"][0]["summaries"][0]
        self.assertEqual(emoji_summary, "🙂" * 220 + "…")

    def test_summary_markup_is_inert_and_full_article_remains_unchanged(self):
        entry = self.entry(summary='<img src=x onerror="alert(1)">摘要。')
        card = self.render([entry])
        self.assertEqual(card["imageCount"], 0)
        self.assertIn("<img", card["cards"][0]["summaries"][0])
        detail = self.render([entry], "#/entry/eyes-001")
        self.assertEqual(detail["tableCount"], 1)
        self.assertIn("正文表格标记", detail["text"])
        self.assertIn("完整正文尾段标记", detail["text"])
        self.assertNotIn("<img", detail["text"])

    def test_search_includes_edited_summary_without_dropping_full_text_search(self):
        entry = self.entry(summary="独立摘要独有词。")
        self.assertEqual(len(self.render([entry], "#/read?q=独有词")["cards"]), 1)
        self.assertEqual(len(self.render([entry], "#/read?q=完整正文尾段标记")["cards"]), 1)


if __name__ == "__main__":
    unittest.main()
