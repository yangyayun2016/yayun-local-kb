---
type: note
title: 'Agent Rules for Gbrian Brain'
created: 2026-05-17
updated: 2026-05-17
confidence: medium
---

# Agent Rules for Gbrian Brain

This repository is a local GBrain-backed Markdown knowledge base.

## Required Read Order

1. `RESOLVER.md`
2. `schema.md`
3. `index.md`
4. The specific directory `README.md` for the page you are about to create or edit

## Operating Rules

- Search existing pages before creating a new page.
- Use one canonical page per entity.
- Put unsorted or uncertain material in `inbox/`.
- Use `sources/` for source summaries and raw-import notes.
- Use `log.md` for important maintenance and ingest events.
- Do not store secrets, credentials, private keys, session tokens, or payment data.
- Mark uncertain claims as `待确认`.
- Cite sources for important facts whenever possible.
- When a user correction conflicts with existing knowledge, update the page and record the correction in the timeline.

## GBrain Commands

Use these from this repo after setting the active GBrain home to `E:\gbrian-home`:

```powershell
gbrain import . --no-embed
gbrain sync --repo .
gbrain search "keyword"
gbrain query "question"
```

If no embedding API key is configured, keyword search works; semantic vector search can be enabled later.

