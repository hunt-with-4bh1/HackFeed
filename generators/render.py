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


CATEGORY_LABELS = {
    "WEB-EXPLOITATION": ("🌐", "Web Exploitation"),
    "CRYPTOGRAPHY": ("🔐", "Cryptography"),
    "DIGITAL-FORENSICS": ("🧩", "Digital Forensics"),
    "BINARY-EXPLOITATION": ("💥", "Binary Exploitation / Pwn"),
    "AI-SECURITY": ("🤖", "AI Security"),
    "REVERSE-ENGINEERING": ("⚙️", "Reverse Engineering"),
    "OSINT": ("🕵️", "OSINT"),
    "NETWORK": ("🌍", "Network"),
    "CLOUD": ("☁️", "Cloud"),
    "MOBILE": ("📱", "Mobile"),
    "HARDWARE-IOT": ("🔌", "Hardware / IoT"),
    "MISC": ("🎯", "Miscellaneous"),
    "UNCATEGORIZED": ("📂", "Needs classification"),
}


def category_cards(items):
    counts = {category: sum(1 for item in items if item.get("category") == category)
              for category in CATEGORY_FILES}
    keys = list(CATEGORY_LABELS)
    cells = []
    for offset in range(0, len(keys), 3):
        row = []
        for category in keys[offset:offset + 3]:
            emoji, label = CATEGORY_LABELS[category]
            count = counts.get(category, 0)
            row.append(
                f'<td width="33%" align="center"><a href="docs/{CATEGORY_FILES[category]}">'
                f'<strong>{emoji} {label}</strong></a><br/><sub>{count:,} writeups · Browse</sub></td>'
            )
        while len(row) < 3:
            row.append("<td width=\"33%\"></td>")
        cells.append("<tr>" + "".join(row) + "</tr>")
    cells.append('<tr><td colspan="3" align="center"><a href="docs/CTF-WRITEUPS.md"><strong>📚 Browse all CTF writeups by platform →</strong></a></td></tr>')
    return '<table>\\n' + "\\n".join(cells) + '\\n</table>\\n'

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
    category_start, category_end = "<!-- HACKFEED:CATEGORIES:START -->", "<!-- HACKFEED:CATEGORIES:END -->"
    if category_start in readme and category_end in readme:
        before_categories, remainder = readme.split(category_start, 1)
        _, after_categories = remainder.split(category_end, 1)
        readme = before_categories + category_start + "\\n" + category_cards(ctf_items) + category_end + after_categories
    start, end = "<!-- HACKFEED:START -->", "<!-- HACKFEED:END -->"
    if start in readme and end in readme:
        before, remainder = readme.split(start, 1)
        _, after = remainder.split(end, 1)
        other = [x for x in items if x.get("type") != "ctf_writeup"]
        latest = table(ctf_items, 100)
        if other:
            latest += "\n### Other security research\n\n" + table(other, 10)
        readme = before + start + "\n" + latest + end + after
    readme_path.write_text(readme, encoding="utf-8")
