import hashlib
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import yaml

WIKI_DIR = Path("wiki")
TODAY = datetime.today()
STALE_DAYS = 180

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def extract_frontmatter(content: str):
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except Exception:
        return None


def compute_sha256(path: Path):
    if not path.exists():
        return None
    with path.open("rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def find_wikilinks(content: str):
    return WIKILINK_RE.findall(content)


def normalize_link_target(link: str) -> str:
    target = link.split("|", 1)[0].strip()
    target = target.split("#", 1)[0].strip()
    if target.endswith(".md"):
        target = target[:-3]
    return target


def parse_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def is_source_page(path: Path, fm: dict) -> bool:
    return path.parts[:2] == ("wiki", "sources") or "raw_file" in fm or "raw_sha256" in fm


def collect_markdown_files():
    return sorted(path for path in WIKI_DIR.rglob("*.md"))


def build_page_indexes(all_files):
    by_stem = defaultdict(list)
    by_rel = {}
    for path in all_files:
        rel_no_ext = path.relative_to(WIKI_DIR).with_suffix("")
        by_stem[path.stem].append(path)
        by_rel[str(rel_no_ext).replace("\\", "/")] = path
    return by_stem, by_rel


def resolve_wikilink(target: str, by_stem, by_rel) -> bool:
    if not target:
        return True
    normalized = target.strip().replace("\\", "/")
    if normalized in by_rel:
        return True
    if normalized.startswith("wiki/") and normalized[5:] in by_rel:
        return True
    if "/" in normalized:
        return normalized in by_rel
    return normalized in by_stem


all_files = collect_markdown_files()
by_stem, by_rel = build_page_indexes(all_files)
errors = []

for path in all_files:
    content = read_file(path)
    fm = extract_frontmatter(content)

    if fm is None:
        errors.append(f"[NO FRONTMATTER] {path}")
        continue

    if "type" not in fm:
        errors.append(f"[MISSING TYPE] {path}")

    if not any(key in fm for key in ("date", "created", "updated")):
        errors.append(f"[MISSING TIMESTAMP] {path}")

    if len(content.strip()) < 100:
        errors.append(f"[STUB] {path}")

    updated = parse_date(fm.get("updated") or fm.get("date") or fm.get("created"))
    if updated and TODAY - updated > timedelta(days=STALE_DAYS):
        errors.append(f"[STALE] {path}")

    if is_source_page(path, fm):
        raw_file = fm.get("raw_file")
        if raw_file:
            raw_path = Path(raw_file)
            if not raw_path.exists():
                errors.append(f"[RAW MISSING] {path} -> {raw_path}")
            stored_hash = fm.get("raw_sha256")
            if stored_hash and raw_path.exists():
                current_hash = compute_sha256(raw_path)
                if current_hash != stored_hash:
                    errors.append(f"[HASH MISMATCH] {path}")

        # Also validate every path in the `sources:` list field
        sources_list = fm.get("sources")
        if isinstance(sources_list, list):
            for src_path_str in sources_list:
                if isinstance(src_path_str, str):
                    src_path = Path(src_path_str)
                    if not src_path.exists():
                        errors.append(f"[SOURCE MISSING] {path} -> {src_path}")

    for link in find_wikilinks(content):
        target = normalize_link_target(link)
        if not resolve_wikilink(target, by_stem, by_rel):
            errors.append(f"[BROKEN LINK] {path} -> [[{link}]]")


duplicate_stems = {stem: paths for stem, paths in by_stem.items() if len(paths) > 1}
for stem, paths in sorted(duplicate_stems.items()):
    joined = ", ".join(str(path) for path in paths)
    errors.append(f"[DUPLICATE STEM] {stem}: {joined}")


print("\n=== LINT REPORT ===\n")

if not errors:
    print("✅ No issues found")
else:
    for error in sorted(errors):
        print("❌", error)

print(f"\nTotal issues: {len(errors)}")
