# LLM Wiki Skills

Codex skills for researching, ingesting, saving, and linting LLM wiki notes.

## Skills

- `llm-wiki-research`: Research workflow for LLM wiki entries.
- `llm-wiki-ingest`: Ingest workflow for converting source material into wiki notes.
- `llm-wiki-save`: Save workflow for finalizing wiki notes.
- `llm-wiki-lint`: Lint workflow and helper script for wiki note quality checks.

## Install

Copy the skills you want into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/llm-wiki-* ~/.codex/skills/
```

For local development, symlink a skill instead:

```bash
ln -s "$PWD/skills/llm-wiki-research" ~/.codex/skills/llm-wiki-research
```

Restart Codex or reload skills after installing.

## Repository Layout

```text
skills/
  llm-wiki-research/
    SKILL.md
    skill.yaml
  llm-wiki-ingest/
    SKILL.md
    skill.yaml
  llm-wiki-save/
    SKILL.md
    skill.yaml
  llm-wiki-lint/
    SKILL.md
    skill.yaml
    lint.py
```

## License

MIT
