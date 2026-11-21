# HackFeed 🚩

> A CTF-first index of public Capture The Flag writeups, walkthroughs, and security research.

**CTFtime is the primary source.** HackFeed also discovers public CTF writeups from GitHub, 0xdf, Hack The Box, TryHackMe, picoCTF, Root-Me, CTF Learn, Medium, DEV.to, and Reddit.

[![Update HackFeed](https://github.com/hunt-with-4bh1/HackFeed/actions/workflows/update.yml/badge.svg)](https://github.com/hunt-with-4bh1/HackFeed/actions/workflows/update.yml)

## Latest CTF writeups

<!-- HACKFEED:START -->
The CTF-focused index will populate after the workflow runs.
<!-- HACKFEED:END -->

## Filter by CTF category

- [Web Exploitation](docs/WEB-EXPLOITATION.md)
- [Cryptography](docs/CRYPTOGRAPHY.md)
- [Digital Forensics](docs/DIGITAL-FORENSICS.md)
- [Binary Exploitation / Pwn](docs/BINARY-EXPLOITATION.md)
- [AI Security](docs/AI-SECURITY.md)
- [Reverse Engineering](docs/REVERSE-ENGINEERING.md)
- [OSINT](docs/OSINT.md)
- [Network](docs/NETWORK.md)
- [Cloud](docs/CLOUD.md)
- [Mobile](docs/MOBILE.md)
- [Hardware / IoT](docs/HARDWARE-IOT.md)
- [Miscellaneous](docs/MISC.md)
- [CTF Writeups by Platform](docs/CTF-WRITEUPS.md)

## Sources

| Source | Method |
|---|---|
| CTFtime | Public writeups listing (highest priority) |
| GitHub | Repository search: ctf-writeups, ctf-writeup, picoCTF, HTB, TryHackMe, Root-Me, CTF Learn |
| 0xdf | Public RSS feed |
| Hack The Box | Official Write-Ups RSS |
| TryHackMe / picoCTF / Root-Me / CTF Learn | Public community RSS and GitHub discovery |
| Medium / DEV.to | Public CTF and platform-tag feeds |
| Reddit | Public subreddit RSS |
| X / Twitter | Optional API integration |
| Discord | Optional bot integration for explicitly authorized channels |

## AI summaries and classification

HackFeed classifies CTF entries into challenge categories using title, feed excerpt, and tags. If \`OPENAI_API_KEY\` is configured, it generates short AI summaries for up to 8 unsummarized CTF entries per run. Without that secret, the original feed excerpt is shown instead.

## Optional integrations

Add secrets in **Settings → Secrets and variables → Actions**:
- \`OPENAI_API_KEY\` — enables AI summaries.
- \`OPENAI_MODEL\` — optional model override (default: \`gpt-4o-mini\`).
- \`X_BEARER_TOKEN\` — optional X recent-search access.
- \`DISCORD_BOT_TOKEN\` and \`DISCORD_CHANNEL_IDS\` — optional; bot must be invited to each server and granted View Channel and Read Message History.
- \`GITHUB_TOKEN\` is supplied automatically by GitHub Actions for repository discovery.

## How it works

1. Collect CTFtime public writeup listings first.
2. Collect public RSS/Atom feeds.
3. Search GitHub for CTF writeup repositories.
4. Optionally collect X posts and messages from authorized Discord channels.
5. Normalize URLs, deduplicate, classify, and generate platform/category indexes.
6. GitHub Actions updates the repository hourly and supports manual runs.

## Important notes

- HackFeed stores links and metadata, not full copyrighted writeups.
- CTFtime's documented API is not used to clone its events service; this project indexes links from the public writeups listing.
- RSS/community results can include discussions or announcements; open the original source to verify relevance.
- Category labels are automated hints, not human verification.
- AI summaries are based only on available feed excerpts and must not be treated as a substitute for the original writeup.

## Run locally

\`\`\`bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
\`\`\`

## License

MIT. See [LICENSE](LICENSE).
