"""One-time migration from the existing manuscript. No network or medical rewriting."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from .content_model import (CHAPTER_NAMES, CHECKED_AT, CONTENT_VERSION, SCHEMA_VERSION,
        ContentError, convert_references, editorial_tags, evidence_labels, parse_manuscript,
        read_json, reference_numbers, source_id, source_identity, validate_content, write_json)
except ImportError:
    from content_model import (CHAPTER_NAMES, CHECKED_AT, CONTENT_VERSION, SCHEMA_VERSION,
        ContentError, convert_references, editorial_tags, evidence_labels, parse_manuscript,
        read_json, reference_numbers, source_id, source_identity, validate_content, write_json)

ROOT = Path(__file__).resolve().parents[1]


def migrate(markdown: str, legacy_sources: list[dict], audits: list[dict], existing_registry=None):
    parsed = parse_manuscript(markdown)
    registry = existing_registry or {"schema_version": SCHEMA_VERSION, "edition": CHECKED_AT, "entries": {}, "units": {}, "sources": {}}
    sources = []
    number_to_id = {}
    identities = set()
    aliases = {}
    for row in legacy_sources:
        if type(row.get("number")) is not int or row["number"] in number_to_id:
            raise ContentError(f"Missing/duplicate legacy source number: {row.get('number')}")
        identity = source_identity(row)
        if identity in identities:
            raise ContentError(f"Duplicate source identity must be reconciled explicitly: {identity}")
        identities.add(identity)
        legacy_id = row["id"]
        previous = registry["sources"].get(legacy_id)
        if previous and previous["identity"] != identity:
            raise ContentError(f"Source identity changed; review the registry explicitly: {legacy_id}")
        identifier = previous["id"] if previous else source_id(identity)
        registry["sources"][legacy_id] = {"id": identifier, "identity": identity, "legacy_number": row["number"]}
        number_to_id[row["number"]] = identifier
        source = {"id": identifier, "number": row["number"], "citation": row["citation"], "url": row["url"], "type": row.get("type", ""),
                  "support": row.get("支持结论", ""), "limitations": row.get("局限", ""), "legacy_id": legacy_id,
                  "legacy_aliases": list(dict.fromkeys([legacy_id] + row.get("aliases", []))), "content_checked_at": row.get("review_edition")}
        for alias in source["legacy_aliases"]:
            if alias in aliases and aliases[alias] != identifier:
                raise ContentError(f"Ambiguous legacy source alias: {alias}")
            aliases[alias] = identifier
        sources.append(source)
    sources.sort(key=lambda source: source["number"])
    audit_lookup = {}
    for row in audits:
        key = (row["章节"], int(row["条目"]))
        if key in audit_lookup:
            raise ContentError(f"Duplicate evidence audit: {key}")
        audit_lookup[key] = row
    chapters = []
    review_log = []
    used_audits = set()
    for chapter in parsed["chapters"]:
        chapter_id = chapter["id"]
        chapter["intro"] = convert_references(chapter["intro"], number_to_id)
        ordinal_to_id = {}
        for entry in chapter["entries"]:
            key = f"{chapter_id}:{entry['ordinal']}"
            prior = registry["entries"].get(key)
            if prior and prior["import_title"] != entry["title"]:
                raise ContentError(f"Entry title/position changed; reconcile stable IDs before re-import: {key}")
            identifier = prior["id"] if prior else f"{chapter_id}-{entry['ordinal']:03d}"
            registry["entries"][key] = {"id": identifier, "import_title": entry["title"]}
            audit_key = (CHAPTER_NAMES[chapter_id], entry["ordinal"])
            if audit_key not in audit_lookup:
                raise ContentError(f"Missing evidence audit: {audit_key}")
            audit = audit_lookup[audit_key]
            used_audits.add(audit_key)
            if audit["最终标题"] != f"{entry['ordinal']} {entry['title']}":
                raise ContentError(f"Audit title does not match current manuscript: {audit_key}")
            # Some later editorial citations appear only in benefits or notes.
            # Preserve every field; link the complete union rather than rewriting it.
            cited = reference_numbers("\n".join(entry["fields"].values()))
            if set(cited) != set(audit["最终文献号"]):
                raise ContentError(f"Audit source numbers do not match current manuscript: {audit_key}")
            entry["id"] = identifier
            entry["chapter_id"] = chapter_id
            entry["evidence_labels"] = evidence_labels(entry["fields"]["evidence"])
            entry["tags"] = editorial_tags(entry["title"], entry["fields"])
            entry["source_ids"] = [number_to_id[number] for number in cited]
            entry["fields"] = {name: convert_references(value, number_to_id) for name, value in entry["fields"].items()}
            entry["content_checked_at"] = CHECKED_AT
            entry["clinical_review_status"] = "not_clinically_reviewed"
            ordinal_to_id[entry["ordinal"]] = identifier
            review_log.append({"entry_id": identifier, "content_checked_at": CHECKED_AT, "clinical_review_status": "not_clinically_reviewed", "legacy_audit": audit})
        for unit in chapter["units"]:
            key = unit["id"]
            old_title = registry["units"].get(key, {}).get("import_title")
            if old_title is not None and old_title != unit["title"]:
                raise ContentError(f"Unit title/order changed; reconcile registry: {key}")
            registry["units"][key] = {"id": key, "import_title": unit["title"]}
            unit["intro"] = convert_references(unit["intro"], number_to_id)
            unit["entry_ids"] = [ordinal_to_id[number] for number in unit.pop("entry_ordinals")]
        chapters.append(chapter)
    if used_audits != set(audit_lookup):
        raise ContentError("Some audits have no corresponding entry")
    book = {"schema_version": SCHEMA_VERSION, "content_version": CONTENT_VERSION, "title": "五官与头部护理指南", "language": "zh-CN",
            "content_checked_at": CHECKED_AT, "clinical_review_status": "not_clinically_reviewed", "chapter_ids": [chapter["id"] for chapter in chapters],
            "front_matter": convert_references(parsed["front_matter"], number_to_id), "back_matter": convert_references(parsed["back_matter"], number_to_id),
            "tags_note": "标签仅按少量文字关键词作编辑分类，不是医学分诊、产品评级或个体建议。",
            "review_note": "案头核查现有关键证据与推导；未获得医生签审，不是穷尽文献或原始数据重算。"}
    validate_content(book, chapters, sources, registry)
    return book, chapters, sources, registry, review_log


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manuscript", required=True, type=Path)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--audits", required=True, type=Path)
    args = parser.parse_args(argv)
    content = ROOT / "content"
    registry_path = content / "id-registry.json"
    old_registry = read_json(registry_path) if registry_path.exists() else None
    result = migrate(args.manuscript.read_text(encoding="utf-8-sig"), read_json(args.sources), read_json(args.audits), old_registry)
    book, chapters, sources, registry, reviews = result
    # Validate before creating or updating any canonical data.
    write_json(content / "book.json", book)
    write_json(content / "sources.json", sources)
    write_json(content / "id-registry.json", registry)
    write_json(content / "review-log.json", reviews)
    for chapter in chapters:
        write_json(content / "chapters" / f"{chapter['id']}.json", chapter)
    print(json.dumps({"chapters": len(chapters), "entries": sum(len(chapter["entries"]) for chapter in chapters), "sources": len(sources), "medical_rewrite": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContentError, OSError) as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
