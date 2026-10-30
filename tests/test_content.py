"""Content integrity and portable-export tests; no medical efficacy assertions."""
from __future__ import annotations

import copy
import json
import re
import shutil
import unittest
import uuid
from contextlib import contextmanager
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree as ET

from scripts.build import (book_markdown, build, data_script, inline_offline, pack_data)
from scripts.content_model import (CHAPTER_NAMES, FIELD_NAMES, ContentError, evidence_labels,
                                   load_content, parse_manuscript, source_id, source_identity,
                                   validate_content, write_json)
from scripts.import_legacy import migrate
from scripts.static_pages import render_entry_html

ROOT = Path(__file__).resolve().parents[1]
STAMP = "2026-10-29T00:00:00Z"


class PageFacts(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


@contextmanager
def workspace_temp():
    # Keep fixtures in the authorized workspace, including under Windows sandboxing.
    base = (ROOT / ".test-tmp").resolve()
    base.mkdir(exist_ok=True)
    # tempfile's private 0700 ACL can exclude the Windows sandbox identity.
    # A normal workspace mkdir inherits the workspace's authorized ACL instead.
    target = (base / ("test-" + uuid.uuid4().hex)).resolve()
    if not target.is_relative_to(base) or target == base:
        raise AssertionError("Temporary fixture escaped the test workspace")
    target.mkdir()
    try:
        yield target
    finally:
        resolved = target.resolve()
        if not resolved.is_relative_to(base) or resolved == base:
            raise AssertionError("Temporary cleanup target escaped the test workspace")
        shutil.rmtree(resolved)


def fixture():
    """Synthetic prose deliberately carries no medical advice."""
    text = "导言 [1]\n\n# 阅读导览\n\n只是导览\n"
    audits = []
    for key, title in CHAPTER_NAMES.items():
        text += f"\n# {title} 示例章节\n\n篇章引言\n\n## 示例单元\n\n单元引言\n\n### 1 保留原句\n\n"
        values = {"成本": "示例成本", "说人话": "原文，不新增医学结论。", "收益": "仅作测试。", "证据等级": "C，示例。", "来源": "[1]", "备注": "备注另引[2]。"}
        text += "\n\n".join(f"**{label}：** {value}" for label, value in values.items()) + "\n"
        audits.append({"章节": title, "条目": 1, "最终标题": "1 保留原句", "最终文献号": [1, 2], "核查状态": "案头核查", "原始核查": {"边界": "不是医生签审"}})
    text += "\n# 证据与引用说明\n\n说明[2]\n\n# 参考文献\n\n[1] 不应重复导入的旧列表\n"
    sources = [{"id": "OLD1", "number": 1, "citation": "Example. doi:10.1234/example.", "url": "https://example.org/paper", "type": "test", "支持结论": "保留", "局限": "非医学研究", "review_edition": "2026-10-28"},
               {"id": "OLD2", "number": 2, "citation": "Example source [Internet]. Available from:", "url": "https://example.org/second", "type": "test", "支持结论": "保留二", "局限": "非医学研究", "review_edition": "2026-10-28"}]
    return text, sources, audits


def install_fixture(root, result):
    book, chapters, sources, registry, reviews = result
    write_json(root / "content/book.json", book)
    write_json(root / "content/sources.json", sources)
    write_json(root / "content/id-registry.json", registry)
    write_json(root / "content/review-log.json", reviews)
    write_json(root / "content/config.json", {"repository_url": "", "site_url": "", "planned_parts": [{"title": "待规划", "status": "planned"}]})
    for chapter in chapters:
        write_json(root / f"content/chapters/{chapter['id']}.json", chapter)
    web = root / "web"
    web.mkdir()
    (web / "index.html").write_text('<!doctype html><html><head><link rel="stylesheet" href="./styles.css"><script src="./data.js" defer></script><script src="./app.js" defer></script></head><body><main id="main"></main></body></html>', encoding="utf-8")
    (web / "styles.css").write_text("body{color:teal}", encoding="utf-8")
    (web / "app.js").write_text("document.getElementById('main').textContent='fixture';", encoding="utf-8")


class MigrationTests(unittest.TestCase):
    def test_legacy_footnotes_and_prose_survive_roundtrip(self):
        text, sources, audits = fixture()
        book, chapters, migrated_sources, registry, reviews = migrate(text.replace("\n", "\r\n"), sources, audits)
        self.assertEqual(chapters[0]["entries"][0]["fields"]["plain"], "原文，不新增医学结论。")
        self.assertEqual(len(chapters[0]["entries"][0]["source_ids"]), 2)
        self.assertEqual(reviews[0]["clinical_review_status"], "not_clinically_reviewed")
        self.assertNotIn("旧列表", book["back_matter"])
        bundle = {"manifest": {"book": book}, "chapters": [{k: v for k, v in ch.items() if k != "entries"} for ch in chapters], "entries": [e for ch in chapters for e in ch["entries"]], "sources": migrated_sources}
        exported = book_markdown(bundle)
        roundtrip = parse_manuscript(exported)
        original = parse_manuscript(text)
        self.assertEqual(roundtrip["front_matter"], original["front_matter"])
        self.assertEqual(roundtrip["back_matter"], original["back_matter"])
        self.assertEqual(roundtrip["chapters"], original["chapters"])

    def test_missing_or_duplicate_field_fails_before_export(self):
        text, sources, audits = fixture()
        with self.assertRaisesRegex(ContentError, "six fields"):
            migrate(text.replace("**成本：** 示例成本", "", 1), sources, audits)
        with self.assertRaisesRegex(ContentError, "Duplicate field"):
            migrate(text.replace("**成本：** 示例成本", "**成本：** 示例成本\n\n**成本：** 再次", 1), sources, audits)

    def test_unknown_reference_fails(self):
        text, sources, audits = fixture()
        with self.assertRaisesRegex(ContentError, "Unknown reference"):
            migrate(text.replace("导言 [1]", "导言 [999]"), sources, audits)

    def test_audit_drift_is_not_silently_accepted(self):
        text, sources, audits = fixture()
        audits[0]["最终标题"] = "1 另一条"
        with self.assertRaisesRegex(ContentError, "Audit title"):
            migrate(text, sources, audits)

    def test_same_doi_cannot_silently_be_double_counted(self):
        text, sources, audits = fixture()
        sources[1]["citation"] = "Another title. doi:10.1234/EXAMPLE."
        with self.assertRaisesRegex(ContentError, "Duplicate source identity"):
            migrate(text, sources, audits)

    def test_registry_guards_reordering_and_identity_changes(self):
        text, sources, audits = fixture()
        first = migrate(text, sources, audits)
        second = migrate(text, sources, audits, copy.deepcopy(first[3]))
        self.assertEqual(first[3], second[3])
        with self.assertRaisesRegex(ContentError, "reconcile stable IDs"):
            migrate(text.replace("### 1 保留原句", "### 1 修改了标题", 1), sources, audits, copy.deepcopy(first[3]))
        changed_sources = copy.deepcopy(sources)
        changed_sources[0]["citation"] = "doi:10.1234/new-paper."
        with self.assertRaisesRegex(ContentError, "Source identity changed"):
            migrate(text, changed_sources, audits, copy.deepcopy(first[3]))

    def test_evidence_filters_do_not_promote_negative_grade_mentions(self):
        self.assertEqual(evidence_labels("B，不能把配方升为A。"), ["B"])
        self.assertEqual(evidence_labels("B，温敷部分为C，未验证。"), ["B", "C"])
        self.assertEqual(evidence_labels("A仅用于指定结论，不能外推。"), ["A"])
        self.assertEqual(evidence_labels("未分级，不猜测"), [])


class CanonicalTests(unittest.TestCase):
    def test_move_between_chapters_preserves_registered_entry_id(self):
        book, chapters, sources, registry, _ = migrate(*fixture())
        origin, destination = chapters[:2]
        moved = origin["entries"].pop(0)
        identifier = moved["id"]
        original_registry = copy.deepcopy(registry)
        original_fields = copy.deepcopy(moved["fields"])
        destination["entries"].append(moved)
        # Moving the object alone must not bypass its ownership constraints.
        with self.assertRaisesRegex(ContentError, "chapter/unit|unit membership"):
            validate_content(book, chapters, sources, registry)
        moved["chapter_id"] = destination["id"]
        moved["unit_id"] = destination["units"][0]["id"]
        moved["ordinal"] = 2
        # Updating entry fields alone still leaves inconsistent unit membership.
        with self.assertRaisesRegex(ContentError, "unit membership"):
            validate_content(book, chapters, sources, registry)
        origin["units"][0]["entry_ids"].remove(identifier)
        destination["units"][0]["entry_ids"].append(identifier)
        validate_content(book, chapters, sources, registry)
        self.assertEqual(identifier, "eyes-001")
        self.assertEqual(moved["chapter_id"], "nose")
        self.assertEqual(moved["fields"], original_fields)
        self.assertEqual(registry, original_registry)
        # The unchanged legacy-prefix ID remains the exported share-link key.
        with workspace_temp() as root:
            install_fixture(root, (book, chapters, sources, registry, []))
            exported = pack_data(root, built_at=STAMP)
            matches = [entry for entry in exported["entries"] if entry["id"] == identifier]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["chapter_id"], "nose")

    def test_published_edition_has_complete_reference_graph(self):
        book, chapters, sources, registry = load_content(ROOT)
        entries = [entry for chapter in chapters for entry in chapter["entries"]]
        self.assertEqual((len(chapters), len(entries), len(sources)), (7, 66, 170))
        self.assertEqual(len({entry["id"] for entry in entries}), 66)
        self.assertTrue(all(entry["content_checked_at"] == "2026-10-28" for entry in entries))
        self.assertTrue(all(entry["clinical_review_status"] == "not_clinically_reviewed" for entry in entries))
        self.assertTrue(all(list(entry["fields"]) == list(FIELD_NAMES.values()) for entry in entries))

    def test_dangling_citation_or_false_signoff_fails(self):
        book, chapters, sources, registry = load_content(ROOT)
        chapter_copy = copy.deepcopy(chapters)
        chapter_copy[0]["entries"][0]["fields"]["notes"] += " [@src-000000000000]"
        with self.assertRaises(ContentError):
            validate_content(book, chapter_copy, sources, registry)
        chapter_copy = copy.deepcopy(chapters)
        chapter_copy[0]["entries"][0]["clinical_review_status"] = "clinically_reviewed"
        with self.assertRaisesRegex(ContentError, "sign-off"):
            validate_content(book, chapter_copy, sources, registry)

    def test_source_identity_is_deterministic(self):
        a = {"citation": "doi:10.1000/ABC.", "url": "https://example.org/one"}
        b = {"citation": "doi:10.1000/abc.", "url": "https://example.org/other"}
        self.assertEqual(source_id(source_identity(a)), source_id(source_identity(b)))


class ExportTests(unittest.TestCase):
    def test_static_pages_escape_content_and_restrict_external_links(self):
        with workspace_temp() as root:
            install_fixture(root, migrate(*fixture()))
            data = pack_data(root, built_at=STAMP)
            entry = data["entries"][0]
            entry["title"] = '<img src=x onerror="alert(1)">'
            entry["fields"]["plain"] += '<script>alert(2)</script> [安全](https://example.org/?a=1&b=2) [危险](javascript:alert(3)) [文件](file:///secret)'
            data["sources"][0]["citation"] = '<svg onload="alert(4)">恶意书目</svg>'
            # The renderer also rejects unsafe URLs if validation is bypassed.
            data["sources"][0]["url"] = 'javascript:alert(5)'
            html = render_entry_html(data, entry)
            facts = PageFacts(html)
            self.assertFalse({tag for tag, _ in facts.tags} & {"script", "img"})
            # The four fixed navigation icons are trusted template markup. User
            # prose, titles, metadata and source citations must still never emit SVG.
            navigation = list(re.finditer(r'<nav class="static-mobile-nav" aria-label="手机阅读导航">.*?</nav>', html, re.S))
            self.assertEqual(len(navigation), 1)
            allowed = navigation[0]
            nav_facts = PageFacts(allowed.group(0))
            svg_attrs = [attrs for tag, attrs in nav_facts.tags if tag == 'svg']
            self.assertEqual(svg_attrs, [{'class': 'icon', 'aria-hidden': 'true', 'viewbox': '0 0 24 24'}] * 4)
            self.assertEqual(sum(tag == 'svg' for tag, _ in facts.tags), 4)
            self.assertTrue({tag for tag, _ in nav_facts.tags} <= {'nav', 'a', 'svg', 'path', 'circle', 'span'})
            self.assertFalse(any(key.lower().startswith('on') for _, attrs in nav_facts.tags for key in attrs))
            content_facts = PageFacts(html[:allowed.start()] + html[allowed.end():])
            self.assertFalse({tag for tag, _ in content_facts.tags} & {'script', 'img', 'svg'})
            self.assertIn('&lt;script&gt;alert(2)&lt;/script&gt;', html)
            self.assertIn('&lt;img src=x onerror=&quot;alert(1)&quot;&gt;', html)
            self.assertIn('&lt;svg onload=&quot;alert(4)&quot;&gt;恶意书目&lt;/svg&gt;', html)
            self.assertIn('<script>alert(2)</script>', ''.join(facts.text))
            links = [attrs["href"] for tag, attrs in facts.tags if "href" in attrs]
            self.assertIn('https://example.org/?a=1&b=2', links)
            self.assertTrue(all(not urlsplit(link).scheme or urlsplit(link).scheme in {"http", "https"} for link in links))
            for identifier in entry["source_ids"]:
                self.assertIn('#ref-' + identifier, links)
                self.assertTrue(any(attrs.get("id") == 'ref-' + identifier for _, attrs in facts.tags))

    def test_all_66_static_pages_have_six_fields_and_subpath_links(self):
        with workspace_temp() as root:
            book, chapters, sources, registry = load_content(ROOT)
            install_fixture(root, (book, chapters, sources, registry, []))
            build(root, built_at=STAMP)
            pages = list((root / "dist/read").glob("*/index.html"))
            self.assertEqual(len(pages), 66)
            expected = {entry["id"]: entry for chapter in chapters for entry in chapter["entries"]}
            for page in pages:
                identifier = page.parent.name
                entry = expected[identifier]
                facts = PageFacts(page.read_text(encoding="utf-8"))
                self.assertNotIn('script', [tag for tag, _ in facts.tags])
                self.assertTrue(all(any(attrs.get("id") == 'field-' + field for _, attrs in facts.tags) for field in FIELD_NAMES.values()))
                ids = {attrs["id"] for _, attrs in facts.tags if "id" in attrs}
                self.assertTrue({'ref-' + sid for sid in entry["source_ids"]}.issubset(ids))
                links = [attrs["href"] for _, attrs in facts.tags if "href" in attrs]
                self.assertIn('../../#/entry/' + identifier, links)
                self.assertIn('../../#/chapter/' + entry["chapter_id"], links)
                base = 'https://example.org/body-care-guide/read/' + identifier + '/'
                for link in links:
                    if not urlsplit(link).scheme:
                        resolved = urljoin(base, link)
                        self.assertTrue(resolved.startswith('https://example.org/body-care-guide/'), (link, resolved))
                self.assertEqual(urljoin(base, '../../styles.css'), 'https://example.org/body-care-guide/styles.css')
            self.assertFalse((root / 'dist/sitemap.xml').exists())

    def test_sitemap_and_canonical_require_explicit_site_url(self):
        with workspace_temp() as root:
            install_fixture(root, migrate(*fixture()))
            config_path = root / 'content/config.json'
            build(root, built_at=STAMP)
            page = root / 'dist/read/eyes-001/index.html'
            preview = page.read_text(encoding='utf-8')
            self.assertIn('content="noindex, nofollow"', preview)
            self.assertIn('content="noindex, nofollow"', (root / 'dist/index.html').read_text(encoding='utf-8'))
            self.assertIn('content="noindex, nofollow"', (root / 'dist/downloads/guide-offline.html').read_text(encoding='utf-8'))
            self.assertNotIn('rel="canonical"', preview)
            self.assertFalse((root / 'dist/sitemap.xml').exists())
            config = json.loads(config_path.read_text(encoding='utf-8'))
            config['site_url'] = 'https://example.org/body-care-guide/'
            write_json(config_path, config)
            build(root, built_at=STAMP)
            published = page.read_text(encoding='utf-8')
            canonical = 'https://example.org/body-care-guide/read/eyes-001/'
            self.assertIn('rel="canonical" href="' + canonical + '"', published)
            self.assertIn('property="og:url" content="' + canonical + '"', published)
            self.assertNotIn('noindex', published)
            self.assertNotIn('noindex', (root / 'dist/index.html').read_text(encoding='utf-8'))
            sitemap = ET.parse(root / 'dist/sitemap.xml')
            locations = [item.text for item in sitemap.findall('.//{*}loc')]
            self.assertEqual(len(locations), 8)
            self.assertIn(canonical, locations)
            self.assertTrue(all(value.startswith(config['site_url']) for value in locations))
            # Unsetting a previously configured URL must remove stale public URLs.
            config['site_url'] = ''
            write_json(config_path, config)
            build(root, built_at=STAMP)
            self.assertFalse((root / 'dist/sitemap.xml').exists())
            self.assertNotIn('rel="canonical"', page.read_text(encoding='utf-8'))

    def test_check_is_read_only_and_build_produces_all_downloads(self):
        with workspace_temp() as root:
            install_fixture(root, migrate(*fixture()))
            manifest = build(root, check_only=True, built_at=STAMP)
            self.assertFalse((root / "dist").exists())
            build(root, built_at=STAMP)
            self.assertEqual(manifest["content_checked_at"], "2026-10-28")
            self.assertEqual(manifest["build_at"], STAMP)
            for file in ("api/v1/entries.json", "api/v1/sources.json", "api/v1/chapters.json", "api/v1/manifest.json", "downloads/guide.md", "downloads/guide.json", "downloads/guide-offline.html", "data.js", ".nojekyll"):
                self.assertTrue((root / "dist" / file).is_file(), file)
            entries = json.loads((root / "dist/api/v1/entries.json").read_text(encoding="utf-8"))
            self.assertEqual(entries["schema_version"], "1.0.0")
            self.assertEqual(len(entries["entries"]), 7)
            self.assertNotIn("[@src-", (root / "dist/downloads/guide.md").read_text(encoding="utf-8"))

    def test_data_cannot_close_inline_script(self):
        source = {"text": "</script><script>bad()</script>\u2028"}
        script = data_script(source)
        self.assertNotIn("</script", script.lower())
        self.assertEqual(json.loads(script[len("window.__GUIDE_DATA__="):-2]), source)

    def test_inline_export_does_not_rely_on_defer_or_network_assets(self):
        index = '<html><head><link rel="stylesheet" href="styles.css"><script src="data.js" defer></script><script src="app.js" defer></script></head><body><main></main></body></html>'
        html = inline_offline(index, "body{color:teal}", "console.log('app')", "window.__GUIDE_DATA__={};")
        self.assertNotRegex(html, r"src=['\"](?:data|app)\.js")
        self.assertNotIn('href="styles.css"', html)
        self.assertGreater(html.index("window.__GUIDE_DATA__"), html.index("</main>"))
        self.assertLess(html.index("window.__GUIDE_DATA__"), html.index("console.log"))
        with self.assertRaises(ContentError):
            inline_offline(index.replace('src="app.js"', 'src="data.js"'), "", "", "")

    def test_invalid_future_status_is_not_published(self):
        with workspace_temp() as root:
            install_fixture(root, migrate(*fixture()))
            write_json(root / "content/config.json", {"planned_parts": [{"title": "尚无内容", "status": "published"}]})
            with self.assertRaisesRegex(ContentError, "planned"):
                pack_data(root, built_at=STAMP)


if __name__ == "__main__":
    unittest.main()
