"""Pre-render shareable entry pages without JavaScript or third-party packages."""
from __future__ import annotations

import re
from html import escape
from pathlib import Path
from urllib.parse import quote, urlsplit
from xml.etree import ElementTree as ET

try:
    from .content_model import FIELD_NAMES, ContentError
except ImportError:
    from content_model import FIELD_NAMES, ContentError


INLINE_TOKEN = re.compile(
    r"\[@(src-[0-9a-f]{12})\]|\[([^\]\n]+)\]\(([^)\n]+)\)|\*\*([^*\n]+)\*\*"
)


def safe_external_url(value: str) -> str | None:
    """Only explicit HTTP(S) destinations can become external hyperlinks."""
    if not isinstance(value, str) or re.search(r"[\x00-\x20\x7f]", value):
        return None
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username:
            return None
        _ = parsed.port  # Reject malformed ports rather than emitting broken links.
    except ValueError:
        return None
    return value


def site_base(value: str) -> str | None:
    """Use a configured public origin/subpath; never infer one from preview hosts."""
    if not value:
        return None
    if not safe_external_url(value) or urlsplit(value).scheme != "https":
        raise ContentError("site_url must be empty or a valid HTTPS base URL")
    parsed = urlsplit(value)
    if parsed.query or parsed.fragment:
        raise ContentError("site_url must not contain a query or fragment")
    return value.rstrip("/") + "/"


def render_inline(text: str, sources: dict) -> str:
    """Render a small Markdown subset; all source text starts as escaped text."""
    pieces = []
    position = 0
    for match in INLINE_TOKEN.finditer(text):
        pieces.append(escape(text[position:match.start()]))
        identifier, label, url, strong = match.groups()
        if identifier:
            if identifier not in sources:
                raise ContentError(f"Static page cites an unknown source: {identifier}")
            number = sources[identifier]["number"]
            pieces.append(f'<a class="citation" href="#ref-{escape(identifier)}" aria-label="来源 {number}">[{number}]</a>')
        elif label is not None and safe_external_url(url):
            pieces.append(f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>')
        elif strong is not None:
            pieces.append("<strong>" + escape(strong) + "</strong>")
        else:
            pieces.append(escape(match.group(0)))
        position = match.end()
    pieces.append(escape(text[position:]))
    return "".join(pieces).replace("\n", "<br>\n")


def render_prose(value, sources: dict) -> str:
    if isinstance(value, list):
        value = "；".join(str(item) for item in value)
    paragraphs = re.split(r"\n\s*\n", str(value or "").strip())
    return "\n".join("<p>" + render_inline(part, sources) + "</p>" for part in paragraphs if part)


def entry_url(base: str, identifier: str) -> str:
    return base + "read/" + quote(identifier, safe="") + "/"


def preview_index_html(index: str, configured_site_url: str) -> str:
    """Keep an unconfigured preview homepage out of search results as well."""
    if site_base(configured_site_url):
        return index
    if not re.search(r"</head\s*>", index, re.I):
        raise ContentError("index.html must have a closing head element")
    index = re.sub(r'<meta\b(?=[^>]*\bname=["\']robots["\'])[^>]*>', "", index, flags=re.I)
    return re.sub(r"</head\s*>", '<meta name="robots" content="noindex, nofollow">\n</head>', index, count=1, flags=re.I)


def render_entry_html(data: dict, entry: dict) -> str:
    manifest = data["manifest"]
    chapter = next(item for item in data["chapters"] if item["id"] == entry["chapter_id"])
    source_lookup = {item["id"]: item for item in data["sources"]}
    title = entry["title"] + " · " + manifest["title"]
    description = (entry["title"] + "。" + manifest["title"] + "的" + chapter["title"]
                   + "护理条目，含成本、说人话、收益、证据等级、来源与备注。资料核对日期："
                   + entry["content_checked_at"] + "；研究修订稿，未完成临床签审。")
    metadata = [
        '<meta name="description" content="' + escape(description) + '">',
        '<meta property="og:title" content="' + escape(title) + '">',
        '<meta property="og:description" content="' + escape(description) + '">',
        '<meta property="og:type" content="article">',
    ]
    base = site_base(manifest.get("site_url", ""))
    if base:
        canonical = escape(entry_url(base, entry["id"]))
        metadata.extend(['<link rel="canonical" href="' + canonical + '">',
                         '<meta property="og:url" content="' + canonical + '">'])
    else:
        metadata.append('<meta name="robots" content="noindex, nofollow">')
    sections = []
    for label, field in FIELD_NAMES.items():
        sections.append('<section class="reading-field" aria-labelledby="field-' + field + '">'
                        + '<h2 id="field-' + field + '">' + escape(label) + '</h2>'
                        + '<div class="prose">' + render_prose(entry["fields"][field], source_lookup) + '</div></section>')
    footnotes = []
    for identifier in entry["source_ids"]:
        source = source_lookup[identifier]
        note = ['<li id="ref-' + escape(identifier) + '" value="' + str(source["number"]) + '">',
                render_prose(source["citation"], source_lookup)]
        url = safe_external_url(source["url"])
        if url:
            note.append('<p><a href="' + escape(url) + '" target="_blank" rel="noopener noreferrer">查看原始来源 ↗</a></p>')
        if source.get("support"):
            note.append('<div><strong>支持范围：</strong>' + render_prose(source["support"], source_lookup) + '</div>')
        if source.get("limitations"):
            note.append('<div><strong>局限：</strong>' + render_prose(source["limitations"], source_lookup) + '</div>')
        note.append('</li>')
        footnotes.append("\n".join(note))
    interactive = "../../#/entry/" + quote(entry["id"], safe="")
    chapter_link = "../../#/chapter/" + quote(entry["chapter_id"], safe="")
    return "\n".join([
        '<!doctype html>', '<html lang="zh-CN"><head>', '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>' + escape(title) + '</title>', *metadata,
        '<link rel="stylesheet" href="../../styles.css">',
        '<style>.static-reader .main{max-width:900px;margin:auto;padding:40px 24px 70px}'
        '.static-reader .reading-field{margin:32px 0}.static-reader h2{font-size:20px}'
        '.static-reader .source-list{padding-left:28px;font-size:13px;line-height:1.9;overflow-wrap:anywhere}'
        '.static-reader .source-list li{padding:20px 8px;border-top:1px solid var(--line)}'
        '.static-reader .source-list p{margin:6px 0}.static-reader a:not(.button){color:var(--green);text-decoration:underline}'
        '.static-reader .reading-field .prose{font-size:16px}.static-reader :target{scroll-margin-top:20px}'
        '@media print{.static-reader .main{padding:0}.static-reader .source-list{font-size:9pt}}</style>',
        '</head><body class="static-reader"><main class="main article" id="main">',
        '<nav class="breadcrumb" aria-label="阅读导航"><a href="../../">' + escape(manifest["title"]) + '</a> / '
        + '<a href="' + escape(chapter_link) + '">' + escape(chapter["title"]) + '</a></nav>',
        '<header class="page-head"><h1>' + escape(entry["title"]) + '</h1>',
        '<p class="page-lead">' + escape(chapter["title"]) + ' · 第 ' + str(entry["ordinal"]) + ' 条 · 资料核对 '
        + escape(entry["content_checked_at"]) + ' · 未临床签审</p>',
        '<div class="action-row article-actions"><a class="button primary" href="' + escape(interactive) + '">进入交互阅读</a>'
        + '<a class="button" href="' + escape(chapter_link) + '">返回章节目录</a></div></header>',
        '<article>', *sections, '</article>',
        '<section aria-labelledby="references"><h2 id="references">本条全部来源</h2><ol class="source-list">',
        *footnotes, '</ol></section>',
        '<footer class="provenance-note">此页保留完整条目和引用，关闭 JavaScript 也能阅读。'
        '内容版本 ' + escape(manifest["content_version"]) + '；研究修订稿，未完成临床签审。</footer>',
        '</main></body></html>', "",
    ])


def sitemap_xml(data: dict, base: str) -> str:
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in [base] + [entry_url(base, entry["id"]) for entry in data["entries"]]:
        ET.SubElement(ET.SubElement(urlset, "url"), "loc").text = url
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(urlset, encoding="unicode") + "\n"


def write_static_pages(data: dict, dist: Path) -> None:
    for entry in data["entries"]:
        target = dist / "read" / entry["id"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_entry_html(data, entry), encoding="utf-8")
    sitemap = dist / "sitemap.xml"
    base = site_base(data["manifest"].get("site_url", ""))
    if base:
        sitemap.write_text(sitemap_xml(data, base), encoding="utf-8")
    elif sitemap.exists():
        # Remove only our known generated file if a previous public URL was unset.
        sitemap.unlink()
