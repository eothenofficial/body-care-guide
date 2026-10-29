"""Report editorial review age separately from clinical sign-off, without edits."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
NOTICE = "到期仅是按案头核查日期生成的维护提醒，不表示医学结论已失效。未临床签审单独列示，不等于到期；脚本不改正文、证据等级或审阅状态。"


def summarize_reviews(book: dict, chapters: list[dict], sources: list[dict],
                      as_of: date, interval_days: int = 180) -> dict:
    if type(as_of) is not date or type(interval_days) is not int or interval_days < 1:
        raise ValueError("as_of must be a date and interval_days a positive integer")
    records = []

    def add(kind: str, item: dict):
        checked = item.get("content_checked_at")
        record = {"kind": kind, "id": item.get("id", "book" if kind == "book" else ""),
                  "title": item.get("title") or item.get("citation") or item.get("id", ""),
                  "content_checked_at": checked, "age_days": None, "status": "invalid_date",
                  "clinical_review_status": (item.get("clinical_review_status", "unknown")
                                             if kind != "source" else "not_applicable")}
        if isinstance(checked, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", checked):
            try:
                age = (as_of - date.fromisoformat(checked)).days
                record["age_days"] = age
                record["status"] = "future_date" if age < 0 else "due" if age >= interval_days else "current"
            except ValueError:
                pass
        records.append(record)

    add("book", book)
    for chapter in chapters:
        for entry in chapter["entries"]:
            add("entry", entry)
    for source in sources:
        add("source", source)
    pending = [row for row in records if row["kind"] != "source"
               and row["clinical_review_status"] != "clinically_reviewed"]
    return {"as_of": as_of.isoformat(), "interval_days": interval_days, "notice": NOTICE,
            "content_version": book.get("content_version"), "records": records,
            "counts": {**dict(Counter(row["status"] for row in records)),
                       "total": len(records), "clinical_review_pending": len(pending)},
            "due": [row for row in records if row["status"] == "due"],
            "invalid_dates": [row for row in records if row["status"] == "invalid_date"],
            "future_dates": [row for row in records if row["status"] == "future_date"],
            "clinical_review_pending": pending}


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_markdown(report: dict) -> str:
    lines = ["# 内容复核提醒", "", report["notice"], "",
             f"计算日：{report['as_of']}；提醒间隔：{report['interval_days']}天。", ""]
    sections = [("按日期到期", "due"), ("日期缺失或无效", "invalid_dates"),
                ("核查日期晚于计算日", "future_dates"), ("尚未完成临床签审（与到期分开）", "clinical_review_pending")]
    for title, key in sections:
        rows = report[key]
        lines.extend([f"## {title}：{len(rows)}项", ""])
        if not rows:
            lines.extend(["无。", ""])
            continue
        lines.extend(["| 类别 | ID | 标题 | 案头核查日 | 间隔天数 | 临床审阅状态 |",
                      "| --- | --- | --- | --- | --- | --- |"])
        for row in rows:
            values = [row["kind"], row["id"], row["title"], row["content_checked_at"] or "缺失",
                      row["age_days"] if row["age_days"] is not None else "—", row["clinical_review_status"]]
            lines.append("| " + " | ".join(_cell(value) for value in values) + " |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--as-of", type=date.fromisoformat, default=None)
    parser.add_argument("--interval-days", type=int, default=180)
    args = parser.parse_args(argv)
    if args.interval_days < 1:
        parser.error("--interval-days must be positive")
    try:
        content = args.root / "content"
        def read(path):
            return json.loads(path.read_text(encoding="utf-8-sig"))
        book = read(content / "book.json")
        chapters = []
        for key in book["chapter_ids"]:
            if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", key):
                raise ValueError("Invalid chapter ID in book.json")
            chapters.append(read(content / "chapters" / f"{key}.json"))
        sources = read(content / "sources.json")
        report = summarize_reviews(book, chapters, sources, args.as_of or date.today(), args.interval_days)
        output = args.output_dir or args.root / "reports"
        output.mkdir(parents=True, exist_ok=True)
        (output / "review-due.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (output / "review-due.md").write_text(render_markdown(report), encoding="utf-8")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Review report could not be generated: {exc}", file=sys.stderr)
        return 2
    print(f"Review dates: {report['counts']}. {NOTICE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
