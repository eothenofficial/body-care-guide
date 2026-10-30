"""Reader/static crosslinks must name real entries without widening URL access."""
from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

from scripts.static_pages import render_entry_html

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "src-000000000001"
LINK_PROSE = (
    "[有效](#/entry/eyes-002) [缺失](#/entry/eyes-999) "
    "[多余路径](#/entry/eyes-002/extra) [查询](#/entry/eyes-002?x=1) "
    "[编码](#/entry/%65yes-002) [其他页面](#/chapter/eyes) "
    "[危险](javascript:alert(1)) [数据](data:text/html,bad) "
    "[文件](file:///secret) [空白网址](https://example.org/ bad) "
    "[网页](https://example.org/?a=1&b=2) "
    f"[@{SOURCE}]"
)


def reader_fixture():
    fields = dict.fromkeys(("cost", "plain", "benefit", "evidence", "sources", "notes"), "示例")
    fields["plain"] = LINK_PROSE
    entries = [
        {"id": identifier, "chapter_id": "eyes", "unit_id": "eyes-u1", "ordinal": i,
         "title": "测试条目", "content_checked_at": "2026-10-29", "fields": fields.copy(),
         "evidence_labels": [], "source_ids": [SOURCE], "tags": []}
        for i, identifier in enumerate(("eyes-001", "eyes-002"), 1)
    ]
    return {
        "manifest": {"title": "测试指南", "content_version": "test", "site_url": ""},
        "entries": entries,
        "chapters": [{"id": "eyes", "title": "眼睛", "units": [
            {"id": "eyes-u1", "title": "示例单元", "entry_ids": [e["id"] for e in entries]}
        ]}],
        "sources": [{"id": SOURCE, "number": 1, "citation": "Test source.",
                     "url": "https://example.org/source"}],
    }


class LinkFacts(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.links = []
        self.current = None
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current = {"attrs": dict(attrs), "label": ""}
            self.links.append(self.current)

    def handle_endtag(self, tag):
        if tag == "a":
            self.current = None

    def handle_data(self, text):
        if self.current is not None:
            self.current["label"] += text


# A tiny DOM supplies browser primitives while the complete production reader
# renders its actual entry view. It does not duplicate link-parsing rules.
NODE_READER = r"""
const fs = require('node:fs'), vm = require('node:vm');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
class N {
  constructor(tag='', text='') { this.tag=tag;this.text=text;this.children=[];this.attrs={};this.dataset={};this.open=false;this.classList={remove(){},toggle(){return false;}}; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children=[...items];this.text=''; }
  setAttribute(key,value) { this.attrs[key]=String(value); }
  addEventListener() {}
  set textContent(value) { this.text=String(value);this.children=[]; }
  get textContent() { return this.text+this.children.map(n=>n.textContent).join(''); }
}
const elements=new Map();
const doc={
  getElementById(id){if(!elements.has(id))elements.set(id,new N('div'));return elements.get(id);},
  createElement:tag=>new N(tag),createElementNS:(_,tag)=>new N(tag),
  createTextNode:text=>new N('',String(text)),createDocumentFragment:()=>new N(),
  querySelector:()=>new N(),querySelectorAll:()=>[],addEventListener(){},body:new N('body')
};
const window={__GUIDE_DATA__:input.data,addEventListener(){},scrollTo(){}};
const location={protocol:input.protocol,pathname:input.pathname,hash:'#/entry/eyes-001'};
vm.runInNewContext(input.app, {window,document:doc,location,Node:N,URL,URLSearchParams,
  localStorage:{getItem:()=>null},history:{replaceState(){}},setTimeout,clearTimeout});
const nodes=[];
function walk(n){nodes.push(n);n.children.forEach(walk);}
walk(doc.getElementById('main'));
process.stdout.write(JSON.stringify({
  links:nodes.filter(n=>n.tag==='a').map(n=>({attrs:n.attrs,label:n.textContent})),
  citations:nodes.filter(n=>n.tag==='button'&&n.className==='citation').length,
  text:doc.getElementById('main').textContent
}));
"""


class InternalLinkTests(unittest.TestCase):
    def assert_only_supported_prose_links(self, links, expected_internal):
        by_label = {item["label"]: item["attrs"] for item in links}
        self.assertEqual(by_label["有效"]["href"], expected_internal)
        self.assertNotIn("target", by_label["有效"])
        self.assertEqual(by_label["网页"]["href"], "https://example.org/?a=1&b=2")
        self.assertEqual(by_label["网页"]["target"], "_blank")
        self.assertEqual(by_label["网页"]["rel"], "noopener noreferrer")
        for label in ("缺失", "多余路径", "查询", "编码", "其他页面", "危险", "数据", "文件", "空白网址"):
            self.assertNotIn(label, by_label)

    def test_static_crosslinks_resolve_under_subpaths_and_file_urls(self):
        data = reader_fixture()
        markup = render_entry_html(data, data["entries"][0])
        links = LinkFacts(markup).links
        target = "../../index.html#/entry/eyes-002"
        self.assert_only_supported_prose_links(links, target)
        self.assertEqual(urljoin("https://example.org/body-care-guide/read/eyes-001/", target),
                         "https://example.org/body-care-guide/index.html#/entry/eyes-002")
        self.assertEqual(urljoin("file:///C:/guide/read/eyes-001/index.html", target),
                         "file:///C:/guide/index.html#/entry/eyes-002")
        self.assertIn(f'href="#ref-{SOURCE}"', markup)
        self.assertIn("[缺失](#/entry/eyes-999)", markup)

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed to execute the actual reader")
    def test_browser_reader_keeps_valid_crosslinks_local_online_and_offline(self):
        for protocol, pathname in (("https:", "/body-care-guide/index.html"),
                                   ("file:", "/C:/guide/guide-offline.html")):
            with self.subTest(protocol=protocol):
                result = subprocess.run(
                    [shutil.which("node"), "-e", NODE_READER],
                    input=json.dumps({"data": reader_fixture(), "protocol": protocol,
                                      "pathname": pathname,
                                      "app": (ROOT / "web/app.js").read_text(encoding="utf-8")}),
                    text=True, encoding="utf-8", capture_output=True, check=True,
                )
                rendered = json.loads(result.stdout)
                self.assert_only_supported_prose_links(rendered["links"], "#/entry/eyes-002")
                self.assertEqual(rendered["citations"], 1)
                self.assertIn("[缺失](#/entry/eyes-999)", rendered["text"])


if __name__ == "__main__":
    unittest.main()
