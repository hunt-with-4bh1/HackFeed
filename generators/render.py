from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PLATFORM_DIR = DOCS / "platforms"
CATEGORY_FILES = {
    "WEB-EXPLOITATION": "WEB-EXPLOITATION.md",
    "CRYPTOGRAPHY": "CRYPTOGRAPHY.md",
    "DIGITAL-FORENSICS": "DIGITAL-FORENSICS.md",
    "BINARY-EXPLOITATION": "BINARY-EXPLOITATION.md",
    "AI-SECURITY": "AI-SECURITY.md",
    "REVERSE-ENGINEERING": "REVERSE-ENGINEERING.md",
    "OSINT": "OSINT.md", "NETWORK": "NETWORK.md", "CLOUD": "CLOUD.md",
    "MOBILE": "MOBILE.md", "HARDWARE-IOT": "HARDWARE-IOT.md",
    "MISC": "MISC.md", "UNCATEGORIZED": "UNCATEGORIZED.md",
}

def esc(value):
    return str(value or "").replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()

def table(items, limit=250):
    if not items:
        return "_No matching public writeups collected yet._\n"
    rows = [
        "| Date | CTF / Challenge / Repository | Platform | Category | Author / Team | Source |",
        "|---|---|---|---|---|---|",
    ]
    for item in items[:limit]:
        date = esc(item.get("published_at") or item.get("discovered_at", ""))[:16] or "Unknown"
        title = esc(item.get("title", "Untitled"))
        summary = esc(item.get("ai_summary") or item.get("summary", ""))
        if summary:
            title += "<br><sub>" + summary[:240] + "</sub>"
        rows.append(
            f"| {date} | [{title}]({item.get('url', '')}) | "
            f"{esc(item.get('platform'))} | {esc(item.get('category'))} | "
            f"{esc(item.get('author'))} | {esc(item.get('source'))} |"
        )
    return "\n".join(rows) + "\n"

def render(data):
    DOCS.mkdir(parents=True, exist_ok=True)
    PLATFORM_DIR.mkdir(parents=True, exist_ok=True)
    items = data.get("items", [])
    ctf_items = [x for x in items if x.get("type") == "ctf_writeup"]

    for category, filename in CATEGORY_FILES.items():
        selected = [x for x in ctf_items if x.get("category") == category]
        heading = category.replace("-", " ").title()
        (DOCS / filename).write_text(
            f"# {heading} CTF Writeups\n\n{table(selected)}", encoding="utf-8"
        )

    platforms = sorted({x.get("platform", "Other") for x in ctf_items})
    index = [
        "# CTF Writeups by Platform", "",
        "CTFtime is the primary source. Browse public writeup links by platform.", "",
    ]
    for platform in platforms:
        slug = platform.lower().replace(" ", "-").replace("/", "-").replace("·", "").strip("-")
        selected = [x for x in ctf_items if x.get("platform") == platform]
        index.append(f"- [{platform}](platforms/{slug}.md) — {len(selected)} entries")
        (PLATFORM_DIR / (slug + ".md")).write_text(
            f"# {platform} Writeups\n\n{table(selected, 500)}", encoding="utf-8"
        )

    (DOCS / "CTF-WRITEUPS.md").write_text(
        "\n".join(index) + "\n\n## Latest CTF writeups\n\n" + table(ctf_items, 300),
        encoding="utf-8",
    )

    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HACKFEED:START -->", "<!-- HACKFEED:END -->"
    if start in readme and end in readme:
        before, remainder = readme.split(start, 1)
        _, after = remainder.split(end, 1)
        other = [x for x in items if x.get("type") != "ctf_writeup"]
        latest = table(ctf_items, 60)
        if other:
            latest += "\n### Other security research\n\n" + table(other, 10)
        readme = before + start + "\n" + latest + end + after
    readme_path.write_text(readme, encoding="utf-8")
