# HackFeed AI Knowledge Base

## Goal

Build a source-grounded knowledge base so an AI assistant can search, read, explain, compare, and cite CTF writeups while helping solve future challenges.

## Retrieval is not model training

A public GitHub repository URL does not automatically train Gemini or another model. The recommended first implementation is Retrieval-Augmented Generation (RAG):

1. Discover writeup metadata and original URLs.
2. Fetch full text only when the source licence/terms or explicit author permission allows it.
3. Extract readable text while preserving headings and code blocks. Record author, canonical URL, publication date, licence/permission evidence, and fetch timestamp.
4. Split long articles into overlapping chunks, retaining section heading, category, difficulty, and source URL.
5. Generate embeddings and store chunks in a searchable vector index.
6. At question time, retrieve relevant chunks and pass them to Gemini with citations to the original articles.
7. Make the assistant explain concepts, compare approaches, and suggest next steps without inventing details not present in retrieved sources.

RAG keeps the corpus updateable. Fine-tuning is a separate later option for response style or structured output; it is not a substitute for retrieving current writeups.

## Content rights

- Public visibility is not permission to republish full article text.
- Default to link-only metadata and permitted feed excerpts.
- Full-text ingestion requires explicit permission or a compatible licence recorded per document.
- Do not bypass logins, paywalls, robots restrictions, rate limits, or private Discord access.
- Store attribution and source URLs with every chunk.
- If rights are unclear, index metadata and link to the original only.

See [Content Policy](CONTENT-POLICY.md).

## Difficulty and quality labels

Use Easy/Beginner, Medium/Intermediate, or Hard/Advanced only when the source explicitly states the level or a reviewer verifies it. Otherwise label it UNRATED. An AI estimate must be visibly marked as estimated and include confidence and its evidence. Never duplicate or fabricate entries to reach a target.

The target of 30 Easy + 30 Medium + 30 Hard entries per category is a collection goal, not a claim about current coverage. Each category should show the real available count at each level.

## Current implementation status

- Metadata, public feed excerpts, category/platform indexes, and Gemini summaries from feed excerpts: implemented in part.
- Full article text extraction, rights-aware document store, chunking, embeddings, vector search, and grounded Q&A: not implemented yet.
- Current Gemini summaries are based on feed metadata/excerpts, not complete article contents.

## Planned document fields

`document_id`, `title`, `canonical_url`, `author`, `published_at`, `category`, `difficulty`, `difficulty_basis`, `platform`, `challenge_name`, `content_mode`, `rights_basis`, `rights_evidence`, `attribution`, `text_hash`, `chunks`, `embedding_model`, `indexed_at`.

Each chunk should retain `chunk_id`, `section_heading`, `text`, `source_url`, `start_offset`, and `end_offset`.

## Evaluation

Test retrieval using real CTF questions. Check that retrieved chunks contain the answer, every answer links to a source, no unsupported commands or exploit steps are invented, labels match the source, duplicate mirrors are detected, and new articles become searchable after updates.
