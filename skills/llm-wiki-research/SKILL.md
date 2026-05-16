---
name: llm-wiki-research
description: Deep synthesis, pattern discovery, and gap analysis across the LLM Wiki. Use when the user says research, reflect, 综合分析, discover patterns, identify gaps, wants cross-source insights, or needs higher-order reasoning over existing wiki knowledge rather than a point-lookup or new ingest.
---

# LLM Wiki Research

> **Skill activated: `llm-wiki-research`** — output this line at the top of every response that uses this skill.

Use this skill for deep analysis over existing wiki knowledge. It is the synthesis and discovery counterpart to `llm-wiki-query` (point retrieval) and `llm-wiki-ingest` (new sources).

## When to Use

- Cross-source synthesis: "What does my wiki say about X across multiple sources?"
- Pattern discovery: "What recurring themes or contradictions appear?"
- Gap analysis: "What is missing or underexplored?"
- Hypothesis testing: "Does my wiki support or refute the claim that…?"
- Question tracking: "Add this open question to the wiki."
- Merge duplicates: "These two pages should be one."
- Periodic review: scheduled gap audits after bulk ingest

## Research Stages

1. **Check for counter-evidence first** — never generate a thesis before looking for disconfirming pages.
2. **Scan the corpus** — `wiki/index.md`, then targeted reads of `wiki/concepts/`, `wiki/entities/`, `wiki/sources/`, `wiki/syntheses/`.
3. **Map patterns and contradictions** — identify recurring ideas, conflicting claims, and sparse areas.
4. **Read deeply** — pull the most relevant pages in full before drawing conclusions.
5. **Synthesize** — produce a defensible thesis with evidence, counter-evidence, and confidence notes.
6. **Run gap analysis** — always append gap findings after any synthesis (see below).
7. **Persist** — write output to `wiki/syntheses/` or `outputs/` and update `wiki/log.md`.

## Required Discipline

- Do not generate a thesis before checking for disconfirming evidence
- Distinguish supported patterns from speculation
- Call out echo-chamber risk when no opposing evidence is found
- Prefer a small number of defensible insights over a long list of weak ones
- Confidence must be calibrated: high / medium / low with reasons

## Gap Analysis (always run after synthesis)

After synthesis, produce a gap report at `outputs/gap-report-YYYY-MM-DD.md`.

Three gap types to scan:

1. **Isolated concepts** — pages with only one source and created more than 30 days ago; flag for follow-up ingest
2. **Hidden blind spots** — things mentioned across multiple sources with no dedicated wiki page yet
3. **Sparse areas** — topic clusters with few pages or weak cross-linking relative to apparent importance

For each gap: state what is missing, which pages reference it, and a concrete next action (ingest a source, create a concept page, merge duplicates).

Open questions from gaps: append to `wiki/QUESTIONS.md` (create if missing):
```
- [ ] <question> — source: <page>, noted: YYYY-MM-DD
```

## Question Tracking

When user says "add question", "track this", "记录一个问题", or "我想搞清楚":

1. Normalize the question to a clear, answerable form.
2. Append to `wiki/QUESTIONS.md` under `## Open Questions`.
3. Link to relevant existing wiki pages if any.
4. After ingest or synthesis that answers an open question, move it to `## Resolved` with a link to the answering output.

## Merge Mode

When user says "merge", "duplicate pages", "consolidate", or two page paths are too similar:

1. Find candidate duplicates via slug similarity, frontmatter `aliases`, and content overlap.
2. Present candidates to user before merging — **never delete without confirmation**.
3. For each confirmed merge:
   - Pick canonical page (better slug, richer content, more inbound links).
   - Merge non-overlapping content into it; preserve contradictions and source links.
   - Add aliases from removed page to canonical frontmatter.
   - Update all wikilinks pointing to the removed page.
   - Delete the removed page.

## Persistence

Required outputs after a research run:

- `wiki/syntheses/YYYY-MM-DD-<topic>.md` — synthesis with thesis, evidence, counter-evidence, confidence, limitations
- `outputs/gap-report-YYYY-MM-DD.md` — gap findings

Always persist:
- thesis or key patterns found
- evidence and counter-evidence with page links
- confidence rating and reasons
- limitations of the current corpus
- next ingest targets or open questions

After persisting: append `wiki/log.md`. Refresh `wiki/index.md` and `wiki/overview.md` (Health Dashboard section if present).

## Synthesis Frontmatter

```yaml
---
title: <Title>
type: synthesis
date: YYYY-MM-DD
sources: [wiki/sources/page1.md, wiki/sources/page2.md]
confidence: medium
---
```
