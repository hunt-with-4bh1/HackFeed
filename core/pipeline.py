"""Feed collection, normalization, classification and persistence."""
from __future__ import annotations
import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import requests

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "config" / "sources.json"
DATABASE = ROOT / "database" / "writeups.json"
LOG = logging.getLogger("hackfeed")
TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}
CATEGORY_RULES = {
    "BUG-BOUNTY": ["bug bounty", "hackerone", "bugcrowd", "intigriti", "responsible disclosure", "bounty"],
    "CTF-WRITEUPS": ["ctf", "capture the flag", "picoctf", "hack the box", "hackthebox", "tryhackme", "htb"],
    "WEB-SECURITY": ["xss", "cross-site scripting", "ssrf", "sqli", "sql injection", "idor", "csrf", "ssti", "rce", "request smuggling", "web security", "api security"],
    "REVERSE-ENGINEERING": ["reverse engineering", "malware analysis", "disassembly", "ghidra", "ida pro", "decompiler"],
    "FORENSICS": ["forensics", "memory dump", "disk image", "volatility", "steganography", "pcap"],
    "PWN": ["pwn", "binary exploitation", "buffer overflow", "rop chain", "heap exploitation", "format string"],
    "CRYPTO": ["cryptography", "cryptanalysis", "rsa", "aes", "elliptic curve", "padding oracle"],
}

def canonical_url(value: str) -> str:
    try:
        parts = urlsplit(value.strip())
        if parts.scheme not in ("http", "https") or not parts.netloc:
            return value.strip()
        query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                 if not k.lower().startswith("utm_") and k.lower() not in TRACKING_KEYS]
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/") or "/", urlencode(query), ""))
    except Exception:
        return value.strip()

def classify(title: str, summary: str, source_tags: list[str]) -> str:
    text = (title + " " + summary + " " + " ".join(source_tags)).lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(word in text for word in keywords):
            return category
    return "OTHER"

def load_database() -> dict:
    if not DATABASE.exists():
        return {"version": 1, "items": []}
    try:
        data = json.loads(DATABASE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data
    except (OSError, json.JSONDecodeError):
        LOG.exception("Could not read database; starting a fresh in-memory collection")
    return {"version": 1, "items": []}

def collect() -> tuple[list[dict], list[dict]]:
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    collected, failures = [], []
    session = requests.Session()
    session.headers.update({"User-Agent": "HackFeed/1.0 (+https://github.com/hunt-with-4bh1/HackFeed)"})
    for source in sources:
        try:
            response = session.get(source["url"], timeout=(8, 20))
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
            if parsed.bozo and not parsed.entries:
                raise ValueError(str(parsed.bozo_exception))
            count = 0
            for entry in parsed.entries[:100]:
                link = canonical_url(entry.get("link") or entry.get("id") or "")
                title = re.sub(r"\s+", " ", entry.get("title", "Untitled")).strip()
                if not link.startswith(("http://", "https://")):
                    continue
                published = entry.get("published") or entry.get("updated") or ""
                author = entry.get("author", "")
                summary = re.sub(r"<[^>]+>", " ", entry.get("summary", ""))
                summary = re.sub(r"\s+", " ", summary).strip()[:500]
                tags = [tag.get("term", "") for tag in entry.get("tags", []) if tag.get("term")]
                tags.extend(source.get("tags", []))
                item_id = hashlib.sha256(link.encode("utf-8")).hexdigest()
                collected.append({
                    "id": item_id, "title": title[:300], "url": link,
                    "source": source["name"], "source_id": source["id"],
                    "type": source.get("type", "article"),
                    "category": classify(title, summary, tags),
                    "author": author[:120], "published_at": published,
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                    "tags": sorted(set(t.lower() for t in tags if t))[:15],
                    "summary": summary, "metadata_checked": True
                })
                count += 1
            LOG.info("%s: collected %d entries", source["name"], count)
        except Exception as exc:
            LOG.warning("%s failed: %s", source.get("name", "unknown source"), exc)
            failures.append({"source": source.get("name", "unknown"), "error": str(exc)[:240]})
    session.close()
    return collected, failures

def run_pipeline() -> dict:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    data = load_database()
    by_id = {item.get("id"): item for item in data["items"] if item.get("id")}
    incoming, failures = collect()
    added = 0
    for item in incoming:
        old = by_id.get(item["id"])
        if old:
            # Preserve first discovery timestamp; refresh feed metadata.
            item["discovered_at"] = old.get("discovered_at", item["discovered_at"])
        else:
            added += 1
        by_id[item["id"]] = item
    items = sorted(by_id.values(), key=lambda x: x.get("published_at") or x.get("discovered_at", ""), reverse=True)
    data = {"version": 1, "updated_at": datetime.now(timezone.utc).isoformat(),
            "total": len(items), "items": items[:5000],
            "last_run": {"feeds_ok": len(json.loads(SOURCES.read_text())) - len(failures),
                         "feeds_failed": failures, "entries_seen": len(incoming), "new_entries": added}}
    DATABASE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOG.info("Saved %d records (%d new); %d feed failures", len(data["items"]), added, len(failures))
    return data
