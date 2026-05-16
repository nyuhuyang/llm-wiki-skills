---
name: llm-wiki-save
description: Two modes — SAVE: after a multi-turn conversation, scan history for genuinely valuable content and selectively save to wiki (not a dump; applies judgment). QUERY: retrieve and answer questions from existing wiki content with grounded citations. Trigger SAVE with /llm-wiki-save or "save the good stuff". Trigger QUERY with "根据我的知识库", "what does the wiki say about", or "query the wiki".
---

# LLM Wiki Save

> **Skill activated: `llm-wiki-save`** — output this line at the top of every response that uses this skill.

Two modes. Claude detects which to use from the trigger phrase and context.

---

## Mode A — SAVE (trigger: `/llm-wiki-save`, "save the good stuff", "distill this conversation")

Distill a productive conversation into durable wiki artifacts. Applies value filter; not a transcript dump.

### Step 1 — Scan and Filter

Read through the conversation history. For each candidate:

| Question | Save if |
|---|---|
| Novel insight, not just a restatement? | Yes |
| Decision with reasoning? | Yes |
| Reusable pattern, concept, or synthesis? | Yes |
| Factual knowledge not already in the wiki? | Yes |
| Ephemeral chat, clarification, or back-and-forth? | **No** |
| Already captured in existing wiki pages? | **No** |

If nothing passes the filter, say so explicitly: "No content in this conversation worth preserving."

### Step 2 — Propose Before Writing

Show a short save plan before writing:

```
Proposed saves:
1. [Insight title] → wiki/syntheses/YYYY-MM-DD-<slug>.md
   "One sentence explaining why this is worth saving."
2. [Concept name] → wiki/concepts/<slug>.md
   "One sentence explaining why."

Saving now...
```

State the plan and proceed — do not ask for confirmation unless the write is ambiguous or risky.

### Step 3 — Route and Write

| Artifact type | Destination |
|---|---|
| Cross-source insight, derived knowledge | `wiki/syntheses/YYYY-MM-DD-<slug>.md` |
| Named concept (reusable abstraction) | `wiki/concepts/<slug>.md` (create or update) |
| Named entity (person, tool, model, paper) | `wiki/entities/<slug>.md` (create or update) |
| Operational output, decision log | `outputs/<slug>.md` |

Check for existing pages before creating — update in place if one already covers the concept.

### Minimum Frontmatter (syntheses)

```yaml
---
title: <Title>
type: synthesis
date: YYYY-MM-DD
sources: []
---
```

### Post-Save Steps

- Append `wiki/log.md` with a timestamped entry per saved file
- Refresh `wiki/index.md` if it tracks recent outputs
- Check `wiki/QUESTIONS.md` — if any open question is now answered, move it to resolved and note the output page

---

## Mode B — QUERY (trigger: "根据我的知识库", "what does the wiki say about", "query the wiki", "look up in wiki")

Retrieve and answer questions from existing wiki content with grounded citations.

### Retrieval Order

1. `wiki/index.md` for overview and recent entries
2. Targeted reads from `wiki/sources/`, `wiki/concepts/`, `wiki/entities/`, `wiki/syntheses/`
3. Read the most relevant pages fully before answering

### Answering Rules

- Ground conclusions in `wiki/sources/` citations
- Surface disagreements explicitly — do not blend them away
- Include confidence notes when evidence is thin, stale, or conflicting

### Output Shape

- Normal question → concise markdown answer
- Comparison → table when it improves clarity
- Trend or evidence summary → structured bullets or small report

### Persist If Valuable

If the answer is non-trivial and reusable, save it:
- `wiki/syntheses/DATE-topic.md` for multi-source analysis
- `outputs/DATE-topic.md` for reports or utility artifacts

Include: answer, supporting source pages, confidence notes, limitations.

If the answer is too weak to persist, answer in chat and explain the gap.

### Post-Query Steps

Check `wiki/QUESTIONS.md` for any open question this answer fully or partially addresses. If found, move it to the resolved section and note which output or synthesis page contains the answer.

---

## Writing Rules (both modes)

- Write in English
- Write distilled insight, not raw conversation text
- `type: synthesis` in frontmatter for synthesis pages
- `sources:` field: name any grounding `wiki/sources/` pages that exist

## What This Skill Does NOT Do

- Does not ingest raw source files → use `llm-wiki-ingest`
- Does not validate wiki integrity → use `llm-wiki-lint`
