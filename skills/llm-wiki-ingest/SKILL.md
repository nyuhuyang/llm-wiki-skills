---
name: llm-wiki-ingest
description: Ingest new raw knowledge sources into the LLM Wiki. Use when the user says ingest, 摄入, 处理这个, provides a raw file (markdown, Word .docx, PDF, or any text source), or wants source material compiled into wiki pages with traceability, deduplication checks, and persisted updates. Also trigger when the user provides a .docx, Word, or PDF file they want added to the knowledge base. Supports --deep flag for exhaustive multi-pass extraction with claim-level sourcing, relationship triples, and mandatory cross-wiki contradiction scan.
---

# LLM Wiki Ingest

> **Skill activated: `llm-wiki-ingest`** — output this line at the top of every response that uses this skill.

Use this skill for converting new material into persistent wiki knowledge.

## Scope

- Read from `raw/` only; do not modify it except for the repo-level `["clippings"]` tag exception defined in `CLAUDE.md`
- Write or update `wiki/sources/`, `wiki/concepts/`, `wiki/entities/`, `wiki/syntheses/`, `wiki/index.md`, and `wiki/log.md`
- Word file pre-processing may write new files to `raw/assets/<slug>/` (image extraction) — this is the only write exception to `raw/` other than the clippings tag rule
- PDF pre-processing writes a converted `.md` alongside the original `.pdf` in the same directory — this is permitted
- If `wiki/QUESTIONS.md` is missing and the workflow needs it, create it first

## Word File Pre-Processing

If the input file is a `.docx` (Word) file, convert it before proceeding to Source Routing.

**Steps:**

1. Derive a slug from the filename: lowercase, spaces → hyphens, strip extension.
   ```
   slug = filename.lower().replace(' ', '-').removesuffix('.docx')
   ```

2. Compute SHA-256 of the original `.docx` file **before** conversion — this is the canonical hash for the source page:
   ```bash
   shasum -a 256 <path-to-file>.docx
   ```

3. Run pandoc to convert to markdown and extract embedded images:
   ```bash
   pandoc \
     -t markdown_strict \
     --extract-media='raw/assets/<slug>' \
     '<path-to-file>.docx' \
     -o '<same-dir-as-docx>/<slug>.md'
   ```
   - `markdown_strict` avoids pandoc-flavored markdown quirks in output
   - `--extract-media` writes all embedded images/figures to `raw/assets/<slug>/` (creates the directory if needed)
   - Output `.md` sits alongside the original `.docx` in the same directory

4. Read the converted `.md` file as the source content for the rest of this skill.

5. Set `raw_file:` in the wiki/sources/ page to the original `.docx` path (not the temp `.md`).

6. If pandoc is not installed, report the error and stop. Do not attempt a manual conversion.

7. **Language preservation:** Do not translate the converted `.md` file. If the source is in Chinese (or any other language), the converted file must retain the original language exactly — headings, body text, titles, all preserved as-is. Translation to English happens only when writing wiki pages.

After pre-processing, continue with Source Routing using the converted markdown content as if it were a native markdown raw file.

## PDF File Pre-Processing

If the input file is a `.pdf`, convert it to markdown before proceeding to Source Routing.

**Steps:**

1. Derive a slug from the filename: lowercase, spaces → hyphens, strip extension.
   ```
   slug = filename.lower().replace(' ', '-').removesuffix('.pdf')
   ```

2. Compute SHA-256 of the original `.pdf` file **before** conversion — this is the canonical hash for the source page:
   ```bash
   shasum -a 256 <path-to-file>.pdf
   ```

3. Convert PDF to markdown. Try tools in this order:

   **Option A — `marker` (best quality; preserves headings, tables, math):**
   ```bash
   marker_single '<path-to-file>.pdf' --output_dir '<same-dir-as-pdf>/'
   ```
   Output lands at `<same-dir-as-pdf>/<slug>/<slug>.md`. Copy or use that file.

   **Option B — `pymupdf4llm` (good quality, Python):**
   ```bash
   python3 -c "
   import pymupdf4llm, pathlib
   md = pymupdf4llm.to_markdown('<path-to-file>.pdf')
   pathlib.Path('<same-dir-as-pdf>/<slug>.md').write_text(md)
   "
   ```

   **Option C — `pdftotext` (fallback; plain text, layout preserved):**
   ```bash
   pdftotext -layout '<path-to-file>.pdf' '<same-dir-as-pdf>/<slug>.txt'
   ```
   Rename/treat `.txt` as the source content. Note: no heading structure; treat the entire text as one section during extraction.

   Try Option A first. If `marker_single` is not installed, try B. If neither is available, use C. If none are available, report and stop — do not attempt manual extraction.

4. Read the converted file as the source content for the rest of this skill.

5. Set `raw_file:` in the wiki/sources/ page to the original `.pdf` path (not the converted file).

6. If the PDF is image-only (scanned, no extractable text), report this and stop — OCR is out of scope.

7. **Language preservation:** Do not translate the converted file. If the PDF content is in Chinese (or any other language), the converted markdown must retain the original language exactly — headings, body text, titles, all preserved as-is. Translation to English happens only when writing wiki pages.

After pre-processing, continue with Source Routing using the converted content as if it were a native markdown raw file.

## Source Routing

Classify in this order:

1. Frontmatter `type: personal-writing` -> personal-writing flow
2. Path under `raw/personal/` -> personal-writing flow
3. Frontmatter `type: pdf-reference` -> pdf-reference flow
4. Otherwise -> standard external-source flow

If frontmatter is missing:

- derive `title` from the first `#` heading, else from filename
- leave source URL empty or mark it unknown
- use filesystem modified time as the fallback date
- continue ingest; record the warning in `wiki/log.md`

If raw frontmatter `tags` are exactly `["clippings"]` and only that single tag:

- the agent may replace that list with up to 3 more relevant tags
- do not make any other raw edits
- do not add more than 3 tags
- do not apply this rule when `tags` already contain anything other than the single value `clippings`

## Standard Flow

1. Read the target source fully.
2. Compute SHA-256 for the raw file and carry it into the source page metadata.
3. Confirm or infer the source title, date, author, and source URL.
4. For long or layered sources, split the source by its natural section structure (`#`, `##`, `###`) and perform extraction section by section before writing any pages.
5. **Create a section-by-section extraction table before writing any pages.** For every substantive section, list:
   - concepts/entities explicitly named
   - insights that are not standalone concepts but still deserve persistence
   - distinctions, caveats, assumptions, boundary conditions, and counterintuitive claims
   - candidate links to existing wiki pages
   - anything surprising or structurally important
   No section may be skipped silently.
6. Create or update one grounded page in `wiki/sources/`. Source pages MUST include `graph-excluded: true` in frontmatter — they are grounding documents, not graph nodes. Knowledge connections belong on concept/entity pages, not source pages.
7. **Enumerate ALL concepts and entities before creating any concept/entity pages.** Produce an explicit numbered list of every named and described concept or entity found in the source. Do not skip anything at this stage — over-enumerate rather than under-enumerate. This list must be written out before proceeding.
8. For each item in the list: check whether a page already exists by checking filename candidates and frontmatter `aliases`. Mark each as "exists" or "new".
9. Decide where each extracted item belongs:
   - reusable named node -> `wiki/concepts/` or `wiki/entities/`
   - source-specific but high-value insight bundle -> `wiki/syntheses/`
   - supporting nuance that does not deserve its own page -> preserve inside the source page and/or the affected concept page under a source-specific section
10. Create a page for every "new" node. Update every "exists" node by appending new evidence, source links, contradictions, evolution notes, and source-specific insights. Do not skip any item on the list.
11. If a source contains layered reasoning, explanatory lenses, or multiple levels of insight, preserve those layers explicitly. Do not collapse them into one umbrella summary.
12. If a source is older than two years, mark it as potentially outdated.
13. Check `wiki/QUESTIONS.md` for open questions this source may answer; surface that possibility to the user.
14. Run a coverage audit before finishing: confirm that each major source section contributed either pages, source-page notes, or a written reason why nothing was persisted.
15. Update `wiki/index.md` and append a timestamped line to `wiki/log.md`.

## Deep Mode (`--deep`)

Activate when the user passes `--deep`, says "deep ingest", "仔细", "非常仔细", "exhaustive", or "thorough ingest".

Deep mode replaces the standard single-pass extraction with a **4-pass protocol** that runs before writing any pages. Every pass must produce written output before the next begins.

### Pass 1 — Structure Map

Produce a structural inventory of the entire source:

```
| Section heading | Depth | Has tables | Has figures | Has code | Word count (approx) |
```

Every `#`, `##`, `###` heading gets a row. If no heading structure exists, divide by natural paragraph breaks. No section may be collapsed or skipped. This table is written out in full before Pass 2 begins.

### Pass 1.5 — Image Vision

Before claim extraction, scan the full source for every image reference:
- Markdown: `![alt](path)` or `![alt](url)`
- HTML img tags: `<img src="...">`

**Path resolution for `.docx`-derived sources:** images extracted by pandoc land in `raw/assets/<slug>/` (relative to KB root). If an image path in the converted markdown is relative (e.g., `raw/assets/<slug>/image1.png`), resolve it from KB root. Do not search elsewhere.

For each image found:

1. **Local path** — resolve relative paths from KB root; check `raw/assets/<slug>/` first for docx-derived sources. Read the file directly using the Read tool (supports PNG, JPG, etc.).
2. **URL** — fetch using WebFetch if publicly accessible.
3. **Describe** — produce a structured annotation:
   ```
   [IMAGE: <filename or url>]
   Alt text: <original alt text or "none">
   Visual description: <what the image shows — diagrams, charts, screenshots, text in image, arrows, labels, data>
   Key information: <any facts, numbers, relationships, or concepts readable from the image>
   Relevance: <how this image relates to surrounding text>
   ```
4. **Inject** — insert the annotation inline, immediately after the image reference in the working copy of the source text. The original source file is NOT modified.
5. **Skip** — if image is inaccessible (broken path, auth-gated URL, etc.), note `[IMAGE SKIPPED: <reason>]` and continue.

Produce an image inventory table before proceeding to Pass 2:

```
| # | Image ref | Type | Status | Key content summary |
```

If no images found: note "no images" and skip this pass entirely.

### Pass 2 — Claim-Level Extraction

For every section from Pass 1, extract **every factual claim** with its exact location anchor:

```
| Section | Claim | Claim type | Confidence signal in source |
```

Claim types: `definition`, `assertion`, `mechanism`, `causal`, `comparative`, `limitation`, `assumption`, `counterintuitive`. A long source will produce 50–200 rows; do not collapse. Write out the full table before Pass 3 begins.

### Pass 3 — Relationship Triples

From the claims in Pass 2, derive explicit entity-relationship triples:

```
| Subject | Relation | Object | Claim row ref |
```

Relation vocabulary (use exact terms): `implements`, `exemplifies`, `contradicts`, `enables`, `requires`, `is-a`, `part-of`, `causally-precedes`, `measures`, `replaces`, `extends`. Every triple must reference the claim row it was derived from. Write the full triple list before Pass 4 begins.

### Pass 4 — Cross-Wiki Contradiction Scan

For every concept or entity named in Pass 2:

1. Search `wiki/concepts/` and `wiki/entities/` for an existing page.
2. If found, read it and compare every claim in Pass 2 against what the wiki already asserts.
3. Flag contradictions, updates, and confirmations explicitly:

```
| Concept | Existing wiki claim | New source claim | Status (confirms | updates | contradicts) |
```

Write this table in full. Do not skip concepts just because no existing page was found — note "no existing page" in the Status column.

### After the 4 Passes

Proceed with the standard flow from step 6 (create/update source page), but with these additional requirements enforced in deep mode:

- **Claim-level sourcing**: every factual statement added to a concept/entity page gets an inline anchor: `> Source: <title>, § <section>`. Not just a wikilink — a paragraph-level reference.
- **Relationship section**: every concept/entity page updated in deep mode must have a `## Relationships` section listing all triples from Pass 3 involving that concept.
- **Exhaustive question generation**: after writing pages, scan for every gap, ambiguity, or incomplete explanation. Generate at least 1 open question per 5 concepts extracted. Append all to `wiki/QUESTIONS.md`.
- **Coverage matrix**: before finishing, produce a final coverage matrix:

```
| Section | Concepts extracted | Claims persisted | Relationships | Questions generated | Status |
```

Every row must reach "complete" status. Any "partial" row requires a written reason.

### Deep Mode Completion Summary

Extend the standard Ingest Complete block with:

```
**Mode:** deep
**Passes completed:** 4/4
**Claims extracted:** <N>
**Relationship triples:** <N>
**Contradictions found:** <N> (list if any)
**Questions generated:** <N> (appended to QUESTIONS.md)
**Coverage matrix:** all sections complete / <N> partial (with reasons)
```

---

## Extraction Granularity

**Source vs. concepts are strictly separate:**

- The source document itself → one `wiki/sources/` page, titled after the article. This is the only place the article title appears as a page name.
- Concepts and entities *inside* the source → extracted into `wiki/concepts/` and `wiki/entities/`. These are ideas, methods, theories, tools, and people discussed in the article — NOT the article itself.

Never create a concept page named after the article. Never treat the article title as a concept. A source about "quantitative investing advantages" should produce concept pages like [[mean-reversion]], [[variance-risk-premium]], [[kelly-criterion]] — not a concept page called [[quantitative-investing-advantages]].

Every named and described concept or entity in the source MUST get its own page. Do not summarize at the topic level only.

**The test**: if the source names something — a method, technique, model, tool, person, dataset, gene, company, theory, framework, or phenomenon — AND provides at least a definition or description of it, it gets a page. Even if it seems minor.

- A source that names 20 distinct concepts must produce ~20 concept/entity pages, not 3 umbrella summaries
- When in doubt, over-extract — a small redundant page costs nothing; a missing node is a broken link in the graph
- Do not skip extraction because the concept seems "obvious" or "well-known" — create or update the page anyway

Concept/entity extraction alone is not enough. Also preserve:

- source-specific insights that sharpen or reinterpret an existing concept
- explanatory lenses or interpretive frames used to make a concept legible
- mechanism descriptions
- non-obvious distinctions
- applicability limits, assumptions, and failure modes
- contradictions, caveats, and "this is deeper than it first looks" arguments

If an insight is valuable but not a durable standalone node, persist it in `wiki/syntheses/` or in a source-specific section on the affected source/concept page. Do not let it disappear just because it is not a clean page title.

For long conversational or pedagogical sources, do not reduce the ingest to canonical textbook concepts only. Extract the deeper structural insights too.

## Insight Persistence

Treat ingest as knowledge compilation, not top-level summarization.

- Named reusable concepts/entities -> pages
- Article- or source-specific insight bundles -> synthesis page when substantial
- Smaller but important nuance -> source page `Notable Insights`, `Section Map`, or source-specific subsection on concept page

When a source contains layered insights, preserve the layering explicitly, for example:

1. surface intuition
2. sharper formal statement
3. structural implication
4. downstream connection

Do not flatten these into one bullet unless the source itself is shallow.

**What counts as a concept**: reusable abstract ideas, methods, theories, phenomena, frameworks (e.g., attention mechanism, gradient descent, mean reversion)

**What counts as an entity**: specific named things — people, tools, models, papers, companies, datasets, genes (e.g., BERT, TP53, Renaissance Technologies)

**For Chinese sources specifically**: translate each concept/entity name to English for the page title and slug; store the original Chinese name in `aliases`.

## Personal-Writing Flow

- Do not treat the author's own writing as independent evidence that raises source-backed confidence
- Prefer writing the stance into `## My Position` or the equivalent section on affected concept pages
- Preserve any cited external sources as separate evidence when they exist
- Still record raw file path, hash, date, and log entry

## Merge-First Rule

**Never create a duplicate page. Never delete an existing page.**

Before writing any new concept or entity page:

1. Search for an existing page by slug, filename, and frontmatter `aliases`.
2. If a match exists → **update it**: append new evidence, refine the definition, add source links, note contradictions or evolution. Do not create a second page.
3. If no match exists → create a new page.
4. If unsure whether a match exists, err on the side of updating the closest match rather than creating a new one.

This rule applies even when the existing page is sparse or outdated. Refine in place; do not replace.

## Writing Rules

- Ground factual claims in source pages, not only in concept/entity pages
- Record disagreements explicitly in `Contradictions`
- Write all wiki page content in English; translate Chinese sources when creating pages
- Prefer English lowercase-hyphen slugs for new canonical targets, with Chinese or alternate names stored in `aliases`
- Do not mass-rename existing legacy pages opportunistically; leave structural cleanup to lint or merge work

## Minimum Persisted Changes

After a successful ingest, persist all of the following:

- source page created or updated
- relevant concept/entity pages created or updated
- `wiki/index.md` refreshed
- `wiki/log.md` appended

If any of these are skipped, state why.

## Completion Summary

**After every ingest, output a structured summary to the user.** Do not end silently.

Format:

```
## Ingest Complete

**Source:** <title> (`<path>`)
**Type:** <standard | personal-writing | pdf-reference>

**Pages created:** <N>
<bulleted list of new wiki/sources/, wiki/concepts/, wiki/entities/, wiki/syntheses/ pages>

**Pages updated:** <N>
<bulleted list of updated pages>

**Key concepts extracted:** <comma-separated list of top 5–10 concepts>

**Open questions answered:** <list matching questions from QUESTIONS.md, or "none">

**Skipped / incomplete:** <any sections or items not persisted, with reason — or "none">
```

Omit any section that has nothing to report (e.g., if no open questions were answered, drop that line). Keep it concise — one line per page is enough.

## Output Telemetry

At the very end of every response, emit these two lines (substitute real values):

```
OUTPUT_PATH: wiki/sources/YYYY-MM-DD-slug.md
QUALITY: 0.8
```

`OUTPUT_PATH` is the path (relative to `KB_ROOT`) of the primary file written. `QUALITY` is your self-assessed quality score for this run (0.0–1.0). Emit both lines even if no file was written (use `""` for path and `0.0` for quality). These lines are parsed by the runner for telemetry.
