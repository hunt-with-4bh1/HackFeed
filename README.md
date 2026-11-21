# HackFeed

> Your automated feed for cybersecurity articles, bug bounty reports, and CTF writeups.

HackFeed discovers public security content from configured RSS/Atom feeds, normalizes links, removes duplicates, classifies entries, and updates this repository automatically.

[![Update HackFeed](https://github.com/hunt-with-4bh1/HackFeed/actions/workflows/update.yml/badge.svg)](https://github.com/hunt-with-4bh1/HackFeed/actions/workflows/update.yml)

## Latest discoveries

<!-- HACKFEED:START -->
The first collection will appear after the GitHub Actions workflow runs.
<!-- HACKFEED:END -->

## Browse by category

- [Bug Bounty](docs/BUG-BOUNTY.md)
- [CTF Writeups](docs/CTF-WRITEUPS.md)
- [Web Security](docs/WEB-SECURITY.md)
- [Reverse Engineering](docs/REVERSE-ENGINEERING.md)
- [Forensics](docs/FORENSICS.md)
- [Pwn & Binary Exploitation](docs/PWN.md)
- [Cryptography](docs/CRYPTO.md)
- [Other Security Research](docs/OTHER.md)

## How it works

1. Collectors fetch configured RSS/Atom feeds.
2. Entries are normalized and deduplicated by canonical URL.
3. A lightweight keyword classifier assigns categories.
4. The generator updates this README and category pages.
5. GitHub Actions runs the pipeline every hour and can also be started manually.

## Add a source

Edit [config/sources.json](config/sources.json). Add an object with a unique `id`, display `name`, feed `url`, and optional `type` / `tags`. Sources must expose a public RSS or Atom feed.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

## Data and attribution

HackFeed stores article metadata and links, not full article text. Content remains on the original publisher's website. Titles, authors, and publication dates are attributed where provided by the feed. Please open the original source for the complete article.

## Reliability notes

- A failed feed is logged and does not stop other feeds from being processed.
- Existing records are retained when a source is temporarily unavailable.
- Feed entries are metadata-checked, not independently verified or reproduced.
- The first run may show only feeds that respond successfully.

## License

MIT. See [LICENSE](LICENSE).
