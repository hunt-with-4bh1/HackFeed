# <img src="https://raw.githubusercontent.com/hunt-with-4bh1/HackFeed/main/assets/hackfeed-mark.svg" width="34" alt="HackFeed mark" /> HackFeed

<p align="center">
  <strong>One feed. The CTF writeups worth learning from.</strong><br/>
  A community-driven index of public CTF writeups and practical security research.
</p>

<p align="center">
  <a href="https://github.com/hunt-with-4bh1/HackFeed/actions/workflows/update.yml"><img src="https://github.com/hunt-with-4bh1/HackFeed/actions/workflows/update.yml/badge.svg" alt="Automated updates"/></a>
  <a href="https://github.com/hunt-with-4bh1/HackFeed/blob/main/LICENSE"><img src="https://img.shields.io/github/license/hunt-with-4bh1/HackFeed?style=flat-square" alt="License"/></a>
  <a href="https://github.com/hunt-with-4bh1/HackFeed/commits/main"><img src="https://img.shields.io/github/last-commit/hunt-with-4bh1/HackFeed?style=flat-square" alt="Last commit"/></a>
</p>

<p align="center">
  <a href="#latest-ctf-writeups">Explore writeups</a> ·
  <a href="#categories">Categories</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#contributing">Contribute</a>
</p>

---

## What is HackFeed?

HackFeed brings public CTF writeups together in one searchable, organized GitHub repository. It puts **CTFtime first**, then supplements it with public feeds and GitHub discovery from the wider security community.

No account. No paywall here. Just useful links, clear attribution, and a growing knowledge index.

## Latest CTF writeups

New public writeup links are collected automatically. Open the original source for the complete article.

<!-- HACKFEED:START -->
| Date | CTF / Challenge / Repository | Platform | Category | Author / Team | Source |
|---|---|---|---|---|---|
<!-- HACKFEED:END -->

## Categories

| Category | Browse |
|---|---|
| 🌐 Web Exploitation | [Open index](docs/WEB-EXPLOITATION.md) |
| 🔐 Cryptography | [Open index](docs/CRYPTOGRAPHY.md) |
| 🧩 Digital Forensics | [Open index](docs/DIGITAL-FORENSICS.md) |
| 💥 Binary Exploitation / Pwn | [Open index](docs/BINARY-EXPLOITATION.md) |
| 🤖 AI Security | [Open index](docs/AI-SECURITY.md) |
| ⚙️ Reverse Engineering | [Open index](docs/REVERSE-ENGINEERING.md) |
| 🕵️ OSINT | [Open index](docs/OSINT.md) |
| 🌍 Network | [Open index](docs/NETWORK.md) |
| ☁️ Cloud | [Open index](docs/CLOUD.md) |
| 📱 Mobile | [Open index](docs/MOBILE.md) |
| 🔌 Hardware / IoT | [Open index](docs/HARDWARE-IOT.md) |
| 🎯 Miscellaneous | [Open index](docs/MISC.md) |
| 📚 All CTF writeups by platform | [Open index](docs/CTF-WRITEUPS.md) |

## Sources

HackFeed currently gathers from public sources, including:

- **CTFtime** — primary source for public CTF writeup listings
- **GitHub** — public repositories tagged or described as CTF writeups
- **Security blogs and feeds** — including 0xdf, PortSwigger Research, and community blogs
- **Learning platforms and communities** — HTB, TryHackMe, picoCTF, Root-Me, CTF Learn, Medium, DEV.to and Reddit feeds

Source availability can change. A listing is a discovery pointer, so always verify details on the original page.

## AI summaries with Google Gemini

HackFeed uses **Google Gemini** to create short summaries from available titles and feed excerpts. It does not claim to read the full linked article. Summaries are limited to a small batch per update and are retained in the index.

### Enable Gemini (one-time setup)

1. Open your repository's **Settings → Secrets and variables → Actions**.
2. Select **New repository secret**.
3. Set the name to `GEMINI_API_KEY`.
4. Paste your newly generated Google AI Studio API key as the secret value.
5. Save it, then open [Actions](https://github.com/hunt-with-4bh1/HackFeed/actions) and run **Update HackFeed** once.

The default model is `gemini-2.5-flash`. You can optionally override it with a repository Actions variable named `GEMINI_MODEL`. The API key is read from the secret at runtime; it is never written into tracked files.

> **Never commit API keys.** If a key is accidentally shared, revoke it and create a replacement immediately.

## How it works

1. Fetch the latest public writeup listings from CTFtime.
2. Collect configured public RSS/Atom feeds.
3. Discover public CTF repositories on GitHub.
4. Normalize links and remove duplicates.
5. Classify entries by challenge category.
6. Ask Gemini for concise summaries when `GEMINI_API_KEY` is configured.
7. Refresh the README and category/platform indexes through GitHub Actions.

The workflow runs hourly and can also be started manually.

## Content and attribution

HackFeed is an **index, not a mirror**. By default it stores metadata, source links, and permitted feed excerpts. Full article text is only appropriate when the author has granted permission or the content has a compatible license. See [Content Policy](docs/CONTENT-POLICY.md).

- Publicly accessible does not automatically mean free to republish.
- Original authors and sources remain credited.
- AI summaries are based only on available feed excerpts.
- Automated categories are suggestions; check the original writeup.

## Contributing

Found a useful public CTF writeup source or spotted a broken link?

1. Open an issue with the source URL and a short explanation, or
2. Submit a pull request with the source details and evidence that the feed is public and suitable for indexing.

Please do not submit private, leaked, or access-controlled content.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

## License

MIT — see [LICENSE](LICENSE).
