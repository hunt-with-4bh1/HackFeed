from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CATEGORY_FILES = {
    "BUG-BOUNTY": "BUG-BOUNTY.md", "CTF-WRITEUPS": "CTF-WRITEUPS.md",
    "WEB-SECURITY": "WEB-SECURITY.md", "REVERSE-ENGINEERING": "REVERSE-ENGINEERING.md",
    "FORENSICS": "FORENSICS.md", "PWN": "PWN.md", "CRYPTO": "CRYPTO.md", "OTHER": "OTHER.md"
}

def esc(value: str) -> str:
    return (value or "").replace("|", "\\|").replace("\n", " ").strip()

def table(items: list[dict], limit: int = 100) -> str:
    if not items:
        return "_No entries collected yet. The page will populate after a successful feed run._\n"
    rows = ["| Published | Article / writeup | Category | Source |", "|---|---|---|---|"]
    for item in items[:limit]:
        date = esc(item.get("published_at", ""))[:16] or "Unknown"
        title = esc(item.get("title", "Untitled"))
        url = item.get("url", "")
        source = esc(item.get("source", ""))
        category = esc(item.get("category", "OTHER"))
        rows.append(f"| {date} | [{title}]({url}) | {category} | {source} |")
    return "\n".join(rows) + "\n"

def render(data: dict) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    items = data.get("items", [])
    for category, filename in CATEGORY_FILES.items():
        selected = [x for x in items if x.get("category") == category]
        heading = filename.replace(".md", "").replace("-", " ").title()
        content = f"# {heading}\n\nAutomatically collected public links. Always read the original publisher's page.\n\n{table(selected)}"
        (DOCS / filename).write_text(content, encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    start, end = "<!-- HACKFEED:START -->", "<!-- HACKFEED:END -->"
    latest = table(items, 50)
    if start in readme and end in readme:
        before, remainder = readme.split(start, 1)
        _, after = remainder.split(end, 1)
        readme = before + start + "\n" + latest + end + after
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
