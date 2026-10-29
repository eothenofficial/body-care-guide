"""Validate and build a portable static guide with the Python standard library."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

try:
    from .content_model import (FIELD_NAMES, SCHEMA_VERSION, STABLE_REF, ContentError,
                                load_content, read_json, write_json)
    from .static_pages import preview_index_html, site_base, write_static_pages
except ImportError:
    from content_model import (FIELD_NAMES, SCHEMA_VERSION, STABLE_REF, ContentError,
                               load_content, read_json, write_json)
    from static_pages import preview_index_html, site_base, write_static_pages

ROOT = Path(__file__).resolve().parents[1]
FIELD_LABELS = {value: key for key, value in FIELD_NAMES.items()}


def build_time() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    stamp = datetime.fromtimestamp(int(epoch), timezone.utc) if epoch else datetime.now(timezone.utc)
    return stamp.isoformat(timespec="seconds").replace("+00:00", "Z")


def pack_data(root: Path = ROOT, built_at: str | None = None) -> dict:
    book, chapters, sources, _ = load_content(root)
    config = read_json(root / "content" / "config.json")
    for part in config.get("planned_parts", []):
        if part.get("status") != "planned":
            raise ContentError("Future parts must be marked planned; they have no published content")
    for key in ("repository_url", "site_url"):
        if config.get(key) and not config[key].startswith("https://"):
            raise ContentError(f"{key} must be empty or an HTTPS URL")
    site_base(config.get("site_url", ""))
    entries = [entry for chapter in chapters for entry in sorted(chapter["entries"], key=lambda value: value["ordinal"])]
    chapter_index = [{key: value for key, value in chapter.items() if key != "entries"} for chapter in chapters]
    manifest = {
        "schema_version": SCHEMA_VERSION, "content_version": book["content_version"],
        "title": config.get("title", book["title"]), "language": book["language"],
        "entry_count": len(entries), "source_count": len(sources), "chapter_count": len(chapters),
        "content_checked_at": book["content_checked_at"], "status": "research_draft",
        "clinical_review_status": book["clinical_review_status"],
        "repository_url": config.get("repository_url", ""), "site_url": config.get("site_url", ""),
        "build_at": built_at or build_time(), "planned_parts": config.get("planned_parts", []),
        "api": {name: f"api/v1/{name}.json" for name in ("manifest", "entries", "sources", "chapters")},
        "downloads": {"markdown": "downloads/guide.md", "json": "downloads/guide.json", "offline": "downloads/guide-offline.html"},
        "book": {"title": book["title"], "front_matter": book["front_matter"], "back_matter": book["back_matter"],
                 "tags_note": book["tags_note"], "review_note": book["review_note"]},
    }
    return {"manifest": manifest, "entries": entries, "sources": sources, "chapters": chapter_index}


def envelope(data: dict, key: str) -> dict:
    return {"schema_version": data["manifest"]["schema_version"], "content_version": data["manifest"]["content_version"], key: data[key]}


def restore_references(text: str, numbers: dict[str, int]) -> str:
    def replace(match):
        identifier = match.group(1)
        if identifier not in numbers:
            raise ContentError(f"Unknown source in Markdown export: {identifier}")
        return f"[{numbers[identifier]}]"
    return STABLE_REF.sub(replace, text)


def book_markdown(data: dict) -> str:
    numbers = {source["id"]: source["number"] for source in data["sources"]}
    entry_lookup = {entry["id"]: entry for entry in data["entries"]}
    book = data["manifest"]["book"]
    blocks = [book["front_matter"]]
    for chapter in data["chapters"]:
        blocks.extend([f"# {chapter['title']} {chapter['subtitle']}".rstrip(), chapter["intro"]])
        for unit in chapter["units"]:
            blocks.extend(["## " + unit["title"], unit["intro"]])
            for identifier in unit["entry_ids"]:
                entry = entry_lookup[identifier]
                blocks.append(f"### {entry['ordinal']} {entry['title']}")
                for field, label in FIELD_LABELS.items():
                    blocks.append(f"**{label}：** {entry['fields'][field]}")
    blocks.extend([book["back_matter"], "# 参考文献"])
    for source in sorted(data["sources"], key=lambda value: value["number"]):
        citation = source["citation"].strip()
        url = source["url"]
        if citation.endswith(url):
            citation = citation[:-len(url)].rstrip()
        blocks.append(f"[{source['number']}] {citation} [原文]({url})")
    return restore_references("\n\n".join(block for block in blocks if block), numbers).strip() + "\n"


def data_script(data: dict) -> str:
    # '<' escaping prevents user-authored strings from closing an inline script.
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return "window.__GUIDE_DATA__=" + payload + ";\n"


def inline_offline(index: str, styles: str, app: str, script: str, favicon: str | None = None) -> str:
    style_pattern = re.compile(r'<link\b[^>]*\bhref=["\'](?:\./)?styles\.css["\'][^>]*>', re.I)
    script_pattern = re.compile(r'<script\b[^>]*\bsrc=["\'](?:\./)?(?:data|app)\.js["\'][^>]*>\s*</script\s*>', re.I)
    if len(style_pattern.findall(index)) != 1:
        raise ContentError("index.html must link styles.css exactly once")
    if len(script_pattern.findall(index)) != 2:
        raise ContentError("index.html must load data.js and app.js exactly once")
    for name in ("data", "app"):
        if len(re.findall(r'<script\b[^>]*\bsrc=["\'](?:\./)?' + name + r'\.js["\']', index, re.I)) != 1:
            raise ContentError("index.html must load data.js and app.js exactly once")
    if not re.search(r"</body\s*>", index, re.I):
        raise ContentError("index.html must have a closing body element")
    safe_styles = re.sub(r"</style", lambda match: "<\\/style", styles, flags=re.I)
    safe_app = re.sub(r"</script", lambda match: "<\\/script", app, flags=re.I)
    index = style_pattern.sub(lambda match: "<style>\n" + safe_styles + "\n</style>", index)
    index = script_pattern.sub("", index)
    if favicon is not None:
        index = re.sub(r'(<link\b[^>]*\bhref=["\'])(?:\./)?favicon\.svg(["\'])',
                       lambda match: match.group(1) + "data:image/svg+xml," + quote(favicon, safe="") + match.group(2), index, flags=re.I)
    scripts = "<script>\n" + script + "</script>\n<script>\n" + safe_app + "\n</script>\n"
    # Inline scripts cannot use defer. Run after the DOM has been parsed instead.
    index = re.sub(r"</body\s*>", lambda match: scripts + match.group(0), index, count=1, flags=re.I)
    return index


def validate_web(root: Path) -> dict[str, str]:
    web = root / "web"
    contents = {}
    for name in ("index.html", "styles.css", "app.js"):
        path = web / name
        if not path.is_file():
            raise ContentError(f"Missing frontend input: web/{name}")
        contents[name] = path.read_text(encoding="utf-8-sig")
    # The same inlining checks are used in --check and a real build.
    inline_offline(contents["index.html"], contents["styles.css"], contents["app.js"], "")
    return contents


def build(root: Path = ROOT, check_only=False, output: Path | None = None, built_at=None) -> dict:
    data = pack_data(root, built_at)
    web = validate_web(root)
    web["index.html"] = preview_index_html(web["index.html"], data["manifest"]["site_url"])
    if check_only:
        return data["manifest"]
    dist = output or root / "dist"
    dist = dist.resolve()
    if not dist.is_relative_to(root.resolve()) or dist == root.resolve():
        raise ContentError("Build output must be a subdirectory of the project")
    dist.mkdir(parents=True, exist_ok=True)
    for asset in sorted((root / "web").rglob("*")):
        if asset.is_symlink():
            raise ContentError(f"Frontend symlinks are not copied: {asset.name}")
        if asset.is_file():
            target = dist / asset.relative_to(root / "web")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(asset, target)
    (dist / "index.html").write_text(web["index.html"], encoding="utf-8")
    api = dist / "api" / "v1"
    for key in ("entries", "sources", "chapters"):
        write_json(api / f"{key}.json", envelope(data, key))
    write_json(api / "manifest.json", data["manifest"])
    script = data_script(data)
    (dist / "data.js").write_text(script, encoding="utf-8")
    (dist / ".nojekyll").write_text("", encoding="utf-8")
    downloads = dist / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    (downloads / "guide.md").write_text(book_markdown(data), encoding="utf-8")
    write_json(downloads / "guide.json", data)
    favicon_path = root / "web" / "favicon.svg"
    offline = inline_offline(web["index.html"], web["styles.css"], web["app.js"], script,
                             favicon_path.read_text(encoding="utf-8") if favicon_path.exists() else None)
    (downloads / "guide-offline.html").write_text(offline, encoding="utf-8")
    write_static_pages(data, dist)
    return data["manifest"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate content and frontend contracts without writing outputs")
    args = parser.parse_args(argv)
    manifest = build(check_only=args.check)
    print(json.dumps({"mode": "check" if args.check else "build", "entries": manifest["entry_count"],
                      "sources": manifest["source_count"], "chapters": manifest["chapter_count"],
                      "content_checked_at": manifest["content_checked_at"], "build_at": manifest["build_at"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContentError, OSError, ValueError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
