"""CTF-first collectors, topic classification, deduplication and optional AI summaries."""
from __future__ import annotations
import hashlib, html, json, logging, os, re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import feedparser, requests

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "config" / "sources.json"
DATABASE = ROOT / "database" / "writeups.json"
LOG = logging.getLogger("hackfeed")
UA = "HackFeed/2.1 (+https://github.com/hunt-with-4bh1/HackFeed)"
TRACKING = {"fbclid", "gclid", "mc_cid", "mc_eid"}

# Ordered from specific CTF challenge families to broad topics.
CATEGORY_RULES = {
 "WEB-EXPLOITATION": ["web exploitation","web exploit","web challenge","web security","web","sql injection","sqli","cross-site scripting","xss","ssrf","idor","ssti","csrf","xxe","request smuggling","path traversal","file upload","command injection","lfi","rfi","deserialization","prototype pollution","jwt"],
 "CRYPTOGRAPHY": ["cryptography","cryptanalysis","crypto","rsa","aes","elliptic curve","ecc","lattice","padding oracle","xor","lcg","hash length extension"],
 "DIGITAL-FORENSICS": ["digital forensics","forensics","forensic","memory dump","memory forensics","disk image","pcap","wireshark","volatility","steganography","file carving","metadata","evtx","registry hive"],
 "BINARY-EXPLOITATION": ["binary exploitation","binary exploit","pwn","pwning","buffer overflow","rop chain","ret2libc","heap exploitation","format string","stack canary","shellcode","use after free","uaf"],
 "AI-SECURITY": ["ai security","artificial intelligence","machine learning","llm","large language model","prompt injection","jailbreak","model extraction","adversarial","poisoning","rag","agentic","ai ctf"],
 "REVERSE-ENGINEERING": ["reverse engineering","reverse-engineering","reverse","reversing","ghidra","ida pro","radare2","angr","decompilation","disassembly","malware analysis"],
 "OSINT": ["osint","open source intelligence","geolocation","geoint","reconnaissance"],
 "NETWORK": ["network forensics","network exploitation","packet analysis","dns","protocol","snmp","network","rf","radio frequency"],
 "CLOUD": ["cloud security","aws","azure","gcp","iam","kubernetes","docker","container escape"],
 "MOBILE": ["android","ios","mobile app","apk","ipa"],
 "HARDWARE-IOT": ["hardware","iot","firmware","embedded","uart","jtag","rfid"],
 "MISC": ["miscellaneous","misc","programming","warmup","general skills","esoteric"],
}
CATEGORY_FILES = {k:k+".md" for k in CATEGORY_RULES}
CATEGORY_FILES["UNCATEGORIZED"] = "UNCATEGORIZED.md"

def canonical_url(value):
    try:
        p=urlsplit(value.strip())
        if p.scheme not in ("http","https") or not p.netloc: return value.strip()
        q=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if not k.lower().startswith("utm_") and k.lower() not in TRACKING]
        return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path.rstrip("/") or "/",urlencode(q),""))
    except Exception: return value.strip()

def classify(title, summary="", tags=None):
    text=(title+" "+summary+" "+" ".join(tags or [])).lower()
    for category, words in CATEGORY_RULES.items():
        for word in words:
            if re.search(r"(?<![a-z0-9])"+re.escape(word)+r"(?![a-z0-9])",text):
                return category
    return "UNCATEGORIZED"

def make_item(url,title,source,source_id,platform,summary="",tags=None,published="",author="",priority=50,item_type="ctf_writeup"):
    url=canonical_url(url)
    if not url.startswith(("http://","https://")): return None
    tags=tags or []
    category=classify(title,summary,tags)
    return {"id":hashlib.sha256(url.encode()).hexdigest(),"title":html.unescape(re.sub(r"\s+"," ",title or "Untitled")).strip()[:300],
      "url":url,"source":source,"source_id":source_id,"platform":platform,"type":item_type,
      "category":category,"author":author[:120],"published_at":published,"discovered_at":datetime.now(timezone.utc).isoformat(),
      "tags":sorted(set(str(x).lower() for x in tags if x))[:30],"summary":re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",summary or "")).strip()[:800],
      "priority":priority,"metadata_checked":True}

class CTFtimeParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows=[]; self.row=None; self.cell=None; self.anchor=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="tr": self.row=[]
        elif tag=="td" and self.row is not None: self.cell={"text":"","links":[]}
        elif tag=="a" and self.cell is not None: self.anchor={"href":attrs.get("href",""),"text":""}
    def handle_data(self,data):
        if self.cell is not None: self.cell["text"]+=data
        if self.anchor is not None: self.anchor["text"]+=data
    def handle_endtag(self,tag):
        if tag=="a" and self.anchor is not None:
            self.cell["links"].append(self.anchor); self.anchor=None
        elif tag=="td" and self.cell is not None:
            self.row.append(self.cell); self.cell=None
        elif tag=="tr" and self.row is not None:
            if self.row: self.rows.append(self.row)
            self.row=None

def collect_ctftime(session):
    items=[]; failures=[]
    # CTFtime's dedicated public RSS feed for newly published task writeups.
    try:
        r=session.get("https://ctftime.org/writeups/rss/",timeout=(8,25)); r.raise_for_status()
        feed=feedparser.parse(r.content)
        if feed.bozo and not feed.entries: raise ValueError(str(feed.bozo_exception))
        for entry in feed.entries[:250]:
            tags=[t.get("term","") for t in entry.get("tags",[]) if t.get("term")]
            summary=entry.get("summary","")
            item=make_item(entry.get("link") or entry.get("id",""),entry.get("title","CTFtime writeup"),
                "CTFtime","ctftime-writeups","CTFtime",summary,tags,
                entry.get("published") or entry.get("updated",""),entry.get("author",""),100,"ctf_writeup")
            if item: items.append(item)
    except Exception as e:
        failures.append({"source":"CTFtime public writeups RSS","error":str(e)[:240]})
        LOG.warning("CTFtime RSS failed: %s",e)
    LOG.info("CTFtime: collected %d public writeup links",len(items))
    return items,failures

def collect_rss(session,sources):
    items=[]; failures=[]
    for src in sorted(sources,key=lambda x:x.get("priority",50),reverse=True):
        try:
            r=session.get(src["url"],timeout=(8,20)); r.raise_for_status()
            feed=feedparser.parse(r.content)
            if feed.bozo and not feed.entries: raise ValueError(str(feed.bozo_exception))
            count=0
            for entry in feed.entries[:100]:
                tags=[t.get("term","") for t in entry.get("tags",[]) if t.get("term")]+src.get("tags",[])
                item=make_item(entry.get("link") or entry.get("id",""),entry.get("title","Untitled"),
                    src["name"],src["id"],src.get("platform",src["name"]),entry.get("summary",""),tags,
                    entry.get("published") or entry.get("updated",""),entry.get("author",""),src.get("priority",50),src.get("type","research"))
                if item: items.append(item); count+=1
            LOG.info("%s: %d entries",src["name"],count)
        except Exception as e:
            failures.append({"source":src.get("name","unknown"),"error":str(e)[:240]})
            LOG.warning("%s failed: %s",src.get("name","unknown"),e)
    return items,failures

GITHUB_QUERIES=[
 ("ctf-writeups in:name,description","GitHub · CTF writeups"),
 ("ctf-writeup in:name,description","GitHub · CTF writeup"),
 ("picoCTF writeups in:name,description","GitHub · picoCTF"),
 ("HackTheBox writeups in:name,description","GitHub · Hack The Box"),
 ("TryHackMe writeups in:name,description","GitHub · TryHackMe"),
 ("Root-Me writeups in:name,description","GitHub · Root-Me"),
 ("CTFLearn writeups in:name,description","GitHub · CTF Learn"),
]
def collect_github(session):
    items=[]; failures=[]
    headers={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}
    token=os.getenv("GITHUB_TOKEN")
    if token: headers["Authorization"]="Bearer "+token
    for query,label in GITHUB_QUERIES:
        try:
            r=session.get("https://api.github.com/search/repositories",params={"q":query,"sort":"updated","order":"desc","per_page":20},headers=headers,timeout=(8,20)); r.raise_for_status()
            for repo in r.json().get("items",[]):
                item=make_item(repo.get("html_url",""),repo.get("full_name",""),label,"github-search",label.replace("GitHub · ",""),
                    repo.get("description") or "Public CTF writeup repository",repo.get("topics",[])+["ctf","github"],repo.get("updated_at",""),
                    repo.get("owner",{}).get("login",""),70,"ctf_writeup")
                if item: items.append(item)
        except Exception as e: failures.append({"source":label,"error":str(e)[:240]})
    return items,failures

def optional_social(session):
    items=[]; failures=[]
    token=os.getenv("X_BEARER_TOKEN")
    if token:
        try:
            r=session.get("https://api.x.com/2/tweets/search/recent",params={"query":'(CTF OR picoCTF OR HackTheBox OR TryHackMe) (writeup OR walkthrough) -is:retweet',"max_results":100,"tweet.fields":"created_at,author_id"},headers={"Authorization":"Bearer "+token},timeout=(8,20)); r.raise_for_status()
            for p in r.json().get("data",[]):
                item=make_item("https://x.com/i/web/status/"+p["id"],p.get("text","")[:240],"X/Twitter","x-search","X/Twitter",p.get("text",""),["ctf","social"],p.get("created_at",""),p.get("author_id",""),55,"ctf_writeup")
                if item: items.append(item)
        except Exception as e: failures.append({"source":"X/Twitter","error":str(e)[:240]})
    else: failures.append({"source":"X/Twitter","error":"Optional: configure X_BEARER_TOKEN Actions secret"})
    token=os.getenv("DISCORD_BOT_TOKEN"); channels=[x.strip() for x in os.getenv("DISCORD_CHANNEL_IDS","").split(",") if x.strip()]
    if token and channels:
        for channel in channels[:20]:
            try:
                r=session.get(f"https://discord.com/api/v10/channels/{channel}/messages",params={"limit":100},headers={"Authorization":"Bot "+token},timeout=(8,20)); r.raise_for_status()
                for msg in r.json():
                    body=msg.get("content","")
                    if not re.search(r"ctf|write.?up|picoctf|hackthebox|tryhackme|root.?me",body,re.I): continue
                    for link in re.findall(r"https?://[^\s<>]+",body):
                        item=make_item(link,body[:220],"Discord","discord-"+channel,"Discord",body,["ctf","discord"],msg.get("timestamp",""),msg.get("author",{}).get("username",""),50,"ctf_writeup")
                        if item: items.append(item)
            except Exception as e: failures.append({"source":"Discord "+channel,"error":str(e)[:240]})
    else: failures.append({"source":"Discord","error":"Optional: configure DISCORD_BOT_TOKEN and DISCORD_CHANNEL_IDS; bot needs channel read permissions"})
    return items,failures

def ai_summarize(items):
    """Generate concise summaries with Gemini; the API key is read only from Actions secrets."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        LOG.info("Gemini summaries disabled: GEMINI_API_KEY Actions secret is not set")
        return
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    pending = [x for x in items if x.get("type") == "ctf_writeup" and not x.get("ai_summary") and x.get("summary")][:8]
    generated = 0
    for item in pending:
        prompt = (
            "Write a factual 1-2 sentence summary of this CTF writeup listing. "
            "Use only the title and supplied feed excerpt. Do not invent technical details "
            "or imply you read the full article. If information is limited, say so.\n\n"
            f"Title: {item['title']}\nPlatform: {item['platform']}\n"
            f"Category: {item['category']}\nExcerpt: {item['summary'][:700]}"
        )
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                json={"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                      "generationConfig": {"temperature": 0.2, "maxOutputTokens": 180}},
                timeout=(8, 30),
            )
            response.raise_for_status()
            payload = response.json()
            parts = payload.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            summary = " ".join(part.get("text", "") for part in parts).strip()
            if summary:
                item["ai_summary"] = summary[:600]
                item["ai_summary_model"] = model
                item["ai_provider"] = "Google Gemini"
                generated += 1
        except Exception as exc:
            LOG.warning("Gemini summary failed for %s: %s", item.get("url", ""), str(exc)[:200])
    LOG.info("Gemini summaries generated this run: %d; API key configured: yes", generated)

def run_pipeline():
    DATABASE.parent.mkdir(parents=True,exist_ok=True)
    old={}
    if DATABASE.exists():
        try:
            old={x["id"]:x for x in json.loads(DATABASE.read_text(encoding="utf-8")).get("items",[]) if x.get("id")}
        except Exception: LOG.exception("Could not read previous database")
    session=requests.Session(); session.headers.update({"User-Agent":UA})
    ctf,cf=collect_ctftime(session)
    sources=json.loads(SOURCES.read_text(encoding="utf-8"))
    rss,rf=collect_rss(session,sources)
    gh,gf=collect_github(session)
    social,sf=optional_social(session)
    session.close()
    incoming=ctf+rss+gh+social
    added=0; by_id=dict(old)
    for item in incoming:
        previous=old.get(item["id"])
        if previous:
            item["discovered_at"]=previous.get("discovered_at",item["discovered_at"])
            if previous.get("ai_summary"): item["ai_summary"]=previous["ai_summary"]; item["ai_summary_model"]=previous.get("ai_summary_model","")
        else: added+=1
        by_id[item["id"]]=item
    items=list(by_id.values())
    ai_summarize(items)
    items.sort(key=lambda x:(x.get("type")=="ctf_writeup",x.get("priority",0),x.get("published_at") or x.get("discovered_at","")),reverse=True)
    failures=cf+rf+gf+sf
    data={"version":3,"updated_at":datetime.now(timezone.utc).isoformat(),"total":len(items),"items":items[:10000],
      "last_run":{"ctftime_entries":len(ctf),"rss_entries":len(rss),"github_repositories":len(gh),"social_links":len(social),
      "new_entries":added,"failures":failures}}
    DATABASE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    LOG.info("HackFeed: %d records (%d new), CTFtime=%d, RSS=%d, GitHub=%d",len(data["items"]),added,len(ctf),len(rss),len(gh))
    return data
