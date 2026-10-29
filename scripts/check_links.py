"""Report source URL accessibility; HTTP success is not medical validation.

No content is rewritten. --strict fails only for definite HTTP 404/410 results;
blocked requests, throttling and connection failures remain inconclusive.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.client import HTTPException
import json
from pathlib import Path
import socket
import ssl
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NOTICE = "仅检测链接可访问性。HTTP 200不代表医学结论正确、内容未变或来源已获临床审阅。403、429和超时不能直接判为失效。"


def _request_url(url: str) -> str:
    if not isinstance(url, str):
        raise ValueError("URL must be text")
    parts = urlsplit(url.strip())
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError("Only absolute HTTP(S) source URLs are supported")
    if parts.username or parts.password:
        raise ValueError("Source URLs must not contain credentials")
    if any(character.isspace() for character in parts.netloc):
        raise ValueError("Source URL host must not contain whitespace")
    host = parts.hostname.encode("idna").decode("ascii")
    if ":" in host:
        host = f"[{host}]"
    if parts.port is not None:
        host += f":{parts.port}"
    return urlunsplit((parts.scheme, host, quote(parts.path, safe="/%:@!$&'()*+,;=-._~"),
                       quote(parts.query, safe="%=&?/:@!$'()*+,;~-._"), ""))


def _http_category(code: int) -> str:
    if 200 <= code < 300:
        return "reachable"
    if code in {404, 410}:
        return "missing"
    if code in {401, 403}:
        return "blocked"
    if code == 429:
        return "rate_limited"
    if 500 <= code < 600:
        return "server_error"
    if 300 <= code < 400:
        return "redirect_unresolved"
    return "http_error"


def check_url(url: str, timeout: float = 10.0, opener=None) -> dict:
    """HEAD first, then GET only when the server explicitly returns 405."""
    result = {"url": url, "status": "invalid_url", "http_status": None,
              "method": "HEAD", "detail": "", "final_url": None}
    try:
        target = _request_url(url)
    except (ValueError, UnicodeError) as exc:
        result["detail"] = str(exc)
        return result
    open_url = opener if opener is not None else urlopen
    for method in ("HEAD", "GET"):
        result.update(method=method, http_status=None, final_url=None)
        request = Request(target, method=method, headers={
            "User-Agent": "BodyCareGuide-LinkCheck/1.0 (source accessibility only)",
            "Accept": "text/html,application/pdf,*/*;q=0.5",
        })
        try:
            with open_url(request, timeout=timeout) as response:
                code = response.getcode()
                result.update(http_status=code, final_url=response.geturl())
                if code == 405 and method == "HEAD":
                    continue
                result.update(status=_http_category(code), detail=f"HTTP {code}")
                return result
        except HTTPError as exc:
            code = exc.code
            result.update(http_status=code, final_url=exc.geturl())
            exc.close()
            if code == 405 and method == "HEAD":
                continue
            result.update(status=_http_category(code), detail=f"HTTP {code}")
            return result
        except (TimeoutError, socket.timeout) as exc:
            result.update(status="timeout", detail=str(exc) or "Request timed out")
            return result
        except ssl.SSLError as exc:
            result.update(status="tls_error", detail=str(exc))
            return result
        except URLError as exc:
            reason = exc.reason
            status = ("timeout" if isinstance(reason, (TimeoutError, socket.timeout))
                      else "tls_error" if isinstance(reason, ssl.SSLError)
                      else "network_error")
            result.update(status=status, detail=str(reason))
            return result
        except (OSError, ValueError, HTTPException) as exc:
            result.update(status="network_error", detail=str(exc))
            return result
    return result


def collect_links(root: Path) -> list[dict]:
    """Deduplicate the canonical source ledger, retaining every source ID."""
    sources = json.loads((Path(root) / "content" / "sources.json").read_text(encoding="utf-8-sig"))
    if not isinstance(sources, list):
        raise ValueError("content/sources.json must contain an array")
    links = {}
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("url"), str):
            raise ValueError("Every source needs a URL string")
        url = source["url"].strip()
        item = links.setdefault(url, {"url": url, "source_ids": []})
        identifier = source.get("id", "")
        if identifier not in item["source_ids"]:
            item["source_ids"].append(identifier)
    return list(links.values())


def build_report(links: list[dict], timeout: float = 10.0, opener=None, workers: int = 8) -> dict:
    def check(item):
        return {**check_url(item["url"], timeout=timeout, opener=opener),
                "source_ids": item["source_ids"]}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(check, links))
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "notice": NOTICE,
            "checked_urls": len(results), "counts": dict(Counter(row["status"] for row in results)),
            "results": results}


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_markdown(report: dict) -> str:
    lines = ["# 来源链接健康报告", "", report["notice"], "",
             f"生成时间：{report['generated_at']}；共检查{report['checked_urls']}个去重URL。", "",
             "分类计数：" + ", ".join(f"{key}={value}" for key, value in sorted(report["counts"].items())), "",
             "所有结果均保留在 JSON；以下列出需要人工查看的请求。", "",
             "| 分类 | HTTP | 方法 | 来源ID | URL | 说明 |", "| --- | --- | --- | --- | --- | --- |"]
    problems = [row for row in report["results"] if row["status"] != "reachable"]
    for row in problems:
        values = [row["status"], row["http_status"] or "—", row["method"],
                  ", ".join(row["source_ids"]), row["url"], row["detail"]]
        lines.append("| " + " | ".join(_cell(value) for value in values) + " |")
    if not problems:
        lines.append("| 无待查看请求 | — | — | — | — | 仅说明本次请求可达 |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--strict", action="store_true", help="Fail only for HTTP 404/410, not blocked/timeout results")
    args = parser.parse_args(argv)
    if args.timeout <= 0 or args.workers < 1:
        parser.error("--timeout and --workers must be positive")
    try:
        report = build_report(collect_links(args.root), timeout=args.timeout, workers=args.workers)
        output = args.output_dir or args.root / "reports"
        output.mkdir(parents=True, exist_ok=True)
        (output / "link-health.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (output / "link-health.md").write_text(render_markdown(report), encoding="utf-8")
    except (OSError, ValueError, TypeError) as exc:
        print(f"Link report could not be generated: {exc}", file=sys.stderr)
        return 2
    print(f"Checked {report['checked_urls']} URLs; results: {report['counts']}. {NOTICE}")
    return 1 if args.strict and report["counts"].get("missing", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
