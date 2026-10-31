"""Run the real mobile reader against its real HTML; layout pixels are browser QA."""
from __future__ import annotations

from html.parser import HTMLParser
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest
from urllib.parse import urljoin

from scripts.static_pages import render_entry_html, render_prose
from scripts.build import build
from scripts.import_legacy import migrate
from test_audience_reader import NODE_AUDIENCE
from test_content import fixture, install_fixture, workspace_temp
from test_internal_links import reader_fixture

ROOT = Path(__file__).resolve().parents[1]


class BodyTree(HTMLParser):
    """Retain the actual navigation/control markup instead of inventing test nodes."""
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, markup):
        super().__init__()
        self.root = {'tag': 'root', 'attrs': {}, 'children': []}
        self.stack = [self.root]
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'children': []}
        self.stack[-1]['children'].append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1]['children'].append({'tag': tag, 'attrs': dict(attrs), 'children': []})

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]['tag'] == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data):
        self.stack[-1]['children'].append({'tag': '', 'text': data, 'attrs': {}, 'children': []})


NODE_MOBILE = NODE_AUDIENCE.split('vm.runInNewContext(input.app', 1)[0] + r"""
// Browser primitives only. All navigation, filtering, sharing and saving logic is app.js.
function classes(n){return new Set(String(n.className||'').split(/\s+/).filter(Boolean));}
function enhance(n){
 n.style={setProperty(k,v){this[k]=v;},removeProperty(k){delete this[k];}};
 n.classList={contains(c){return classes(n).has(c);},add(...items){const s=classes(n);items.forEach(c=>s.add(c));n.className=[...s].join(' ');},remove(...items){const s=classes(n);items.forEach(c=>s.delete(c));n.className=[...s].join(' ');},toggle(c,force){const s=classes(n),on=force===undefined?!s.has(c):force;if(on)s.add(c);else s.delete(c);n.className=[...s].join(' ');return on;}};
 if(n.tag==='details'){let open=!!n.open;Object.defineProperty(n,'open',{configurable:true,get(){return open;},set(value){const changed=open!==!!value;open=!!value;if(changed)n.emit('toggle');}});}
 return n;
}
function matchSimple(n,selector){
 if(!n.tag)return false;
 const exclusions=[...selector.matchAll(/:not\(([^)]+)\)/g)].map(m=>m[1]);
 if(exclusions.some(s=>matchSimple(n,s)))return false;
 selector=selector.replace(/:not\([^)]+\)/g,'');
 const tag=/^[a-zA-Z][a-zA-Z0-9-]*/.exec(selector);if(tag&&n.tag!==tag[0])return false;
 const id=/#([\w-]+)/.exec(selector);if(id&&n.getAttribute('id')!==id[1])return false;
 for(const c of selector.matchAll(/\.([\w-]+)/g))if(!classes(n).has(c[1]))return false;
 for(const a of selector.matchAll(/\[([\w-]+)(?:([\^$*]?=)["']?([^\]"']*)["']?)?\]/g)){
   const actual=n.getAttribute(a[1]);if(actual===null)return false;
   if(a[2]==='='&&actual!==a[3]||a[2]==='^='&&!actual.startsWith(a[3])||a[2]==='$='&&!actual.endsWith(a[3])||a[2]==='*='&&!actual.includes(a[3]))return false;
 }
 return true;
}
function matches(n,selector){return selector.split(',').some(part=>{const bits=part.trim().split(/\s+/),last=bits.pop();if(!matchSimple(n,last))return false;let p=n.parentNode;for(let i=bits.length-1;i>=0;i--){while(p&&!matchSimple(p,bits[i]))p=p.parentNode;if(!p)return false;p=p.parentNode;}return true;});}
N.prototype.append=function(...items){for(const item of items){if(item.parentNode)item.remove();item.parentNode=this;this.children.push(item);}};
N.prototype.replaceChildren=function(...items){for(const c of this.children)c.parentNode=null;this.children=[];this.text='';this.append(...items);};
N.prototype.remove=function(){if(this.parentNode){this.parentNode.children=this.parentNode.children.filter(n=>n!==this);this.parentNode=null;}};
N.prototype.querySelectorAll=function(selector){return walk(this).slice(1).filter(n=>matches(n,selector));};
N.prototype.querySelector=function(selector){return this.querySelectorAll(selector)[0]||null;};
N.prototype.closest=function(selector){for(let p=this;p;p=p.parentNode)if(matches(p,selector))return p;return null;};
N.prototype.contains=function(other){for(let p=other;p;p=p.parentNode)if(p===this)return true;return false;};
N.prototype.select=function(){this.selected=true;};
N.prototype.scrollIntoView=function(){};
Object.defineProperty(N.prototype,'offsetParent',{get(){for(let p=this;p;p=p.parentNode){if(p.hidden||p.inert)return null;const mobile=window.innerWidth<=760,id=p.getAttribute('id'),c=classes(p);if(mobile&&(id==='theme-toggle'||c.has('brand')||c.has('edition-label')||c.has('sidebar-bottom')||c.has('topbar-label')||c.has('audience-desktop-label')))return null;if(!mobile&&(id==='menu-toggle'||c.has('mobile-nav-link')||c.has('sidebar-mobile-head')||c.has('mobile-theme')||c.has('audience-mobile-label')))return null;}return this.parentNode;}});
N.prototype.getClientRects=function(){return this.offsetParent?[{}]:[];};
N.prototype.emitAsync=async function(kind,extra={}){
 let prevented=false;const event={preventDefault(){prevented=true;},target:this,currentTarget:this,...extra};
 for(let p=this;p;p=p.parentNode){event.currentTarget=p;for(const fn of p.handlers.get(kind)||[])await fn(event);}
 if(kind==='click'&&!prevented&&this.tag==='summary'&&this.parentNode?.tag==='details')this.parentNode.open=!this.parentNode.open;
 if(kind==='click'&&!prevented&&this.tag==='a'&&(this.getAttribute('href')||'').startsWith('#/')){
  const next=this.getAttribute('href'),changed=location.hash!==next;location.hash=next;if(changed)for(const fn of windowHandlers.get('hashchange')||[])await fn();
 }
};
function hydrate(raw){const n=enhance(new N(raw.tag,raw.text||''));for(const [k,v]of Object.entries(raw.attrs)){n.setAttribute(k,v??'');if(k==='class')n.className=v;if(k==='hidden')n.hidden=true;if(k==='value')n.value=v;}for(const child of raw.children)n.append(hydrate(child));return n;}
elements.clear();const tree=hydrate(input.html);
doc.documentElement=tree.querySelector('html');doc.body=tree.querySelector('body');doc.activeElement=doc.body;
doc.getElementById=id=>walk(tree).find(n=>n.getAttribute('id')===id)||null;
doc.createElement=tag=>enhance(new N(tag));doc.createElementNS=(_,tag)=>enhance(new N(tag));
doc.createTextNode=text=>enhance(new N('',String(text)));doc.createDocumentFragment=()=>enhance(new N());
doc.querySelectorAll=selector=>tree.querySelectorAll(selector);doc.querySelector=selector=>tree.querySelector(selector);
Object.assign(location,{protocol:'https:',pathname:'/body-care-guide/',href:'https://eothenofficial.github.io/body-care-guide/'});
const media=new Map();
window.matchMedia=query=>{if(!media.has(query)){const listeners=[];media.set(query,{media:query,matches:query.includes('760')?input.mobile!==false:false,addEventListener(_,fn){listeners.push(fn);},addListener(fn){listeners.push(fn);},notify(){for(const fn of listeners)fn(this);}});}return media.get(query);};
window.innerWidth=input.mobile===false?1200:375;window.scrollY=0;
const scrollCalls=[],storageWrites=[],storageReads=[],clipboardWrites=[];
const animationFrames=[];
if(input.animationFrame)window.requestAnimationFrame=fn=>{animationFrames.push(fn);return animationFrames.length;};
window.scrollTo=options=>{scrollCalls.push(options);window.scrollY=options.top||0;};
const localStorage={getItem(key){storageReads.push(key);if(input.storageReadBlocked)throw new Error('Storage unavailable');if(key==='body-care-guide:bookmarks:v1')return JSON.stringify(input.saved||[]);if(key==='body-care-guide:mobile-font:v1')return input.mobileFont??null;if(key==='body-care-guide:reading:v1')return JSON.stringify(input.legacyReading||null);return null;},setItem(key,value){if(input.storageBlocked)throw new Error('Storage unavailable');storageWrites.push({key,value});}};
const navigator={clipboard:{async writeText(text){clipboardWrites.push(text);if(input.clipboardFail)throw new Error('Permission denied');}}};
vm.runInNewContext(input.app,{window,document:doc,location,history,Node:N,URL:TestURL,URLSearchParams,Blob:TestBlob,navigator,localStorage,setTimeout:()=>0,clearTimeout(){}});
function state(){const side=doc.getElementById('sidebar'),menu=doc.getElementById('menu-toggle'),share=doc.getElementById('share-panel'),guide=doc.getElementById('home-guide'),guideToggle=doc.getElementById('home-guide-toggle');return {
 navOpen:side.classList.contains('open'),locked:doc.body.classList.contains('nav-open'),inert:!!side.inert,ariaHidden:side.getAttribute('aria-hidden'),expanded:menu.getAttribute('aria-expanded'),focus:doc.activeElement?.getAttribute('id'),y:window.scrollY,audienceOpen:doc.getElementById('audience-dialog').open,audienceLocked:doc.body.classList.contains('audience-open'),mainInert:!!doc.getElementById('main').inert,footerInert:!!doc.querySelector('.site-footer').inert,headerInert:!!doc.querySelector('.topbar').inert,pendingFrames:animationFrames.length,
 shareCount:doc.querySelectorAll('#share-panel').length,shareInputs:share?walk(share).filter(n=>n.tag==='input').map(n=>({value:n.value,attrs:n.attrs})):[],
 home:doc.getElementById('mobile-home-link')?.getAttribute('href'),search:doc.getElementById('mobile-search-link')?.getAttribute('href'),hash:location.hash,
 saves:walk(doc.getElementById('main')).filter(n=>n.getAttribute('data-save')).map(n=>({id:n.getAttribute('data-save'),text:n.textContent,pressed:n.getAttribute('aria-pressed'),icons:walk(n).filter(c=>c.tag==='svg').length})),theme:doc.body.dataset.theme,mobileTheme:doc.getElementById('mobile-theme-toggle')?.textContent,mobileThemeLabel:doc.getElementById('mobile-theme-toggle')?.getAttribute('aria-label'),desktopTheme:doc.getElementById('theme-toggle')?.getAttribute('aria-label'),
 mobileFont:doc.body.getAttribute('data-mobile-font')||doc.body.dataset.mobileFont||null,
 legacyReadingSize:doc.body.getAttribute('data-reading-size'),legacyReadingLine:doc.body.getAttribute('data-reading-line'),
 fontButtons:['small','medium','large'].map(size=>({size,pressed:doc.getElementById('mobile-font-'+size)?.getAttribute('aria-pressed'),text:doc.getElementById('mobile-font-'+size)?.textContent})),
 guideExists:!!guide,guideOpen:!!guide?.open,guideTag:guide?.tag,guideExpanded:guideToggle?.getAttribute('aria-expanded'),guideLabel:guideToggle?.textContent,savedCount:doc.getElementById('saved-count').textContent,sourceOpen:doc.getElementById('source-dialog').open
};}
function visibleText(n){if(n.hidden)return '';if(n.tag==='details'&&!n.open)return n.querySelector('summary')?.textContent||'';return n.text+n.children.map(visibleText).join('');}
function actionButton(text){return walk(doc.getElementById('main')).find(n=>n.tag==='button'&&n.textContent.includes(text));}
const snapshots=[];
(async()=>{
 snapshots.push(state());
 for(const step of input.steps||[]){
  if(step.action==='click'){const target=doc.getElementById(step.id);if(!target)throw new Error('Missing actual HTML control: '+step.id);target.focus();await target.emitAsync('click');}
  else if(step.action==='scroll'){window.scrollY=step.y;}
  else if(step.action==='key'){for(const fn of documentHandlers.get('keydown')||[])await fn({key:step.key,shiftKey:!!step.shift,preventDefault(){},target:doc.activeElement});}
  else if(step.action==='desktop'){window.innerWidth=1200;for(const value of media.values())if(value.media.includes('760')){value.matches=false;value.notify();}for(const fn of windowHandlers.get('resize')||[])await fn();}
  else if(step.action==='route'){location.hash=step.hash;for(const fn of windowHandlers.get('hashchange')||[])await fn();}
  else if(step.action==='sidebar'){const link=walk(doc.getElementById('sidebar')).find(n=>n.getAttribute('data-chapter')===step.chapter);await link.emitAsync('click');}
  else if(step.action==='save'){const button=walk(doc.getElementById('main')).find(n=>n.getAttribute('data-save')===step.id);await button.emitAsync('click');}
  else if(step.action==='copy'){await doc.getElementById('copy-entry-link').emitAsync('click');}
  else if(step.action==='citation'){const scope=doc.getElementById('home-guide')||doc.getElementById('main');const target=walk(scope).filter(n=>n.tag==='button'&&classes(n).has('citation'))[step.index||0];if(!target)throw new Error('Missing rendered citation');target.focus();await target.emitAsync('click');}
  else if(step.action==='frame'){for(const fn of animationFrames.splice(0))fn(0);}
  snapshots.push(state());
 }
 const guide=doc.getElementById('home-guide'),guideToggle=doc.getElementById('home-guide-toggle');
 process.stdout.write(JSON.stringify({snapshots,storageWrites,storageReads,clipboardWrites,text:doc.getElementById('main').textContent,visibleText:visibleText(doc.getElementById('main')),headerText:doc.querySelector('.topbar').textContent,
 links:walk(doc.getElementById('main')).filter(n=>n.tag==='a').map(n=>({href:n.getAttribute('href'),text:n.textContent,icons:walk(n).filter(c=>c.tag==='svg').length,iconUses:walk(n).filter(c=>c.tag==='use').map(c=>c.getAttribute('href'))})),
 guideText:guide?.textContent||'',guideSummary:guide?.querySelector('summary')?.textContent||'',guideSections:guide?walk(guide).filter(n=>n.tag==='section').length:0,
 methodControl:guideToggle?{tag:guideToggle.tag,controls:guideToggle.getAttribute('aria-controls'),text:guideToggle.textContent,icons:walk(guideToggle).filter(n=>n.tag==='svg').length,iconUses:walk(guideToggle).filter(n=>n.tag==='use').map(n=>n.getAttribute('href'))}:null,
 heroParagraphs:doc.querySelectorAll('.hero-description').map(n=>n.textContent),guideCitations:guide?walk(guide).filter(n=>n.tag==='button'&&classes(n).has('citation')).map(n=>({label:n.getAttribute('aria-label'),text:n.textContent})):[],
 homeLandmarks:walk(doc.getElementById('main')).filter(n=>classes(n).has('hero')||classes(n).has('stats')||n.getAttribute('id')==='home-guide'||classes(n).has('section-heading')).map(n=>n.getAttribute('id')||n.className),
 sourceDialogText:doc.getElementById('source-dialog-body').textContent,
 fontControlsInSidebar:['small','medium','large'].every(size=>doc.getElementById('sidebar').contains(doc.getElementById('mobile-font-'+size)))}));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1;});
"""


@unittest.skipUnless(shutil.which('node'), 'Node executes the actual mobile reader')
class MobileReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('home_disclosure_contracts', ROOT / 'drafts/whole-body/approved-home-20261030/build_release.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        book, chapters, sources, _ = module.make_data()
        cls.production_data = dict(manifest={**book, 'book': book}, chapters=chapters,
                                   entries=[e for c in chapters for e in c['entries']], sources=sources)

    def run_reader(self, steps=(), route='#/entry/eyes-001', **options):
        data = options.pop('data', None) or reader_fixture()
        result = subprocess.run([shutil.which('node'), '-e', NODE_MOBILE],
            input=json.dumps(dict(data=data, hash=route, steps=steps,
                html=BodyTree((ROOT / 'web/index.html').read_text(encoding='utf-8')).root,
                app=(ROOT / 'web/app.js').read_text(encoding='utf-8'), **options)),
            text=True, encoding='utf-8', capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_mobile_directory_can_open_at_scroll_and_close_without_losing_position(self):
        result = self.run_reader([dict(action='scroll', y=1800), dict(action='click', id='menu-toggle'), dict(action='click', id='nav-close')])
        initial, _, opened, closed = result['snapshots']
        self.assertTrue(initial['inert'])
        self.assertTrue(opened['navOpen']);self.assertTrue(opened['locked']);self.assertFalse(opened['inert'])
        self.assertEqual(opened['expanded'], 'true')
        self.assertEqual(opened['focus'], 'nav-close')
        self.assertFalse(closed['navOpen']);self.assertFalse(closed['locked']);self.assertTrue(closed['inert'])
        self.assertEqual(closed['expanded'], 'false');self.assertEqual(closed['focus'], 'menu-toggle')
        self.assertEqual(closed['y'], 1800)

    def test_escape_backdrop_and_selected_chapter_all_unlock_the_background(self):
        for close in [dict(action='key', key='Escape'), dict(action='click', id='nav-shade'), dict(action='sidebar', chapter='eyes')]:
            with self.subTest(close=close):
                result = self.run_reader([dict(action='click', id='menu-toggle'), close])
                final = result['snapshots'][-1]
                self.assertFalse(final['navOpen']);self.assertFalse(final['locked']);self.assertTrue(final['inert'])
                self.assertEqual(final['expanded'], 'false')
                if close['action'] == 'sidebar':
                    self.assertEqual(final['hash'], '#/chapter/eyes')

    def test_resizing_to_desktop_restores_sidebar_access_and_background_scroll(self):
        final = self.run_reader([dict(action='click', id='menu-toggle'), dict(action='desktop')])['snapshots'][-1]
        self.assertFalse(final['navOpen']);self.assertFalse(final['locked']);self.assertFalse(final['inert'])
        self.assertNotEqual(final['ariaHidden'], 'true')
        self.assertEqual(final['focus'], 'main')
        self.assertFalse(final['mainInert']);self.assertFalse(final['footerInert'])

    def test_open_directory_excludes_background_content_but_keeps_persistent_header_operable(self):
        initial, opened, closed = self.run_reader([dict(action='click', id='menu-toggle'), dict(action='click', id='nav-close')])['snapshots']
        self.assertFalse(initial['mainInert']);self.assertFalse(initial['footerInert'])
        self.assertTrue(opened['mainInert']);self.assertTrue(opened['footerInert']);self.assertFalse(opened['headerInert'])
        self.assertFalse(closed['mainInert']);self.assertFalse(closed['footerInert']);self.assertFalse(closed['headerInert'])

    def test_deferred_directory_focus_waits_for_render_and_cannot_steal_focus_after_close(self):
        result = self.run_reader([dict(action='click', id='menu-toggle'), dict(action='frame')], animationFrame=True)
        waiting, rendered = result['snapshots'][1:]
        self.assertEqual(waiting['focus'], 'menu-toggle');self.assertEqual(waiting['pendingFrames'], 1)
        self.assertEqual(rendered['focus'], 'nav-close');self.assertEqual(rendered['pendingFrames'], 0)
        result = self.run_reader([dict(action='click', id='menu-toggle'), dict(action='click', id='nav-close'), dict(action='frame')], animationFrame=True)
        closed = result['snapshots'][-1]
        self.assertFalse(closed['navOpen']);self.assertFalse(closed['locked']);self.assertTrue(closed['inert'])
        self.assertEqual(closed['focus'], 'menu-toggle');self.assertEqual(closed['pendingFrames'], 0)

    def test_current_header_destination_closes_directory_without_needing_hashchange(self):
        for route, target in [('#/', 'mobile-home-link'), ('#/read', 'mobile-search-link')]:
            with self.subTest(route=route):
                final = self.run_reader([dict(action='scroll', y=1800), dict(action='click', id='menu-toggle'), dict(action='click', id=target)], route=route)['snapshots'][-1]
                self.assertFalse(final['navOpen']);self.assertFalse(final['locked'])
                self.assertEqual(final['hash'], route)

    def test_header_filter_replaces_directory_without_leaving_the_background_locked(self):
        result = self.run_reader([dict(action='scroll', y=1800), dict(action='click', id='menu-toggle'), dict(action='click', id='audience-toggle'), dict(action='key', key='Escape')])
        opened, closed = result['snapshots'][3:]
        self.assertFalse(opened['navOpen']);self.assertFalse(opened['locked'])
        self.assertTrue(opened['audienceOpen']);self.assertTrue(opened['audienceLocked'])
        self.assertFalse(closed['audienceOpen']);self.assertFalse(closed['audienceLocked'])
        self.assertEqual(closed['focus'], 'audience-toggle');self.assertEqual(closed['y'], 1800)

    def test_tab_and_shift_tab_stay_within_open_navigation_and_persistent_header(self):
        result = self.run_reader([dict(action='click', id='menu-toggle'), dict(action='key', key='Tab', shift=True), dict(action='key', key='Tab')])
        self.assertEqual(result['snapshots'][1]['focus'], 'nav-close')
        self.assertEqual(result['snapshots'][2]['focus'], 'audience-toggle')
        self.assertEqual(result['snapshots'][3]['focus'], 'nav-close')

    def test_theme_control_inside_mobile_directory_keeps_desktop_control_synchronized(self):
        result = self.run_reader([dict(action='click', id='menu-toggle'), dict(action='click', id='mobile-theme-toggle'), dict(action='click', id='mobile-theme-toggle')])
        dark, light = result['snapshots'][2:]
        self.assertEqual(dark['theme'], 'dark');self.assertEqual(light['theme'], 'light')
        self.assertEqual(dark['mobileTheme'], '浅色');self.assertEqual(light['mobileTheme'], '深色')
        self.assertEqual(dark['mobileThemeLabel'], '切换浅色模式');self.assertEqual(dark['desktopTheme'], '切换浅色模式')
        self.assertEqual(light['mobileThemeLabel'], '切换深色模式');self.assertEqual(light['desktopTheme'], '切换深色模式')
        self.assertTrue(dark['navOpen']);self.assertTrue(light['navOpen'])

    def test_fixed_home_and_search_links_keep_current_demographic_filters(self):
        result = self.run_reader(route='#/read?band=adult&sex=female')
        final = result['snapshots'][-1]
        self.assertEqual(final['home'], '#/?band=adult&sex=female')
        self.assertEqual(final['search'], '#/read?band=adult&sex=female')
        result = self.run_reader([dict(action='route', hash='#/read')], route='#/read?band=adult&sex=female')
        self.assertEqual(result['snapshots'][-1]['home'], '#/')
        self.assertEqual(result['snapshots'][-1]['search'], '#/read')

    def test_save_toggle_preserves_single_icon_text_and_existing_storage_key(self):
        result = self.run_reader([dict(action='save', id='eyes-001'), dict(action='save', id='eyes-001')])
        saves = [snapshot['saves'][0] for snapshot in result['snapshots']]
        self.assertEqual([s['text'] for s in saves], ['收藏', '已收藏', '收藏'])
        self.assertEqual([s['pressed'] for s in saves], ['false', 'true', 'false'])
        self.assertTrue(all(s['icons'] == 1 for s in saves))
        self.assertTrue(all(w['key'] == 'body-care-guide:bookmarks:v1' for w in result['storageWrites']))

    def test_clipboard_failure_shows_one_reusable_and_closable_share_panel(self):
        result = self.run_reader([dict(action='copy'), dict(action='copy'), dict(action='click', id='share-close')], clipboardFail=True)
        first, repeat, closed = result['snapshots'][1:]
        self.assertEqual(first['shareCount'], 1);self.assertEqual(repeat['shareCount'], 1)
        self.assertEqual(len(repeat['shareInputs']), 1)
        self.assertEqual(repeat['shareInputs'][0]['value'], 'https://eothenofficial.github.io/body-care-guide/read/eyes-001/')
        self.assertIn('readonly', repeat['shareInputs'][0]['attrs'])
        self.assertEqual(closed['shareCount'], 0)
        self.assertNotIn('Permission denied', result['text'])

    def test_successful_clipboard_copy_uses_public_static_link_without_extra_panel(self):
        result = self.run_reader([dict(action='copy')])
        self.assertEqual(result['clipboardWrites'], ['https://eothenofficial.github.io/body-care-guide/read/eyes-001/'])
        self.assertEqual(result['snapshots'][-1]['shareCount'], 0)

    def test_mobile_font_defaults_to_medium_and_marks_exactly_one_choice(self):
        result = self.run_reader(route='#/read')
        state = result['snapshots'][0]
        self.assertEqual(state['mobileFont'], 'medium')
        self.assertEqual([b['size'] for b in state['fontButtons'] if b['pressed'] == 'true'], ['medium'])
        self.assertEqual([b['text'] for b in state['fontButtons']], ['小', '中', '大'])
        self.assertTrue(result['fontControlsInSidebar'])
        self.assertFalse(any(w['key'] == 'body-care-guide:mobile-font:v1' for w in result['storageWrites']))

    def test_mobile_font_selection_persists_an_enum_without_changing_reading_context(self):
        route = '#/entry/eyes-001?band=adult&sex=female'
        result = self.run_reader([dict(action='click', id='menu-toggle'),
                                  dict(action='click', id='mobile-font-large'),
                                  dict(action='click', id='mobile-font-small')],
                                 route=route, saved=['eyes-001'])
        large, small = result['snapshots'][2:]
        self.assertEqual(large['mobileFont'], 'large');self.assertEqual(small['mobileFont'], 'small')
        self.assertEqual([b['size'] for b in large['fontButtons'] if b['pressed'] == 'true'], ['large'])
        self.assertEqual([b['size'] for b in small['fontButtons'] if b['pressed'] == 'true'], ['small'])
        for state in [large, small]:
            self.assertTrue(state['navOpen'])
            self.assertEqual(state['hash'], route)
            self.assertEqual(state['home'], '#/?band=adult&sex=female')
            self.assertEqual(state['saves'][0]['pressed'], 'true')
        writes = [w for w in result['storageWrites'] if w['key'] == 'body-care-guide:mobile-font:v1']
        self.assertEqual([w['value'] for w in writes], ['large', 'small'])
        self.assertFalse(any(w['key'] == 'body-care-guide:bookmarks:v1' for w in result['storageWrites']))

    def test_mobile_font_reloads_only_valid_preferences_and_ignores_withdrawn_desktop_settings(self):
        for pref in ['small', 'medium', 'large', '', 'oversized', '24', '{"size":24}', ' LARGE ']:
            with self.subTest(pref=pref):
                result = self.run_reader(mobileFont=pref, legacyReading={'size':24,'line':'relaxed'})
                state = result['snapshots'][0]
                self.assertEqual(state['mobileFont'], pref if pref in {'small','medium','large'} else 'medium')
                self.assertIsNone(state['legacyReadingSize']);self.assertIsNone(state['legacyReadingLine'])
                self.assertNotIn('body-care-guide:reading:v1', result['storageReads'])
                self.assertFalse(any(w['key'] == 'body-care-guide:reading:v1' for w in result['storageWrites']))
        desktop = self.run_reader(mobile=False, mobileFont='large', legacyReading={'size':24,'line':'relaxed'})
        self.assertIsNone(desktop['snapshots'][0]['legacyReadingSize'])
        self.assertIsNone(desktop['snapshots'][0]['legacyReadingLine'])
        self.assertNotIn('body-care-guide:reading:v1', desktop['storageReads'])

    def test_mobile_font_unavailable_storage_does_not_break_reading_or_current_selection(self):
        result = self.run_reader([dict(action='click', id='menu-toggle'), dict(action='click', id='mobile-font-large')],
                                 storageReadBlocked=True, storageBlocked=True)
        self.assertEqual(result['snapshots'][0]['mobileFont'], 'medium')
        self.assertEqual(result['snapshots'][-1]['mobileFont'], 'large')
        self.assertTrue(result['text'])
        self.assertFalse(any(w['key'] == 'body-care-guide:mobile-font:v1' for w in result['storageWrites']))

    def test_about_replaces_internal_developer_panel_with_author_profile_and_invitation(self):
        result = self.run_reader(route='#/about')
        self.assertIn('开发者', result['text']);self.assertIn('Eothen Tsang', result['text'])
        self.assertRegex(result['text'], '共同维护|一起维护');self.assertIn('建议', result['text'])
        profile = [link for link in result['links'] if (link['href'] or '').rstrip('/') == 'https://github.com/eothenofficial']
        self.assertEqual(len(profile), 1)
        self.assertNotIn('给维护者与开发者', result['text'])
        self.assertNotIn('自动检查负责字段、引用、链接与复核期限', result['text'])
        self.assertFalse(any((link['href'] or '').startswith('api/v1/') for link in result['links']))
        self.assertTrue(any((link['href'] or '').endswith('downloads/guide.json') for link in result['links']))

    def test_home_reading_method_button_uses_controlled_vector_and_names_its_inline_guide(self):
        result = self.run_reader(route='#/', data=self.production_data)
        method = result['methodControl']
        self.assertIsNotNone(method)
        self.assertEqual(method['tag'], 'button')
        self.assertEqual(method['text'], '了解阅读方法')
        self.assertEqual(method['controls'], 'home-guide')
        self.assertEqual(method['icons'], 1)
        self.assertTrue(all((use or '').startswith('#i-') for use in method['iconUses']))
        self.assertFalse(any('section=method' in (link['href'] or '') for link in result['links']))

    def test_home_guide_is_closed_after_stats_and_does_not_duplicate_the_approved_hero(self):
        result = self.run_reader(route='#/', data=self.production_data)
        state = result['snapshots'][0]
        home = self.production_data['manifest']['home_content']
        self.assertTrue(state['guideExists']);self.assertEqual(state['guideTag'], 'details')
        self.assertFalse(state['guideOpen']);self.assertEqual(state['guideExpanded'], 'false')
        self.assertEqual(result['heroParagraphs'], home['lead'].split('\n\n'))
        for paragraph in result['heroParagraphs']:
            self.assertEqual(result['text'].count(paragraph), 1)
            self.assertNotIn(paragraph, result['guideText'])
        landmarks = result['homeLandmarks']
        self.assertLess(landmarks.index('hero'), landmarks.index('stats'))
        self.assertLess(landmarks.index('stats'), landmarks.index('home-guide'))
        self.assertLess(landmarks.index('home-guide'), landmarks.index('section-heading'))
        self.assertIn('先了解这份指南', result['guideSummary'])
        self.assertNotIn(home['why_title'], result['visibleText'])
        self.assertIn('今天，从哪里开始', result['visibleText'])

    def test_home_guide_opens_and_closes_inline_without_changing_audience_or_bookmarks(self):
        route = '#/?band=adult&sex=female'
        result = self.run_reader([dict(action='click', id='home-guide-toggle'),
                                  dict(action='click', id='home-guide-summary'),
                                  dict(action='click', id='home-guide-summary'),
                                  dict(action='click', id='home-guide-toggle')],
                                 route=route, data=self.production_data, saved=['eyes-001'])
        initial, opened, closed, reopened, button_closed = result['snapshots']
        self.assertFalse(initial['guideOpen']);self.assertTrue(opened['guideOpen']);self.assertFalse(closed['guideOpen'])
        self.assertTrue(reopened['guideOpen']);self.assertFalse(button_closed['guideOpen'])
        self.assertEqual([s['guideExpanded'] for s in result['snapshots']], ['false', 'true', 'false', 'true', 'false'])
        self.assertIn('收起', opened['guideLabel']);self.assertEqual(closed['guideLabel'], '了解阅读方法')
        for snapshot in result['snapshots']:
            self.assertEqual(snapshot['hash'], route)
            self.assertEqual(snapshot['savedCount'], '1')
            self.assertEqual(snapshot['home'], route)
        self.assertEqual(result['storageWrites'], [])

    def test_home_guide_renders_all_approved_sections_and_citations_as_reader_controls(self):
        result = self.run_reader([dict(action='click', id='home-guide-toggle'),
                                  dict(action='citation')], route='#/', data=self.production_data)
        home = self.production_data['manifest']['home_content']
        self.assertEqual(result['guideSections'], 3)
        for phrase in [home['why_title'], '读完能做什么', '怎么使用',
                       '如果疲劳持续、原因不明，或已经影响日常生活，就需要评估',
                       '身体和情绪会彼此影响，但没有一种原因能解释所有不舒服',
                       '医学内容尚未经过临床医生逐条签审']:
            self.assertIn(phrase, result['guideText'])
        for decision in home['decisions']:
            self.assertIn(decision['title'], result['guideText']);self.assertIn(decision['text'], result['guideText'])
        self.assertEqual(len(result['guideCitations']), 2)
        self.assertTrue(all(c['label'] and re.fullmatch(r'\[\d+\]', c['text']) for c in result['guideCitations']))
        self.assertNotRegex(result['guideText'], r'\[@src-')
        self.assertTrue(result['snapshots'][-1]['sourceOpen'])
        self.assertIn('它支持什么', result['sourceDialogText'])
        for identifier in ['basics-003', 'basics-008']:
            self.assertTrue(any((link['href'] or '') == '#/entry/' + identifier for link in result['links']))

    def test_home_guide_direct_link_opens_and_about_links_to_the_same_home_content(self):
        result = self.run_reader(route='#/?section=guide&band=older&sex=female', data=self.production_data)
        self.assertTrue(result['snapshots'][0]['guideOpen'])
        self.assertEqual(result['snapshots'][0]['guideExpanded'], 'true')
        self.assertIn('身体是你做所有事情的底子', result['visibleText'])
        about = self.run_reader(route='#/about?band=older&sex=female', data=self.production_data)
        self.assertNotIn(self.production_data['manifest']['home_content']['why_title'], about['text'])
        self.assertTrue(any('section=guide' in (link['href'] or '') and (link['href'] or '').startswith('#/?') for link in about['links']))
        self.assertIn('怎样理解证据等级', about['text'])

    def test_minimal_older_book_without_home_guide_still_has_a_working_method_destination(self):
        result = self.run_reader(route='#/')
        self.assertFalse(result['snapshots'][0]['guideExists'])
        self.assertTrue(any('section=method' in (link['href'] or '') for link in result['links']))


def tree_nodes(node):
    yield node
    for child in node.get('children', []):
        yield from tree_nodes(child)


def tree_text(node):
    return node.get('text', '') + ''.join(tree_text(child) for child in node.get('children', []))


class StaticMobileReaderTests(unittest.TestCase):
    def test_changed_mobile_styles_refresh_published_asset_urls_without_changing_book_version(self):
        # A returning phone may cache all three files independently. Query values
        # must describe the bytes actually published, while offline stays self-contained.
        with workspace_temp() as root:
            install_fixture(root, migrate(*fixture()))
            shutil.copytree(ROOT / 'web', root / 'web', dirs_exist_ok=True)
            raw_index = (root / 'web/index.html').read_bytes()

            def inspect_build():
                manifest = build(root=root, built_at='2026-10-30T00:00:00Z')
                dist = root / 'dist'
                nodes = list(tree_nodes(BodyTree((dist / 'index.html').read_text(encoding='utf-8')).root))
                references = [n['attrs'].get('src') or n['attrs'].get('href') for n in nodes]
                urls = {}
                for name in ('styles.css', 'app.js', 'data.js'):
                    expected = name + '?v=' + hashlib.sha256((dist / name).read_bytes()).hexdigest()[:16]
                    self.assertEqual(references.count(expected), 1, name)
                    urls[name] = expected
                self.assertRegex(manifest['reader_revision'], r'^[0-9a-f]{16}$')
                share = next((dist / 'read').glob('*/index.html')).read_text(encoding='utf-8')
                self.assertIn('href="../../styles.css?v=' + manifest['reader_revision'] + '"', share)
                offline = (dist / 'downloads/guide-offline.html').read_text(encoding='utf-8')
                offline_nodes = list(tree_nodes(BodyTree(offline).root))
                self.assertFalse(any(n['tag'] == 'script' and n['attrs'].get('src') for n in offline_nodes))
                self.assertFalse(any(n['tag'] == 'link' and n['attrs'].get('rel') == 'stylesheet' for n in offline_nodes))
                payload = json.loads(re.search(r'window\.__GUIDE_DATA__=(.*?);\n', offline, re.S).group(1))
                self.assertEqual(payload, json.loads((dist / 'downloads/guide.json').read_text(encoding='utf-8')))
                self.assertEqual(payload['manifest'], manifest)
                return manifest, payload, urls

            before, old_data, old_urls = inspect_build()
            css = root / 'web/styles.css'
            css.write_bytes(css.read_bytes() + b'\n/* Mobile cache regression fixture. */\n')
            after, new_data, new_urls = inspect_build()
            self.assertNotEqual(after['reader_revision'], before['reader_revision'])
            self.assertNotEqual(new_urls['styles.css'], old_urls['styles.css'])
            self.assertNotEqual(new_urls['data.js'], old_urls['data.js'])
            self.assertEqual(new_urls['app.js'], old_urls['app.js'])
            self.assertEqual(after['content_version'], before['content_version'])
            for key in ('entries', 'chapters', 'sources'):
                self.assertEqual(new_data[key], old_data[key])
            self.assertEqual((root / 'web/index.html').read_bytes(), raw_index)

    def test_shared_article_has_four_script_free_navigation_links_with_correct_subpaths(self):
        data = reader_fixture()
        markup = render_entry_html(data, data['entries'][0])
        nodes = list(tree_nodes(BodyTree(markup).root))
        navs = [n for n in nodes if n['tag'] == 'nav' and n['attrs'].get('class') == 'static-mobile-nav']
        self.assertEqual(len(navs), 1)
        nav = navs[0]
        self.assertEqual(nav['attrs'].get('aria-label'), '手机阅读导航')
        links = [n for n in tree_nodes(nav) if n['tag'] == 'a']
        self.assertEqual([tree_text(n) for n in links], ['首页', '本章目录', '查找', '打开指南'])
        expected = ['#/', '#/chapter/eyes', '#/read', '#/entry/eyes-001']
        for base, root in [('https://example.org/nested/guide/read/eyes-001/', 'https://example.org/nested/guide/'),
                           ('file:///C:/offline-guide/read/eyes-001/index.html', 'file:///C:/offline-guide/')]:
            with self.subTest(base=base):
                self.assertEqual([urljoin(base, n['attrs']['href']) for n in links], [root + suffix for suffix in expected])
        self.assertFalse(any(n['tag'] == 'script' for n in nodes))
        self.assertEqual(sum(n['tag'] == 'h1' for n in nodes), 1)
        self.assertIn(data['entries'][0]['title'], markup)

    def test_comparison_table_hint_and_keyboard_region_preserve_cells_and_citations(self):
        identifier = 'src-0123456789ab'
        prose = '| 方案 | 用途 | 来源 |\n| --- | --- | --- |\n| 甲 | 说明 | [@' + identifier + '] |'
        markup = render_prose(prose, {identifier: {'number': 7}}, {'eyes-001'})
        nodes = list(tree_nodes(BodyTree(markup).root))
        wrappers = [n for n in nodes if n['attrs'].get('class') == 'table-wrap']
        self.assertEqual(len(wrappers), 1)
        self.assertEqual(wrappers[0]['attrs'].get('role'), 'region')
        self.assertEqual(wrappers[0]['attrs'].get('tabindex'), '0')
        self.assertTrue(wrappers[0]['attrs'].get('aria-label'))
        hints = [n for n in nodes if n['attrs'].get('class') == 'table-hint']
        self.assertEqual([tree_text(n) for n in hints], ['左右滑动查看完整表格'])
        self.assertEqual(sum(n['tag'] == 'th' for n in nodes), 3)
        self.assertEqual(sum(n['tag'] == 'td' for n in nodes), 3)
        self.assertIn('href="#ref-' + identifier + '"', markup)


if __name__ == '__main__':
    unittest.main()
