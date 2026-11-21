# HackFeed Content Policy

HackFeed is a public index and learning library for cybersecurity and CTF writeups.

## Hybrid content model

Each record must use one of these content modes:

- `link_only`: Store title, author, source, URL, tags, dates, category and limited metadata. The reader follows the original publisher.
- `excerpt`: Store a short excerpt only when the source feed/API provides it and its terms permit this use. Preserve attribution and the canonical source URL.
- `full_text_authorized`: Store and display the full article only when the author has granted permission or the content license explicitly permits republication. Record the permission/license evidence and attribution requirements.

Do not infer permission from public accessibility, RSS availability, or search indexing. Do not bypass paywalls, login requirements, robots restrictions, or platform access controls.

## Required metadata for full-text content

A full-text record must include:
- `content_mode: full_text_authorized`
- `rights_basis`: author permission or exact license identifier
- `rights_evidence`: permission reference, source URL, or license URL
- `attribution`: author and original publisher
- `collected_at`: UTC timestamp

If rights are unclear, downgrade the record to `link_only`.

## Community sources

- Discord: collect only from servers/channels where the server owner/admin has authorized the bot and the bot has the required read permissions.
- X/Twitter and Reddit: use permitted public APIs/feeds and respect their terms and rate limits.
- GitHub: retain repository and author attribution; respect repository licenses.

## Corrections and takedowns

Provide a contact method in the future website before accepting broad community submissions. For the repository phase, issues can be used to report incorrect metadata, broken links, attribution problems, or removal requests.

## Principle

HackFeed centralizes discovery and permitted content. It does not claim ownership of third-party articles or replace their original publishers.
