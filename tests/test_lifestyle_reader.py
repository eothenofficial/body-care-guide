"""Exercise bookmark transfer and long-page navigation in the complete reader."""
from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

from test_audience_reader import NODE_AUDIENCE, reader_fixture

ROOT = Path(__file__).resolve().parents[1]

# Reuse the audience reader's DOM and download primitives; only browser storage,
# File reading, scrolling and async event delivery are added for these features.
NODE_LIFESTYLE = NODE_AUDIENCE.split("vm.runInNewContext(input.app", 1)[0] + r"""
const storageWrites=[],scrollCalls=[],snapshots=[];
let fileReads=0;
const localStorage={
  getItem(key){if(input.failStorageRead)throw new Error('Storage blocked');return key==='body-care-guide:bookmarks:v1'?JSON.stringify(input.saved||[]):null;},
  setItem(key,value){storageWrites.push({key,value});if(input.failStorageWrite)throw new Error('Quota exceeded');}
};
window.scrollY=0;
window.matchMedia=query=>({matches:!!input.reduceMotion,media:query});
window.scrollTo=options=>{scrollCalls.push({...options});window.scrollY=options.top||0;for(const fn of windowHandlers.get('scroll')||[])fn();};
N.prototype.emitAsync=async function(kind,extra={}){for(const fn of this.handlers.get(kind)||[])await fn({preventDefault(){},target:this,currentTarget:this,...extra});};
vm.runInNewContext(input.app,{window,document:doc,location,history,Node:N,URL:TestURL,URLSearchParams,Blob:TestBlob,localStorage,setTimeout:()=>0,clearTimeout(){}});
function snapshot(){snapshots.push({hidden:doc.getElementById('back-to-top').hidden,y:window.scrollY,hash:location.hash,focusedMain:doc.activeElement===doc.getElementById('main')});}
function mainButton(label){return walk(doc.getElementById('main')).find(n=>n.tag==='button'&&n.textContent===label);}
(async()=>{
  snapshot();
  for(const step of input.steps||[]){
    if(step.action==='export'){await mainButton('导出收藏').emitAsync('click');}
    else if(step.action==='import'){
      const picker=walk(doc.getElementById('main')).find(n=>n.tag==='input'&&n.attrs.type==='file');
      picker.files=[{size:step.size??Buffer.byteLength(step.text||''),text:async()=>{fileReads++;if(step.failRead)throw new Error('文件无法读取');return step.text;}}];
      await picker.emitAsync('change');
    }
    else if(step.action==='scroll'){window.scrollY=step.y;for(const fn of windowHandlers.get('scroll')||[])fn();snapshot();}
    else if(step.action==='top'){await doc.getElementById('back-to-top').emitAsync('click');snapshot();}
    else if(step.action==='route'){location.hash=step.hash;for(const fn of windowHandlers.get('hashchange')||[])fn();snapshot();}
  }
  process.stdout.write(JSON.stringify({downloads,storageWrites,fileReads,scrollCalls,snapshots,
    savedCount:Number(doc.getElementById('saved-count').textContent),
    cards:walk(doc.getElementById('main')).filter(n=>n.className==='entry-card').map(n=>n.attrs['data-entry']),
    toast:doc.getElementById('toast').textContent,hash:location.hash,
    focusMain:doc.activeElement===doc.getElementById('main')}));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1;});
"""


def bookmark_payload(ids, **overrides):
    return json.dumps(dict(kind="body-care-guide-bookmarks", schema_version="1.0.0",
                           entry_ids=ids, **overrides))


@unittest.skipUnless(shutil.which("node"), "Node.js executes the complete reader")
class LifestyleReaderTests(unittest.TestCase):
    def render(self, steps=None, route="#/saved", saved=None, **options):
        result = subprocess.run(
            [shutil.which("node"), "-e", NODE_LIFESTYLE],
            input=json.dumps(dict(data=reader_fixture(), hash=route,
                                  steps=steps or [], saved=saved or [],
                                  app=(ROOT / "web/app.js").read_text(encoding="utf-8"),
                                  **options)),
            text=True, encoding="utf-8", capture_output=True, check=True,
        )
        return json.loads(result.stdout)

    def test_bookmark_export_only_contains_format_and_all_saved_ids_without_reading_filters(self):
        view = self.render(route="#/saved?age=72&sex=female&q=隐私搜索词",
                           saved=["eyes-001", "eyes-002"], steps=[dict(action="export")])
        exported = json.loads(view["downloads"][0])
        self.assertEqual(exported, dict(kind="body-care-guide-bookmarks", schema_version="1.0.0",
                                        entry_ids=["eyes-001", "eyes-002"]))
        self.assertEqual(set(exported), {"kind", "schema_version", "entry_ids"})
        self.assertNotIn("隐私搜索词", view["downloads"][0])
        self.assertNotIn("female", view["downloads"][0])
        self.assertNotIn("72", view["downloads"][0])
        self.assertEqual(view["cards"], [])

    def test_import_merges_deduplicates_and_skips_unknown_ids_without_replacing_existing(self):
        view = self.render(saved=["eyes-001"], steps=[
            dict(action="import", text=bookmark_payload(["eyes-002", "eyes-002", "eyes-999", "eyes-999"])),
            dict(action="export"),
        ])
        self.assertEqual(view["savedCount"], 2)
        self.assertEqual(json.loads(view["downloads"][0])["entry_ids"], ["eyes-001", "eyes-002"])
        self.assertEqual(view["cards"], ["eyes-001", "eyes-002"])
        self.assertIn("合并了 1 条新收藏", view["toast"])
        self.assertIn("跳过 1 条本版本未收录", view["toast"])
        self.assertEqual(json.loads(view["storageWrites"][0]["value"]), ["eyes-001", "eyes-002"])

    def test_invalid_import_never_partially_changes_existing_bookmarks(self):
        invalid = ["not json", "null", "[]",
                   json.dumps(dict(kind="unrelated", schema_version="1.0.0", entry_ids=["eyes-002"])),
                   json.dumps(dict(kind="body-care-guide-bookmarks", schema_version="9", entry_ids=["eyes-002"])),
                   json.dumps(dict(kind="body-care-guide-bookmarks", schema_version="1.0.0", entry_ids="eyes-002")),
                   bookmark_payload(["eyes-002", "../../private"]), bookmark_payload(["eyes-002", 42]),
                   bookmark_payload(["eyes-002"] * 5001)]
        for text in invalid:
            with self.subTest(text=text[:80]):
                view = self.render(saved=["eyes-001"], steps=[dict(action="import", text=text), dict(action="export")])
                self.assertEqual(view["savedCount"], 1)
                self.assertEqual(json.loads(view["downloads"][0])["entry_ids"], ["eyes-001"])
                self.assertEqual(view["storageWrites"], [])
                self.assertIn("未导入：", view["toast"])

    def test_file_size_limit_is_checked_before_reading_and_exact_limit_is_allowed(self):
        text = bookmark_payload(["eyes-002"])
        rejected = self.render(saved=["eyes-001"], steps=[dict(action="import", text=text, size=1024 * 1024 + 1)])
        self.assertEqual(rejected["fileReads"], 0)
        self.assertEqual(rejected["savedCount"], 1)
        self.assertEqual(rejected["storageWrites"], [])
        self.assertIn("不能超过1MB", rejected["toast"])
        allowed = self.render(saved=["eyes-001"], steps=[dict(action="import", text=text, size=1024 * 1024)])
        self.assertEqual(allowed["fileReads"], 1)
        self.assertEqual(allowed["savedCount"], 2)

    def test_failed_storage_keeps_merged_session_bookmarks_and_explains_backup(self):
        view = self.render(saved=["eyes-001"], failStorageWrite=True, steps=[
            dict(action="import", text=bookmark_payload(["eyes-002"])), dict(action="export"),
        ])
        self.assertEqual(view["savedCount"], 2)
        self.assertEqual(json.loads(view["downloads"][0])["entry_ids"], ["eyes-001", "eyes-002"])
        self.assertEqual(len(view["storageWrites"]), 1)
        self.assertIn("只能暂存", view["toast"])
        self.assertIn("请导出备份", view["toast"])

    def test_unreadable_file_preserves_saved_bookmarks(self):
        view = self.render(saved=["eyes-001"], steps=[dict(action="import", text="", failRead=True)])
        self.assertEqual(view["savedCount"], 1)
        self.assertEqual(view["storageWrites"], [])
        self.assertIn("未导入：文件无法读取", view["toast"])

    def test_back_to_top_threshold_is_480_and_route_render_resets_it(self):
        route = "#/entry/eyes-001?age=72&sex=female"
        next_route = "#/entry/eyes-002?age=72&sex=female"
        view = self.render(route=route, steps=[dict(action="scroll", y=479),
            dict(action="scroll", y=480), dict(action="scroll", y=900),
            dict(action="route", hash=next_route)])
        self.assertEqual([s["hidden"] for s in view["snapshots"]], [True, True, False, False, True])
        self.assertEqual(view["snapshots"][-1]["y"], 0)
        self.assertEqual(view["hash"], next_route)
        self.assertEqual(view["scrollCalls"][-1], dict(top=0, behavior="instant"))

    def test_back_to_top_honors_reduced_motion_and_preserves_hash_filters_and_main_focus(self):
        route = "#/entry/eyes-001?age=72&sex=female"
        for reduced, behavior in [(False, "smooth"), (True, "instant")]:
            with self.subTest(reduced=reduced):
                view = self.render(route=route, reduceMotion=reduced,
                                   steps=[dict(action="scroll", y=800), dict(action="top")])
                self.assertEqual(view["scrollCalls"][-1], dict(top=0, behavior=behavior))
                self.assertEqual(view["hash"], route)
                self.assertTrue(view["focusMain"])
                self.assertEqual(view["snapshots"][-1]["y"], 0)
                self.assertTrue(view["snapshots"][-1]["hidden"])


class Element:
    def __init__(self, tag, attrs, parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children = []

    def ancestors(self):
        current = self.parent
        while current is not None:
            yield current
            current = current.parent


class NavigationFacts(HTMLParser):
    void = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, html):
        super().__init__()
        self.root, self.nodes = Element("root", []), []
        self.stack = [self.root]
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        element = Element(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(element)
        self.nodes.append(element)
        if tag not in self.void:
            self.stack.append(element)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.void:
            self.handle_endtag(tag)


class LifestyleNavigationStructureTests(unittest.TestCase):
    def test_saved_is_in_quick_navigation_outside_independent_chapter_scroll_region(self):
        facts = NavigationFacts((ROOT / "web/index.html").read_text(encoding="utf-8"))
        quick = next(n for n in facts.nodes if "nav-quick" in n.attrs.get("class", "").split())
        scroll = next(n for n in facts.nodes if "chapter-nav-scroll" in n.attrs.get("class", "").split())
        saved = next(n for n in facts.nodes if n.tag == "a" and n.attrs.get("data-nav") == "saved")
        chapters = next(n for n in facts.nodes if n.attrs.get("id") == "chapter-nav")
        self.assertIn(quick, list(saved.ancestors()))
        self.assertNotIn(scroll, list(saved.ancestors()))
        self.assertIn(scroll, list(chapters.ancestors()))
        self.assertIs(quick.parent, scroll.parent)
        self.assertLess(quick.parent.children.index(quick), quick.parent.children.index(scroll))

    def test_back_to_top_is_a_hidden_accessible_button_outside_scrollable_chapter_navigation(self):
        facts = NavigationFacts((ROOT / "web/index.html").read_text(encoding="utf-8"))
        button = next(n for n in facts.nodes if n.attrs.get("id") == "back-to-top")
        self.assertEqual(button.tag, "button")
        self.assertEqual(button.attrs.get("type"), "button")
        self.assertEqual(button.attrs.get("aria-label"), "回到页面顶部")
        self.assertIn("hidden", button.attrs)
        self.assertFalse(any("chapter-nav-scroll" in n.attrs.get("class", "").split() for n in button.ancestors()))


if __name__ == "__main__":
    unittest.main()
