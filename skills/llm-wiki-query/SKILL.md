---
name: llm-wiki-query
description: Answer questions from the existing LLM Wiki with grounded citations and targeted retrieval. Use when the user asks what the wiki says about a topic, asks for a point lookup from the knowledge base, wants evidence from existing wiki pages, or needs a concise answer grounded in wiki sources rather than a new ingest or cross-source research pass.
---

# LLM Wiki Query

> **Skill activated: `llm-wiki-query`** — output this line at the top of every response that uses this skill.

Use this skill for point retrieval from the wiki corpus.

## Scope

- Read existing wiki content only: `wiki/index.md`, `wiki/sources/`, `wiki/concepts/`, `wiki/entities/`, `wiki/syntheses/`, and `wiki/QUESTIONS.md`
- Do not ingest new raw sources
- Do not perform broad cross-source synthesis unless the user explicitly asks for research or comparison
- Persist a reusable answer only when it is substantial enough to be worth saving

## Retrieval Order

1. Check `wiki/index.md` for the most likely entry points.
2. Read the most relevant `wiki/sources/` pages first.
3. Use concept and entity pages for definitions, aliases, and linked context.
4. Use `wiki/syntheses/` when the answer is already summarized there.
5. Check `wiki/QUESTIONS.md` if the user’s question may already be tracked or answered.

## Answering Procedure

1. Restate the query narrowly enough to retrieve the right pages.
2. Pull the smallest set of pages that can support a defensible answer.
3. Prefer source pages for factual grounding and concept/entity pages for terminology.
4. Surface disagreements, caveats, and source freshness explicitly.
5. Keep the answer concise unless the user asks for comparison or a deeper breakdown.

## Output Rules

- Cite the relevant wiki pages with markdown links
- Distinguish supported claims from inference
- Say when the corpus is thin, stale, or conflicting
- If the answer is reusable as a higher-level note, persist it to `wiki/syntheses/`
- If the answer is mostly a utility note or short operational summary, persist it to `outputs/`

## Persistence

Persist only when the answer is non-trivial and likely reusable.

- Use `wiki/syntheses/YYYY-MM-DD-<slug>.md` for grounded multi-page answers
- Use `outputs/YYYY-MM-DD-<slug>.md` for short reports or utility outputs
- Append `wiki/log.md` when a file is written
- Update `wiki/QUESTIONS.md` if the answer resolves a tracked question

## What This Skill Does Not Do

- Does not process raw sources into wiki pages; use `llm-wiki-ingest`
- Does not perform deep pattern discovery or gap analysis; use `llm-wiki-research`
- Does not validate wiki structure; use `llm-wiki-lint`
