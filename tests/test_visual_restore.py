"""Visual restoration preserves book content and portable portrait delivery."""
import base64,hashlib,importlib.util,json,shutil,subprocess,unittest
from pathlib import Path
from scripts.build import build
from scripts.import_legacy import migrate
from test_audience_reader import NODE_AUDIENCE
from test_content import fixture,install_fixture,workspace_temp
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'drafts/whole-body/visual-restore-20261030'

class VisualRestoreTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('visual_contracts',HERE/'build_release.py');cls.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.module)
  cls.book,cls.chapters,cls.sources,cls.registry=cls.module.make_data()
 def test_visual_revision_does_not_rewrite_entry_or_source_data(self):
  old,chapters,sources,_=self.module.previous().make_data()
  self.assertEqual(chapters,self.chapters);self.assertEqual(sources,self.sources)
  self.assertEqual(old['entry_aliases'],self.book['entry_aliases'])
  self.assertEqual(len(self.book['entry_aliases']),9);self.assertEqual(self.book['content_version'],'2026.10.30-6')
  self.assertNotIn('阅读设置',self.book['front_matter'])
 def test_original_css_is_retained_with_only_scoped_hero_addition(self):
  css=(ROOT/'web/styles.css').read_bytes();baseline,addition=css.split(b'/* Retain the established reading scale;',1)
  self.assertEqual(hashlib.sha256(baseline.rstrip()).hexdigest(),'29be6f0911e293cb2db3827e967d462684a39581e17b92c19b4539bd8eb0b78f')
  self.assertNotIn(b'--reading-size',css);self.assertNotIn(b'.entry-card',addition)
 def test_offline_and_site_portraits_have_identical_bytes(self):
  # Exercise the current reader and asset from source, without any saved preview.
  with workspace_temp() as root:
   install_fixture(root,(self.book,self.chapters,self.sources,self.registry,[]))
   shutil.copytree(ROOT/'web',root/'web',dirs_exist_ok=True)
   build(root,built_at='2026-10-30T00:00:00Z')
   dist=root/'dist';asset='assets/home-portrait-abstract.png'
   original=(ROOT/'web'/asset).read_bytes()
   self.assertEqual((dist/asset).read_bytes(),original)
   self.assertIn("src:'"+asset+"'",(dist/'app.js').read_text(encoding='utf-8'))
   offline=(dist/'downloads/guide-offline.html').read_text(encoding='utf-8')
   self.assertIn('data:image/png;base64,'+base64.b64encode(original).decode('ascii'),offline)
   self.assertNotIn("src:'"+asset+"'",offline)
 def test_legacy_portrait_inlining_is_supported_in_an_isolated_fixture(self):
  # Legacy filename support is a compiler contract, not the current design.
  with workspace_temp() as root:
   install_fixture(root,migrate(*fixture()))
   asset='assets/home-portrait.png';target=root/'web'/asset
   target.parent.mkdir(parents=True,exist_ok=True)
   target.write_bytes((ROOT/'web'/asset).read_bytes())
   (root/'web/app.js').write_text("document.getElementById('main').appendChild(Object.assign(document.createElement('img'),{src:'"+asset+"'}));",encoding='utf-8')
   build(root,built_at='2026-10-30T00:00:00Z')
   original=target.read_bytes();dist=root/'dist'
   self.assertEqual((dist/asset).read_bytes(),original)
   offline=(dist/'downloads/guide-offline.html').read_text(encoding='utf-8')
   self.assertIn('data:image/png;base64,'+base64.b64encode(original).decode('ascii'),offline)
   self.assertNotIn("src:'"+asset+"'",offline)
 @unittest.skipUnless(shutil.which('node'),'Node runs the actual reader')
 def test_compact_home_keeps_search_near_the_top(self):
  data=dict(manifest={**self.book,'book':self.book},chapters=self.chapters,entries=[e for c in self.chapters for e in c['entries']],sources=self.sources)
  result=subprocess.run([shutil.which('node'),'-e',NODE_AUDIENCE],input=json.dumps(dict(data=data,hash='#/',app=(ROOT/'web/app.js').read_text(encoding='utf-8'))),text=True,encoding='utf-8',capture_output=True,check=True)
  text=json.loads(result.stdout)['text']
  self.assertIn('从头到脚，学会照顾自己。',text);self.assertIn('查找我的问题',text)
  self.assertLess(text.index('今天，从哪里开始'),400)
  for removed in ['字太小？','这本指南，怎么用最省力','身体是你做所有事情的底子']:
   self.assertNotIn(removed,text)

if __name__=='__main__':unittest.main()
