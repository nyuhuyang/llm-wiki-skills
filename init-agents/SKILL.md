---
name: init-agents
description: "Initialize or synchronize a Harness Engineering-style agent context system for a repository: short AGENTS.md plus supporting docs/ files. Use when user says \"init-agents\", \"generate AGENTS.md\", \"sync AGENTS.md\", \"harness-style AGENTS.md\", \"create agent docs\", or wants a structured agent context system."
---

# Init Agents

Initializes and maintains a Harness Engineering-style agent context system: a short `AGENTS.md` navigation map backed by structured docs.

> Give agents a map, not a 1,000-page instruction manual. — Harness Engineering

Core rule: `AGENTS.md` is an index, not the source of truth. Long-lived knowledge belongs in dedicated docs, and `AGENTS.md` must stay synchronized with them.

## Workflow

### 1. Choose mode

- **Init mode**: no `AGENTS.md`, missing `docs/`, or user asks to initialize.
- **Sync mode**: `AGENTS.md` or docs already exist, or user asks to update/sync.
- Never delete docs or overwrite important existing content without confirmation.

### 2. Discover repo

Run in parallel:
```bash
find . -maxdepth 1 -name "*.md" -o -name "Makefile" -o -name "package.json" -o -name "pyproject.toml" | sort
find docs -maxdepth 3 -type f 2>/dev/null | sort || echo NO_DOCS_DIR
head -40 README.md 2>/dev/null
head -30 ARCHITECTURE.md 2>/dev/null
cat AGENTS.md 2>/dev/null
```

After reading the existing `AGENTS.md` repo map, do a second pass: for each source directory it mentions (e.g. `runner/`, `src/`, `lib/`), list its actual contents at depth 1:
```bash
find <src_dir> -maxdepth 1 | sort
```
This catches subdirectory and file drift that root-level discovery misses.

Extract:
- Project name and one-line purpose (from README h1 + first paragraph)
- Primary run/test/build command (from Makefile, package.json scripts, pyproject.toml)
- Existing conventions and escalation rules (from old AGENTS.md, README, CONTRIBUTING)
- Existing docs that should be referenced rather than duplicated

**Bootstrap contract check** — a repo is agent-operable only if a fresh session can answer all four of these from repo contents alone:
1. How do I start / run this? (run command discoverable)
2. How do I validate my work? (test or lint command discoverable)
3. What is the current progress / what's next? (exec-plans, PLANS.md, or context-maintenance.md present)
4. What are the hard constraints? (escalation rules in AGENTS.md)

Record which of the four are missing — report them as bootstrap contract gaps in Step 9, not as blockers. You can still generate AGENTS.md; just flag what's absent.

### 3. Ensure agent docs structure

If missing, create short placeholder docs. If present, preserve content and only add missing index files.

```
docs/
├── design-docs/
│   └── index.md          # Design decisions and core beliefs
├── exec-plans/
│   ├── active/           # Work-in-progress plans
│   └── completed/        # Archived completed plans
├── references/
│   └── index.md          # LLM-readable reference materials
├── adr/
│   └── index.md          # Architecture decision records
├── context-maintenance.md # Cross-session continuity artifact (default)
├── generated/            # Auto-generated — do not edit manually
└── PLANS.md              # Roadmap and prioritized backlog
```

`docs/generated/` is optional. Use it when scripts produce docs from structured state. Files here are **never** listed in the Docs Index and the tree entry must say "do not edit manually."

**`docs/context-maintenance.md`** — create this by default (not optional). It is the continuity artifact that lets a new agent session recover prior work without relying on chat history. Use this template if creating from scratch:

```markdown
# Context Maintenance

## Current WIP (WIP = 1)
<!-- One active task at a time. What is it? -->
-

## Last Validated State
<!-- What passed most recently? test suite / lint / manual check + date -->
-

## Open Decisions
<!-- Decisions made and their rationale — so a new session knows the "why" -->
-

## Next Action
<!-- Concrete first step for the next session -->
-
```

**`docs/PLANS.md`** — create with a feature-list table, not just prose bullets. Feature items are harness primitives: the state column enables automated progress tracking and prevents agents from marking tasks done without evidence.

```markdown
# Plans

## Backlog

| Feature | Behavior | Verification | State |
|---------|----------|--------------|-------|
| Example | What it does when working | `npm test -- feature.spec` | todo |

<!-- State values: todo | in-progress | done | blocked -->
<!-- Only move to "done" after Verification command passes -->
```

Optional, when appropriate for the repo:
- `ARCHITECTURE.md` — domain map and package layering
- `CONTRIBUTING.md` — human workflow
- `TESTING.md` — test strategy and commands
- `docs/agent-context.md` — repo-specific agent operating notes

Placeholder files must be brief: title plus 1-3 lines explaining ownership and intended content.

### 4. Generate or update AGENTS.md

Target: ~100 lines. Hard limit: 120 lines. Routing files in the 50–200 line range work best — below 50 is too thin to orient a fresh session; above 200, important rules get buried mid-file and lose effectiveness ("lost in the middle" effect). Cut prose, keep structure.

Structure:

````markdown
# <Project Name>

> <one-line purpose>

## Quick Start

```bash
<primary build/run/test command>
```

## Repository Map

```
<repo root listing of key files>
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── ...
├── adr/
│   ├── index.md
│   └── ...
├── exec-plans/
│   ├── active/
│   └── completed/
├── references/
│   └── ...
├── context-maintenance.md
└── PLANS.md
```

## Architecture

→ [`ARCHITECTURE.md`](ARCHITECTURE.md) — domain map and package layering

<2–3 bullets if ARCHITECTURE.md exists, else note it is missing>

## Docs Index

| Path | Purpose |
|------|---------|
| `docs/design-docs/` | Design decisions and core beliefs |
| `docs/adr/` | Architecture decision records |
| `docs/exec-plans/active/` | Current work in progress |
| `docs/exec-plans/completed/` | Archived plans |
| `docs/references/` | LLM-readable reference files |
| `docs/PLANS.md` | Roadmap and prioritized backlog |
| `docs/context-maintenance.md` | Cross-session continuity — WIP, decisions, next action |

## Conventions

- <convention 1 — from README/existing AGENTS.md or sensible repo default>
- <convention 2>
- <convention 3>
- <convention 4>
- <convention 5>

## Definition of Done

Before marking any task complete:
- [ ] `<test command>` passes
- [ ] No regressions in affected areas
- [ ] `docs/context-maintenance.md` updated (current WIP cleared, next action set)
- [ ] No unresolved TODOs left in changed files

## Agent Workflow

1. Read this file first.
2. Check `docs/exec-plans/active/` and `docs/context-maintenance.md` for current task context.
3. Read relevant docs before changing architecture or workflows.
4. Update supporting docs when behavior, architecture, commands, or conventions change.
5. Run tests before opening a PR: `<test command>`.
6. Escalate to human for anything in the Escalation section below.

## Escalation — Do Not Proceed Without Human Confirmation

- Schema or API contract changes
- Dependency major-version upgrades
- Deleting files, branches, or database tables
- Pushing to main/master directly
- <any repo-specific escalation points from context>
````

### Optional custom sections (add when present in existing AGENTS.md or clearly useful)

These are valid AGENTS.md sections beyond the standard template. Preserve them if found; add them when the repo warrants it:

- **`## Narrow Reading Scope`** (or `## Critical Token Budget Rule`) — explicit file-reading constraints for large-surface repos where agents tend to over-read. List the minimal file set for common task types (e.g. "bug fix scope: these 3 files only").
- **`## Tool Context`** (or a named tool section like `## Graphify Usage`) — operating notes for a repo-specific tool integrated into the workflow (graph query tools, custom CLI, MCP servers). Belongs in AGENTS.md only if agents need it every session; otherwise move to `docs/references/`.

Keep custom sections short (≤8 lines each). Count toward the 120-line limit.

### 5. Sync checks

Before writing, compare `AGENTS.md` and docs against the filesystem and source-of-truth docs:

- Repository tree in `AGENTS.md` matches actual key files and docs.
- **Source dir depth**: each source directory in the tree matches actual files and subdirs at depth 1. Root-level discovery misses new modules added inside an existing dir (e.g. `runner/core/`, `runner/modules/`). Fix any drift.
- Docs Index includes existing core docs and does not point to missing files unless clearly marked missing.
- Auto-generated dirs (e.g. `docs/generated/`) are in the tree but **not** in the Docs Index. If an auto-generated dir appears in the Docs Index, remove it.
- `docs/PLANS.md` does not contradict active exec plans.
- `docs/exec-plans/active/` stale plans are reported. A plan is stale if its body contains `Status: Deferred`, `Status: Blocked`, or equivalent — flag it and suggest moving to `completed/`.
- Architecture, testing, and contribution commands are referenced from the right source file.
- Important old `AGENTS.md` content is preserved or moved to a better supporting doc.
- Long explanations are moved out of `AGENTS.md` into docs, with links back.

**Prose-density check** (sync mode) — scan each section of `AGENTS.md` for inline prose blocks. Any section with more than 8 consecutive lines of prose (not a table, not a code block, not a bullet list) risks burying important rules mid-file where agents may miss them. Flag these sections in the report and suggest moving the prose to a `docs/` file with a one-line pointer in `AGENTS.md`.

Also flag if `AGENTS.md` is fewer than 50 lines — a file that short usually lacks enough orientation to be useful.

### 6. Source-of-truth rules

Use these authorities when summaries conflict:

- Project purpose: `README.md`; `AGENTS.md` only summarizes.
- Architecture: `ARCHITECTURE.md` and `docs/adr/`.
- Current work state: `docs/exec-plans/active/` and `docs/context-maintenance.md`.
- Roadmap and backlog: `docs/PLANS.md`.
- Commands: `Makefile`, `package.json`, `pyproject.toml`; `TESTING.md` explains test strategy.
- Human workflow: `CONTRIBUTING.md`.
- Agent operating rules: `AGENTS.md` and `docs/context-maintenance.md`.

### 7. Conflict handling

Classify findings before editing:

- **Index drift**: broken links, missing docs in Docs Index, stale repo tree. Auto-fix with minimal edits.
- **Stale summary**: `AGENTS.md` summary disagrees with a clear source-of-truth file. Auto-fix the summary.
- **Missing support doc**: `AGENTS.md` points to an absent core doc. Create a brief placeholder or mark as missing.
- **Semantic conflict**: source-of-truth docs disagree with each other. Do not silently resolve; report and ask the user.
- **Structural migration**: deleting, renaming, or moving many docs. Ask the user first.

Default repair order:
1. Fix `AGENTS.md` index entries.
2. Fix stale summaries from source-of-truth files.
3. Add missing placeholder docs.
4. Report unresolved semantic conflicts and gaps.

### 8. Write policy

- If generating from scratch, write `AGENTS.md` and missing supporting docs.
- If syncing, prefer minimal edits to existing files.
- If existing `AGENTS.md` has important content not captured by the template, preserve it in `## Additional Context` or move it into an appropriate doc and link it.
- Ask before overwriting substantial human-authored docs.

### 9. Report

Tell the user:
- Mode used: Init or Sync
- Files created / files updated
- `AGENTS.md` line count

**Cold-start test** — after writing, answer these 5 questions using only the generated repo docs (not your prior discovery knowledge). A fresh agent session will need to answer all five:

1. What is this system and what does it do? → answered by AGENTS.md purpose line + README pointer
2. How is it organized? → answered by Repository Map section
3. How do I run or build it? → answered by Quick Start
4. How do I validate my work? → answered by Definition of Done section
5. What is the current progress / what's next? → answered by exec-plans/active + context-maintenance.md

Report: `Cold-start test: PASS` if all five are answerable. `PARTIAL` or `FAIL` with a specific list of unanswered questions.

**Bootstrap contract** — report which of the four bootstrap conditions are satisfied or missing (from Step 2 discovery):
- Run command: found / not found
- Test/validation command: found / not found
- Progress artifact: found / not found
- Escalation rules: present / absent

**Prose-density lint** (sync mode) — list any sections flagged for prose bloat, with suggested fix.

Other items to report:
- Whether docs were scaffolded or mapped from existing structure
- Auto-fixed index drift or stale summaries
- Unresolved conflicts: missing ARCHITECTURE.md, empty docs, stale active plans, semantic conflicts, broken AGENTS links

## Hard Constraints

- `AGENTS.md` ≤ 120 lines — cut prose, not structure
- No large content blocks — pointers only
- Tree must reflect actual filesystem
- Escalation section is mandatory
- Supporting docs must be created or updated when `AGENTS.md` points to them
- Existing human-authored content must be preserved unless the user confirms replacement
