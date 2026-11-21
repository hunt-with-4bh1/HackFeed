from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/"docs"
PLATFORM_DIR=DOCS/"platforms"
CATEGORY_FILES={
 "WEB-EXPLOITATION":"WEB-EXPLOITATION.md","CRYPTOGRAPHY":"CRYPTOGRAPHY.md",
 "DIGITAL-FORENSICS":"DIGITAL-FORENSICS.md","BINARY-EXPLOITATION":"BINARY-EXPLOITATION.md",
 "AI-SECURITY":"AI-SECURITY.md","REVERSE-ENGINEERING":"REVERSE-ENGINEERING.md",
 "OSINT":"OSINT.md","NETWORK":"NETWORK.md","CLOUD":"CLOUD.md","MOBILE":"MOBILE.md",
 "HARDWARE-IOT":"HARDWARE-IOT.md","MISC":"MISC.md","UNCATEGORIZED":"UNCATEGORIZED.md"
}
def esc(s): return (str(s or "").replace("|","\\\\|").replace("\\n"," ").strip())
def table(items,limit=250):
 if not items: return "_No matching public writeups collected yet._\\n"
 rows=["| Date | CTF / Challenge / Repository | Platform | Category | Author / Team | Link source |","|---|---|---|---|---|---|"]
 for x in items[:limit]:
  date=esc(x.get("published_at") or x.get("discovered_at",""))[:16] or "Unknown"
  title=esc(x.get("title","Untitled")); url=x.get("url","")
  summary=esc(x.get("ai_summary") or x.get("summary",""))
  if summary: title += "<br><sub>"+summary[:260]+"</sub>"
  rows.append(f"| {date} | [{title}]({url}) | {esc(x.get('platform'))} | {esc(x.get('category'))} | {esc(x.get('author'))} | {esc(x.get('source'))} |")
 return "\\n".join(rows)+"\\n"
def render(data):
 DOCS.mkdir(parents=True,exist_ok=True); PLATFORM_DIR.mkdir(parents=True,exist_ok=True)
 items=data.get("items",[]); ctf=[x for x in items if x.get("type")=="ctf_writeup"]
 for cat,file in CATEGORY_FILES.items():
  selected=[x for x in ctf if x.get("category")==cat]
  (DOCS/file).write_text(f"# {cat.replace('-', ' ').title()} CTF Writeups\\n\\n{table(selected)}",encoding="utf-8")
 platforms=sorted({x.get("platform","Other") for x in ctf})
 index=["# CTF Writeups by Platform","","CTFtime is the primary source. Browse links by platform.",""]
 for platform in platforms:
  slug=platform.lower().replace(" ","-").replace("/","-").replace("·","").strip("-")
  selected=[x for x in ctf if x.get("platform")==platform]
  index.append(f"- [{platform}](platforms/{slug}.md) — {len(selected)} entries")
  (PLATFORM_DIR/(slug+".md")).write_text(f"# {platform} Writeups\\n\\n{table(selected,500)}",encoding="utf-8")
 (DOCS/"CTF-WRITEUPS.md").write_text("\\n".join(index)+"\\n\\n## Latest CTF writeups\\n\\n"+table(ctf,300),encoding="utf-8")
 readme=(ROOT/"README.md").read_text(encoding="utf-8")
 start,end="<!-- HACKFEED:START -->","<!-- HACKFEED:END -->"
 if start in readme and end in readme:
  before,rest=readme.split(start,1); _,after=rest.split(end,1)
  latest=table(ctf,60)+"\\n### Other security research\\n\\n"+table([x for x in items if x.get("type")!="ctf_writeup"],10)
  readme=before+start+"\\n"+latest+end+after
 (ROOT/"README.md").write_text(readme,encoding="utf-8")
