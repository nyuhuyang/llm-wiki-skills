---
name: llm-wiki-lint
description: Validate structural integrity and consistency of the LLM Wiki. Use when the user says lint, 检查, validate, health check, wants a wiki audit, or asks for broken links, stale pages, duplicate concepts, or source-integrity issues to be found and optionally fixed.
---

# LLM Wiki Lint

> **Skill activated: `llm-wiki-lint`** — output this line at the top of every response that uses this skill.

Use this skill for integrity checks and health reports.

## Primary Source Of Truth

- Run `.codex/skills/llm-wiki-lint/lint.py` and treat its output as the baseline report.
- Then add targeted manual checks if the script does not cover the user's concern.

## Expected Checks

Focus on the highest-signal issues:

- invalid or missing frontmatter
- broken wikilinks
- missing index entries or stale index entries
- stub pages
- duplicate or near-duplicate concepts/entities
- source hash drift if hashes are tracked
- stale pages based on volatility or age
- legacy naming drift such as non-canonical wikilink targets
- wiki pages written in non-English (all wiki content must be in English per system contract)
- concept/entity pages whose titles closely match a source page title — this indicates the article was incorrectly turned into a concept instead of concepts being extracted from it

## Reporting

Persist the lint result to `outputs/lint-YYYY-MM-DD.md` when possible.

Include:

- findings ordered by severity
- affected files
- whether the issue is safe to auto-fix
- any gaps in automation or script coverage

Also append `wiki/log.md`.

## Fix Policy

- Review-only by default unless the user asked for fixes
- Never modify `raw/`
- Prefer minimal, mechanical fixes first
- Rerun lint after any fixes that change wiki structure
