"""Zero-dependency content model. This module never interprets medical claims."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

SCHEMA_VERSION = "1.0.0"
CONTENT_VERSION = "2026.10.28-1"
CHECKED_AT = "2026-10-28"
CHAPTER_NAMES = {
    "eyes": "眼睛", "nose": "鼻子", "lips": "嘴唇", "oral": "口腔",
    "ears": "耳朵", "skin": "面部皮肤", "hair": "头发",
}
FIELD_NAMES = {
    "成本": "cost", "说人话": "plain", "收益": "benefit",
    "证据等级": "evidence", "来源": "sources", "备注": "notes",
}
NUMERIC_REF = re.compile(r"(?<!!)\[(\d+)\](?!\()")
STABLE_REF = re.compile(r"\[@(src-[0-9a-f]{12})\]")
AGE_GROUP_LABELS = {"child": "儿童（0–11岁）", "teen": "青少年（12–17岁）",
                    "adult": "成人（18–64岁）", "older": "老年（65岁及以上）"}
SEX_LABELS = {"all": "男女通用", "female": "女性", "male": "男性"}
FIELD = re.compile(r"^\*\*(成本|说人话|收益|证据等级|来源|备注)：\*\*\s*(.*)$")
TAGS = {
    "习惯": ("每天", "日常", "睡前", "清洁", "洗脸", "洗头", "刷牙", "休息", "修剪", "剃须", "温敷", "舔唇"),
    "消费": ("购买", "产品", "用品", "配方", "品牌", "套餐", "多花钱"),
    "症状": ("症状", "疼痛", "干涩", "出血", "红肿", "听不清", "眼红", "瘙痒"),
    "专业服务": ("就诊", "医生", "验光", "验配", "复查", "医美", "正畸", "洗牙", "机构", "处方"),
}


class ContentError(ValueError):
    """An actionable migration or content-validation failure."""


def validate_audience(entry: dict, required: bool = False) -> None:
    """Validate editorial readership metadata, never infer treatment eligibility."""
    audience = entry.get("audience")
    if audience is None and not required:
        return
    identifier = entry.get("id", "unknown")
    if not isinstance(audience, dict):
        raise ContentError(f"Missing/invalid audience: {identifier}")
    for key, allowed in (("age_groups", AGE_GROUP_LABELS), ("sexes", SEX_LABELS)):
        values = audience.get(key)
        if (not isinstance(values, list) or not values
                or any(not isinstance(v, str) or v not in allowed for v in values)
                or len(set(values)) != len(values)):
            raise ContentError(f"Invalid audience {key}: {identifier}")
    if "all" in audience["sexes"] and len(audience["sexes"]) != 1:
        raise ContentError(f"Ambiguous audience sexes: {identifier}")
    note = audience.get("scope_note")
    if (not isinstance(note, str) or not note.strip()
            or re.search(r"[\r\n|<>]|\[@|\]\(", note)):
        raise ContentError(f"Audience scope_note must be plain text: {identifier}")
    if type(audience.get("safety_pin")) is not bool:
        raise ContentError(f"Invalid audience safety_pin: {identifier}")


def audience_caption(entry: dict) -> str:
    audience = entry.get("audience")
    if not audience:
        return ""
    age = "、".join(AGE_GROUP_LABELS[g] for g in audience["age_groups"])
    sex = "、".join(SEX_LABELS[s] for s in audience["sexes"])
    suffix = "；急症提示" if audience["safety_pin"] else ""
    return f"阅读侧重：{age}；{sex}。{audience['scope_note']}{suffix}。年龄分组用于导览，不代表治疗资格。"


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise ContentError(f"Cannot read JSON {path}: {exc}") from exc


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_newlines(value: str) -> str:
    return value.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")


def reference_numbers(text: str) -> list[int]:
    return list(dict.fromkeys(int(match) for match in NUMERIC_REF.findall(text)))


def source_identity(source: dict) -> str:
    """DOI first; otherwise URL. Identity is recorded, not recomputed on edits."""
    match = re.search(r"\bdoi:\s*(10\.\d{4,9}/\S+)", source["citation"], re.I)
    if match:
        return "doi:" + match.group(1).rstrip(".,;，。；").lower()
    parts = urlsplit(source["url"].strip())
    if parts.scheme not in {"https", "http"} or not parts.netloc:
        raise ContentError(f"Source {source.get('id')} has a non-HTTP URL")
    return "url:" + urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), parts.query, ""))


def source_id(identity: str) -> str:
    return "src-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]


def convert_references(text: str, number_to_id: dict[int, str]) -> str:
    def replace(match):
        number = int(match.group(1))
        if number not in number_to_id:
            raise ContentError(f"Unknown reference [{number}]")
        return f"[@{number_to_id[number]}]"
    return NUMERIC_REF.sub(replace, text)


def evidence_labels(text: str) -> list[str]:
    """Only explicit grade declarations; retain the entire original grade text."""
    labels = []
    first = re.match(r"\s*([ABC])(?=[^A-Za-z]|$)", text)
    if first:
        labels.append(first.group(1))
    # Explicit secondary grade declarations such as '部分为C' or '主要为C级'.
    for match in re.finditer(r"(?:部分|主要)(?:是|为|依据)?\s*([ABC])(?=级|[，,。；;])", text):
        if match.group(1) not in labels:
            labels.append(match.group(1))
    return labels


def editorial_tags(title: str, fields: dict) -> list[str]:
    text = title + "\n" + fields["plain"] + "\n" + fields["notes"]
    return [tag for tag, words in TAGS.items() if any(word in text for word in words)]


def parse_manuscript(markdown: str) -> dict:
    """Parse the legacy six-field manuscript, preserving all narrative Markdown."""
    lines = normalize_newlines(markdown).splitlines()
    chapters = []
    chapter = unit = entry = None
    intro_lines = []
    trailing_lines = []
    destination = intro_lines

    def finish_entry():
        nonlocal entry
        if entry is None:
            return
        fields = {}
        current = None
        order = []
        for line in entry.pop("_lines"):
            match = FIELD.match(line)
            if match:
                current = FIELD_NAMES[match.group(1)]
                if current in fields:
                    raise ContentError(f"Duplicate field {current}: {entry['title']}")
                fields[current] = [match.group(2)]
                order.append(current)
            elif current:
                fields[current].append(line)
            elif line.strip():
                raise ContentError(f"Text before six fields: {entry['title']}")
        if order != list(FIELD_NAMES.values()):
            raise ContentError(f"Expected six fields in order: {entry['title']}; got {order}")
        entry["fields"] = {key: "\n".join(value).strip() for key, value in fields.items()}
        if any(not value for value in entry["fields"].values()):
            raise ContentError(f"Empty field: {entry['title']}")
        chapter["entries"].append(entry)
        unit["entry_ordinals"].append(entry["ordinal"])
        entry = None

    def finish_unit():
        nonlocal unit
        finish_entry()
        if unit is not None:
            unit["intro"] = "\n".join(unit.pop("_lines")).strip()
            unit = None

    def finish_chapter():
        nonlocal chapter
        finish_unit()
        if chapter is not None:
            chapter["intro"] = "\n".join(chapter.pop("_lines")).strip()
            ordinals = [item["ordinal"] for item in chapter["entries"]]
            if len(set(ordinals)) != len(ordinals) or ordinals != list(range(1, len(ordinals) + 1)):
                raise ContentError(f"Legacy entry numbering is not sequential: {chapter['id']}")
            chapter = None

    for line_number, line in enumerate(lines, 1):
        h1 = re.fullmatch(r"# (.+)", line)
        h2 = re.fullmatch(r"## (.+)", line)
        h3 = re.fullmatch(r"### ([1-9]\d*) (.+)", line)
        if h1:
            finish_chapter()
            heading = h1.group(1)
            key = next((key for key, name in CHAPTER_NAMES.items() if heading == name or heading.startswith(name + " ")), None)
            if key:
                if any(item["id"] == key for item in chapters):
                    raise ContentError(f"Duplicate chapter {key}")
                chapter = {"id": key, "title": CHAPTER_NAMES[key], "subtitle": heading[len(CHAPTER_NAMES[key]):].strip(), "order": len(chapters) + 1, "_lines": [], "units": [], "entries": []}
                chapters.append(chapter)
            else:
                destination = trailing_lines if chapters else intro_lines
                destination.append(line)
            continue
        if chapter is None:
            destination.append(line)
        elif h2:
            finish_unit()
            unit = {"id": f"{chapter['id']}-u{len(chapter['units']) + 1}", "title": h2.group(1), "order": len(chapter["units"]) + 1, "_lines": [], "entry_ordinals": []}
            chapter["units"].append(unit)
        elif h3:
            if unit is None:
                raise ContentError(f"Entry has no unit at line {line_number}")
            finish_entry()
            entry = {"ordinal": int(h3.group(1)), "title": h3.group(2), "unit_id": unit["id"], "_lines": []}
        elif line.startswith("### "):
            raise ContentError(f"Unsupported entry heading at line {line_number}: {line}")
        elif entry is not None:
            entry["_lines"].append(line)
        elif unit is not None:
            unit["_lines"].append(line)
        else:
            chapter["_lines"].append(line)
    finish_chapter()
    if set(item["id"] for item in chapters) != set(CHAPTER_NAMES):
        raise ContentError("Expected all seven known chapters")
    trailing = "\n".join(trailing_lines).strip()
    # The source ledger is canonical; do not import a second mutable bibliography.
    back_matter = re.split(r"(?m)^# 参考文献\s*$", trailing, maxsplit=1)[0].strip()
    return {"front_matter": "\n".join(intro_lines).strip(), "back_matter": back_matter, "chapters": chapters}


def validate_content(book: dict, chapters: list[dict], sources: list[dict], registry: dict) -> None:
    if book.get("schema_version") != SCHEMA_VERSION or registry.get("schema_version") != SCHEMA_VERSION:
        raise ContentError("Unsupported content schema version")
    source_ids = set()
    numbers = set()
    for source in sources:
        identifier = source.get("id", "")
        if not re.fullmatch(r"src-[0-9a-f]{12}", identifier) or identifier in source_ids:
            raise ContentError(f"Invalid/duplicate source ID: {identifier}")
        source_ids.add(identifier)
        number = source.get("number")
        if type(number) is not int or number < 1 or number in numbers:
            raise ContentError(f"Invalid/duplicate source number: {number}")
        numbers.add(number)
        if not source.get("citation") or not source.get("url"):
            raise ContentError(f"Source lacks citation/URL: {identifier}")
        url_parts = urlsplit(source["url"])
        if url_parts.scheme not in {"http", "https"} or not url_parts.netloc or url_parts.username:
            raise ContentError(f"Non-HTTP source URL: {identifier}")
    if [chapter["id"] for chapter in chapters] != book["chapter_ids"]:
        raise ContentError("Chapter order does not match book.json")
    identifiers = set()
    registered_entry_ids = {item["id"] for item in registry["entries"].values()}
    text_values = [book["front_matter"], book["back_matter"]]
    for chapter in chapters:
        unit_ids = {unit["id"] for unit in chapter["units"]}
        if len(unit_ids) != len(chapter["units"]):
            raise ContentError(f"Duplicate units in {chapter['id']}")
        memberships = {}
        for unit in chapter["units"]:
            for identifier in unit["entry_ids"]:
                if identifier in memberships:
                    raise ContentError(f"Entry assigned to multiple units: {identifier}")
                memberships[identifier] = unit["id"]
            text_values.append(unit["intro"])
        text_values.append(chapter["intro"])
        for entry in chapter["entries"]:
            identifier = entry["id"]
            validate_audience(entry, required=bool(book.get("audience_schema_version")))
            # The prefix records the original allocation, not current placement.
            # Moving a registered entry must preserve its published share URL.
            if identifier in identifiers or not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*-\d{3}", identifier):
                raise ContentError(f"Invalid/duplicate entry ID: {identifier}")
            identifiers.add(identifier)
            if entry["chapter_id"] != chapter["id"] or entry["unit_id"] not in unit_ids or memberships.get(identifier) != entry["unit_id"]:
                raise ContentError(f"Inconsistent chapter/unit: {identifier}")
            if (list(entry["fields"]) != list(FIELD_NAMES.values())
                    or any(not isinstance(value, str) or (key not in {"cost", "notes"} and not value.strip())
                           for key, value in entry["fields"].items())):
                raise ContentError(f"Invalid six fields: {identifier}")
            if "summary" in entry:
                summary = entry["summary"]
                if (not isinstance(summary, str) or not summary.strip()
                        or re.search(r"[\r\n|`]|\*\*|\[[^\]]+\]|^\s*#{1,6}\s", summary)):
                    raise ContentError(f"Summary must be one paragraph of plain text: {identifier}")
            if entry["clinical_review_status"] != "not_clinically_reviewed":
                raise ContentError(f"Clinical sign-off is not established in this edition: {identifier}")
            date.fromisoformat(entry["content_checked_at"])
            if any(label not in {"A", "B", "C"} for label in entry["evidence_labels"]):
                raise ContentError(f"Invalid evidence labels: {identifier}")
            if any(tag not in TAGS for tag in entry["tags"]):
                raise ContentError(f"Invalid editorial tag: {identifier}")
            cited = list(dict.fromkeys(STABLE_REF.findall("\n".join(entry["fields"].values()))))
            if cited != entry["source_ids"]:
                raise ContentError(f"Citation/source_ids mismatch: {identifier}")
            if not cited:
                raise ContentError(f"Entry has no source: {identifier}")
            if identifier not in registered_entry_ids:
                raise ContentError(f"Entry absent from ID registry: {identifier}")
            text_values.extend(entry["fields"].values())
        if set(memberships) != {item["id"] for item in chapter["entries"]}:
            raise ContentError(f"Dangling unit membership in {chapter['id']}")
    for text in text_values:
        missing = set(STABLE_REF.findall(text)) - source_ids
        if missing:
            raise ContentError(f"Unknown stable source token(s): {sorted(missing)}")
        if NUMERIC_REF.search(text):
            raise ContentError("Unmigrated numeric citation in canonical narrative")
        if re.search(r"\[\[@|\[\[[A-Z_]+\d+\]\]", text):
            raise ContentError("Unresolved migration placeholder")
    registry_sources = {item["id"] for item in registry["sources"].values()}
    if registry_sources != source_ids:
        raise ContentError("Source ID registry does not match sources.json")
    if registered_entry_ids != identifiers:
        raise ContentError("Entry ID registry does not match canonical entries")
    aliases=book.get('entry_aliases',{})
    if not isinstance(aliases,dict):raise ContentError('Invalid entry aliases')
    for old,target in aliases.items():
        if (not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*-\d{3}',old)
                or old in identifiers or target not in identifiers or old==target):
            raise ContentError('Invalid merged entry alias: '+str(old))


def load_content(root: Path) -> tuple[dict, list[dict], list[dict], dict]:
    content = root / "content"
    book = read_json(content / "book.json")
    chapters = [read_json(content / "chapters" / f"{key}.json") for key in book["chapter_ids"]]
    sources = read_json(content / "sources.json")
    registry = read_json(content / "id-registry.json")
    validate_content(book, chapters, sources, registry)
    return book, chapters, sources, registry
