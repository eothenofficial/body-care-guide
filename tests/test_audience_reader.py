"""Execute the actual reader to verify demographic navigation and safety scope."""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from test_internal_links import reader_fixture

ROOT = Path(__file__).resolve().parents[1]

NODE_AUDIENCE = r"""
const fs=require('node:fs'),vm=require('node:vm'),input=JSON.parse(fs.readFileSync(0,'utf8'));
const elements=new Map(),documentHandlers=new Map(),windowHandlers=new Map(),downloads=[];
let doc;
class N {
  constructor(tag='',text=''){this.tag=tag;this.text=text;this.children=[];this.attrs={};this.dataset={};this.handlers=new Map();this.open=false;this.value='';this.isConnected=true;this.classList={remove:()=>{},toggle:()=>false};}
  append(...items){this.children.push(...items);}
  replaceChildren(...items){this.children=[...items];this.text='';}
  setAttribute(k,v){this.attrs[k]=String(v);if(k==='id')elements.set(String(v),this);if(k.startsWith('data-'))this.dataset[k.slice(5)]=String(v);}
  getAttribute(k){return this.attrs[k]??null;}
  removeAttribute(k){delete this.attrs[k];}
  addEventListener(k,fn){if(!this.handlers.has(k))this.handlers.set(k,[]);this.handlers.get(k).push(fn);}
  emit(k,extra={}){for(const fn of this.handlers.get(k)||[])fn({preventDefault(){},target:this,currentTarget:this,...extra});}
  set textContent(v){this.text=String(v);this.children=[];}
  get textContent(){return this.text+this.children.map(n=>n.textContent).join('');}
  querySelectorAll(selector){const all=[];walk(this,all);return selector==='[data-value]'?all.filter(n=>'data-value'in n.attrs):[];}
  showModal(){this.open=true;}
  close(){this.open=false;this.emit('close');}
  focus(){doc.activeElement=this;}
  click(){this.emit('click');}
  remove(){}
}
function walk(n,result=[]){result.push(n);for(const child of n.children)walk(child,result);return result;}
doc={getElementById(id){if(!elements.has(id))elements.set(id,new N('div'));return elements.get(id);},createElement:tag=>new N(tag),createElementNS:(_,tag)=>new N(tag),createTextNode:text=>new N('',String(text)),createDocumentFragment:()=>new N(),querySelector:()=>new N(),querySelectorAll(selector){return selector==='#sidebar a[href^="#/"]'?walk(this.getElementById('sidebar')).filter(n=>n.tag==='a'&&(n.getAttribute('href')||'').startsWith('#/')):[];},addEventListener(k,fn){if(!documentHandlers.has(k))documentHandlers.set(k,[]);documentHandlers.get(k).push(fn);},body:new N('body'),activeElement:null};
doc.getElementById('sidebar').append(doc.getElementById('chapter-nav'));
const location={protocol:'file:',pathname:'/guide-offline.html',hash:input.hash||'#/read'},window={__GUIDE_DATA__:input.data,addEventListener(k,fn){if(!windowHandlers.has(k))windowHandlers.set(k,[]);windowHandlers.get(k).push(fn);},scrollTo(){}};
const history={replaceState(_,__,hash){location.hash=hash;}};
class TestURL extends URL {}
TestURL.createObjectURL=blob=>{downloads.push(blob.parts.join(''));return 'blob:test-download';};TestURL.revokeObjectURL=()=>{};
class TestBlob {constructor(parts){this.parts=parts;}}
vm.runInNewContext(input.app,{window,document:doc,location,history,Node:N,URL:TestURL,URLSearchParams,Blob:TestBlob,localStorage:{getItem:()=>null},setTimeout:()=>0,clearTimeout(){}});
let validationMessage='';
for(const step of input.steps||[]){
  if(step.action==='open'){doc.getElementById('audience-toggle').focus();doc.getElementById('audience-toggle').emit('click');}
  else if(step.action==='value'){const field=doc.getElementById(step.id);field.value=step.value;field.emit(step.id==='audience-age'?'input':'change');}
  else if(step.action==='submit'){walk(doc.getElementById('audience-dialog-body')).find(n=>n.tag==='form').emit('submit');validationMessage=doc.getElementById('audience-error').textContent;}
  else if(step.action==='escape'){for(const fn of documentHandlers.get('keydown')||[])fn({key:'Escape'});}
  else if(step.action==='backdrop'){doc.getElementById('audience-dialog').emit('click');}
  else if(step.action==='clear'){walk(doc.getElementById('main')).find(n=>n.tag==='button'&&n.textContent==='清除人群筛选').emit('click');}
  else if(step.action==='download'){walk(doc.getElementById('main')).find(n=>n.className==='download-card'&&n.textContent.includes(step.label)).emit('click');}
  else if(step.action==='sidebar'){const link=walk(doc.getElementById('sidebar')).find(n=>n.tag==='a'&&n.attrs['data-chapter']===step.chapter);location.hash=link.getAttribute('href');for(const fn of windowHandlers.get('hashchange')||[])fn();}
}
const nodes=walk(doc.getElementById('main'));
process.stdout.write(JSON.stringify({
  cards:nodes.filter(n=>n.className==='entry-card').map(n=>n.attrs['data-entry']),
  text:doc.getElementById('main').textContent,
  links:nodes.filter(n=>n.tag==='a').map(n=>n.attrs.href),
  hash:location.hash,open:doc.getElementById('audience-dialog').open,
  validationMessage,focusReturned:doc.activeElement===doc.getElementById('audience-toggle'),downloads,
  sidebarLinks:walk(doc.getElementById('sidebar')).filter(n=>n.tag==='a').map(n=>n.getAttribute('href')),
  filtered:input.filters?window.GuideReader.filterAudience(input.filters):null
}));
"""


@unittest.skipUnless(shutil.which("node"), "Node.js executes the actual reader")
class AudienceReaderTests(unittest.TestCase):
    def data(self):
        data = reader_fixture()
        template = data["entries"][0]
        data["entries"] = []
        scopes = [
            ("eyes-001", ["child"], ["all"], False),
            ("eyes-002", ["teen"], ["all"], False),
            ("eyes-003", ["adult"], ["female"], False),
            ("eyes-004", ["older"], ["male"], False),
            ("eyes-005", ["adult"], ["male"], True),
            ("eyes-006", ["adult"], ["all"], False),
        ]
        for ordinal, (identifier, ages, sexes, pin) in enumerate(scopes, 1):
            entry = copy.deepcopy(template)
            entry.update(id=identifier, ordinal=ordinal, title="主题" + str(ordinal))
            entry["audience"] = dict(age_groups=ages, sexes=sexes, safety_pin=pin,
                                     scope_note="这是阅读侧重，不能替代个体用药核对。")
            data["entries"].append(entry)
        data["chapters"][0]["units"][0]["entry_ids"] = [e["id"] for e in data["entries"]]
        return data

    def render(self, route="#/read", steps=None, filters=None, data=None):
        result = subprocess.run(
            [shutil.which("node"), "-e", NODE_AUDIENCE],
            input=json.dumps(dict(data=data or self.data(), hash=route,
                                  steps=steps or [], filters=filters,
                                  app=(ROOT / "web/app.js").read_text(encoding="utf-8"))),
            text=True, encoding="utf-8", capture_output=True, check=True,
        )
        return json.loads(result.stdout)

    def test_exact_age_boundaries_and_under18_do_not_bypass_scope_for_safety(self):
        for age, expected in [(0, "eyes-001"), (11, "eyes-001"), (12, "eyes-002"),
                              (17, "eyes-002"), (18, "eyes-003"), (64, "eyes-003"),
                              (65, "eyes-004"), (120, "eyes-004")]:
            with self.subTest(age=age):
                cards = self.render(f"#/read?age={age}")["cards"]
                self.assertIn(expected, cards)
                self.assertEqual("eyes-005" in cards, 18 <= age < 65)
                self.assertNotIn("eyes-006", cards) if age < 18 or age >= 65 else None
        self.assertEqual(self.render("#/read?band=under18")["cards"],
                         ["eyes-001", "eyes-002"])

    def test_sex_filter_keeps_universal_content_and_excludes_other_sex_urgent_content(self):
        self.assertEqual(self.render("#/read?band=adult&sex=female")["cards"],
                         ["eyes-003", "eyes-006"])
        self.assertEqual(self.render("#/read?band=adult&sex=male")["cards"],
                         ["eyes-005", "eyes-006"])
        self.assertIn("急症条目也遵守同一规则", self.render("#/read?sex=female")["text"])

    def test_safety_pin_does_not_bypass_symptom_search_or_other_filter_dimensions(self):
        self.assertEqual(self.render("#/read?band=child&q=主题1")["cards"], ["eyes-001"])
        self.assertEqual(self.render("#/read?band=child&q=主题5")["cards"], [])
        self.assertEqual(self.render("#/read?band=adult&sex=male&q=主题5")["cards"], ["eyes-005"])

    def test_legacy_entries_default_to_adult_instead_of_claiming_child_coverage(self):
        data = self.data()
        for entry in data["entries"]:
            del entry["audience"]
        view = self.render("#/chapter/eyes?band=child", data=data)
        self.assertEqual(view["cards"], [])
        self.assertIn("本章该年龄或人群内容尚未系统整理", view["text"])
        self.assertIn("清除人群筛选，查看全章", view["text"])

    def test_entry_scope_and_navigation_query_are_retained(self):
        view = self.render("#/entry/eyes-003?age=16&sex=female")
        self.assertIn("本条的阅读侧重不同", view["text"])
        self.assertNotIn("主题3", view["text"])
        self.assertIn("#/chapter/eyes?age=16&sex=female", view["links"])

    def test_drawer_rejects_invalid_age_then_applies_band_and_gender(self):
        view = self.render(steps=[dict(action="open"),
                                 dict(action="value", id="audience-age", value="12.5"),
                                 dict(action="submit")])
        self.assertTrue(view["open"])
        self.assertIn("0至120之间的整数", view["validationMessage"])
        view = self.render(steps=[dict(action="open"),
                                 dict(action="value", id="audience-age", value="16"),
                                 dict(action="value", id="audience-band", value="adult"),
                                 dict(action="value", id="audience-sex", value="female"),
                                 dict(action="submit")])
        self.assertFalse(view["open"])
        self.assertEqual(view["hash"], "#/read?band=adult&sex=female")
        self.assertEqual(view["cards"], ["eyes-003", "eyes-006"])
        self.assertTrue(view["focusReturned"])

    def test_drawer_escape_backdrop_and_clear(self):
        for action in ("escape", "backdrop"):
            view = self.render(steps=[dict(action="open"), dict(action=action)])
            self.assertFalse(view["open"])
            self.assertTrue(view["focusReturned"])
        view = self.render("#/read?band=child&sex=female", steps=[dict(action="clear")])
        self.assertEqual(view["cards"], [f"eyes-{i:03d}" for i in range(1, 7)])
        self.assertEqual(view["hash"], "#/read")

    def test_invalid_link_parameters_cannot_create_a_demographic_claim(self):
        view = self.render("#/read?age=-1&band=unknown&sex=unknown")
        self.assertEqual(len(view["cards"]), 6)
        self.assertIn("不限年龄与男女", view["text"])

    def test_print_applies_the_current_demographic_filter(self):
        view = self.render("#/print?band=child&sex=female")
        self.assertEqual(view["text"].count("阅读侧重："), 1)
        self.assertEqual(view["text"].count("这是阅读侧重，不能替代个体用药核对。"), 1)
        self.assertIn("主题1", view["text"])
        self.assertNotIn("主题5", view["text"])
        self.assertEqual(view["text"].count("年龄分组用于导览，不代表治疗资格。"), 1)
        unfiltered = self.render("#/print")
        self.assertEqual(unfiltered["text"].count("阅读侧重："), 6)

    def test_offline_markdown_download_keeps_scope_note_age_sex_and_urgent_marker(self):
        view = self.render("#/about?band=child", steps=[dict(action="download", label="完整正文")])
        markdown = view["downloads"][0]
        self.assertEqual(markdown.count("阅读侧重："), 6)
        self.assertEqual(markdown.count("这是阅读侧重，不能替代个体用药核对。"), 6)
        self.assertIn("成人（18–64岁） · 男性 · 急症提示", markdown)
        self.assertIn("老年（65岁起） · 男性", markdown)
        self.assertNotIn("急症入口在年龄和男女筛选时保留", markdown)
        self.assertEqual(markdown.count("年龄分组用于导览，不代表治疗资格。"), 6)

    def test_offline_json_download_preserves_audience_metadata_without_filtering_the_book(self):
        view = self.render("#/about?band=child", steps=[dict(action="download", label="结构化数据")])
        exported = json.loads(view["downloads"][0])
        self.assertEqual(len(exported["entries"]), 6)
        for actual, expected in zip(exported["entries"], self.data()["entries"]):
            self.assertEqual(actual["audience"], expected["audience"])

    def test_persistent_sidebar_replaces_previous_exact_age_and_sex_after_drawer_apply(self):
        view = self.render("#/entry/eyes-004?age=72&sex=female", steps=[
            dict(action="open"), dict(action="value", id="audience-band", value="under18"),
            dict(action="value", id="audience-sex", value=""), dict(action="submit"),
            dict(action="sidebar", chapter="eyes"),
        ])
        self.assertEqual(view["hash"], "#/chapter/eyes?band=under18")
        self.assertEqual(view["cards"], ["eyes-001", "eyes-002"])
        self.assertEqual(view["sidebarLinks"], ["#/chapter/eyes?band=under18"])
        self.assertNotIn("72", view["hash"])
        self.assertNotIn("sex=", view["hash"])

    def test_clearing_audience_also_clears_persistent_sidebar_links(self):
        view = self.render("#/read?age=72&sex=female", steps=[
            dict(action="clear"), dict(action="sidebar", chapter="eyes"),
        ])
        self.assertEqual(view["hash"], "#/chapter/eyes")
        self.assertEqual(view["sidebarLinks"], ["#/chapter/eyes"])
        self.assertEqual(len(view["cards"]), 6)


if __name__ == "__main__":
    unittest.main()
