#!/usr/bin/env python3
"""
lint_refs.py — Cross-reference linter for the engineering-standards repository.

Scans all Markdown files for  → See [...]  cross-references and verifies
that each referenced file exists somewhere in the repository.

Resolution strategy (in order):
  1. If the ref contains '/', treat it as a path relative to the repo root.
     Example: "templates/adr-template.md"  →  <root>/templates/adr-template.md
  2. If the ref is a bare filename, search the full repository index.
     Example: "04-database-standards.md"  →  found wherever it lives

This means the linter works correctly BOTH before and after the folder
reorganisation — it validates the filesystem as it currently is.

Exit codes:
  0  — all references are valid (clean)
  1  — one or more broken references found
  2  — ambiguous references found (no broken refs)

Usage:
    python lint_refs.py [--root PATH] [--verbose]
"""

import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Matches:  → See [anything here]
# The arrow can be followed by optional whitespace before "See".
SEE_REF_PATTERN = re.compile(r"→\s*See\s*\[([^\]]+)\]")

# Extracts the filename part from inside [...]:
#   "04-database-standards.md, §7"     →  "04-database-standards.md"
#   "01-core-principles.md, Section 6" →  "01-core-principles.md"
#   "templates/adr-template.md"        →  "templates/adr-template.md"
FILENAME_EXTRACT = re.compile(r"^([^,§\]]+?)(?:\s*[,§].*)?$")

# Refs that are clearly placeholders / format-documentation examples.
# These appear in "Conventions" and "AI Agent Instructions" sections and are
# intentionally not real file names.
PLACEHOLDER_PREFIXES = ("XX-",)


def is_placeholder(filename: str) -> bool:
    return any(filename.startswith(prefix) for prefix in PLACEHOLDER_PREFIXES)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Reference:
    source_file: Path           # absolute path of the file containing the ref
    line_number: int            # 1-based line number
    raw_ref: str                # full content inside [...], e.g. "04-db.md, §7"
    filename: str               # extracted filename, e.g. "04-db.md"
    status: str = "unresolved"  # "ok" | "broken" | "ambiguous"
    resolved_path: Optional[Path] = None
    candidates: list[Path] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def build_index(root: Path) -> dict[str, list[Path]]:
    """
    Walk <root> recursively and map each .md filename to all its locations.
    Hidden directories (e.g. .git) are skipped.
    """
    index: dict[str, list[Path]] = defaultdict(list)
    for md in sorted(root.rglob("*.md")):
        # Skip files inside hidden directories
        if any(part.startswith(".") for part in md.relative_to(root).parts):
            continue
        index[md.name].append(md.resolve())
    return dict(index)


def extract_refs(file_path: Path) -> list[Reference]:
    """Return all → See [...] references found in a single Markdown file."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"  WARNING: cannot read {file_path}: {exc}", file=sys.stderr)
        return []

    refs: list[Reference] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in SEE_REF_PATTERN.finditer(line):
            raw = match.group(1).strip()
            name_match = FILENAME_EXTRACT.match(raw)
            if not name_match:
                continue
            filename = name_match.group(1).strip()

            # Only track references that point to .md files
            if not filename.endswith(".md"):
                continue
            # Skip pure section markers that somehow slipped through
            if filename.startswith("§"):
                continue
            # Skip placeholder/example refs (e.g. "XX-document-name.md")
            if is_placeholder(filename):
                continue

            refs.append(Reference(
                source_file=file_path.resolve(),
                line_number=line_no,
                raw_ref=raw,
                filename=filename,
            ))
    return refs


def resolve(ref: Reference, root: Path, index: dict[str, list[Path]]) -> None:
    """
    Try to resolve ref.filename to a real file and update ref.status.

    Strategy A — path-relative (ref contains '/'):
        Treat the ref as a path from the repo root.
        Only this strategy is tried; if it fails, the ref is broken.
        Rationale: explicit paths must be exact — a fallback to the index
        would silently mask path errors.

    Strategy B — bare filename (no '/'):
        Search the repository index by filename.
        One match  → ok.  Multiple matches → ambiguous.  None → broken.
    """
    root = root.resolve()

    if "/" in ref.filename:
        # Strategy A: path relative to repo root
        candidate = root / ref.filename
        if candidate.exists():
            ref.status = "ok"
            ref.resolved_path = candidate
        else:
            ref.status = "broken"
        return

    # Strategy B: bare filename — search the index
    matches = index.get(ref.filename, [])
    if len(matches) == 1:
        ref.status = "ok"
        ref.resolved_path = matches[0]
    elif len(matches) > 1:
        ref.status = "ambiguous"
        ref.candidates = matches
    else:
        ref.status = "broken"


# ---------------------------------------------------------------------------
# Reporter
# ---------------------------------------------------------------------------

def report(all_refs: list[Reference], root: Path, verbose: bool) -> int:
    root = root.resolve()
    broken    = [r for r in all_refs if r.status == "broken"]
    ambiguous = [r for r in all_refs if r.status == "ambiguous"]
    ok        = [r for r in all_refs if r.status == "ok"]

    # ── Broken ──────────────────────────────────────────────────────────────
    if broken:
        print(f"\n  ❌  BROKEN REFERENCES  ({len(broken)})")
        print(f"  {'─' * 56}")
        by_file: dict[Path, list[Reference]] = defaultdict(list)
        for r in broken:
            by_file[r.source_file].append(r)
        for src in sorted(by_file):
            print(f"\n  📄  {src.relative_to(root)}")
            for r in sorted(by_file[src], key=lambda x: x.line_number):
                print(f"      L{r.line_number:<5} → See [{r.filename}]")

    # ── Ambiguous ────────────────────────────────────────────────────────────
    if ambiguous:
        print(f"\n  ⚠️   AMBIGUOUS REFERENCES  ({len(ambiguous)})")
        print(f"  {'─' * 56}")
        for r in ambiguous:
            print(f"\n  📄  {r.source_file.relative_to(root)}  L{r.line_number}")
            print(f"      → See [{r.filename}]  →  {len(r.candidates)} matches:")
            for c in r.candidates:
                print(f"        • {c.relative_to(root)}")

    # ── Valid (verbose only) ─────────────────────────────────────────────────
    if verbose and ok:
        print(f"\n  ✅  VALID REFERENCES  ({len(ok)})")
        print(f"  {'─' * 56}")
        by_file_ok: dict[Path, list[Reference]] = defaultdict(list)
        for r in ok:
            by_file_ok[r.source_file].append(r)
        for src in sorted(by_file_ok):
            print(f"\n  📄  {src.relative_to(root)}")
            for r in sorted(by_file_ok[src], key=lambda x: x.line_number):
                resolved = r.resolved_path.relative_to(root) if r.resolved_path else "?"
                print(f"      L{r.line_number:<5} → See [{r.filename}]  →  {resolved}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n  {'─' * 56}")
    print(f"  SUMMARY")
    print(f"  {'─' * 56}")
    print(f"  Total refs scanned : {len(all_refs)}")
    print(f"  ✅  Valid          : {len(ok)}")
    print(f"  ❌  Broken         : {len(broken)}")
    print(f"  ⚠️   Ambiguous      : {len(ambiguous)}")
    print(f"  {'─' * 56}\n")

    if not broken and not ambiguous:
        print("  ✅  All cross-references are valid.\n")
        return 0

    return 1 if broken else 2


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lint → See [...] cross-references in the engineering-standards repo."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Root directory of the repository (default: current directory)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Also print valid references",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    print(f"\n{'═' * 60}")
    print(f"  Engineering Standards — Cross-Reference Linter")
    print(f"  Root: {root}")
    print(f"{'═' * 60}")

    index = build_index(root)
    md_files = sorted({p for paths in index.values() for p in paths})
    print(f"\n  Scanning {len(md_files)} Markdown file(s)...\n")

    all_refs: list[Reference] = []
    for md in md_files:
        refs = extract_refs(md)
        for r in refs:
            resolve(r, root, index)
        all_refs.extend(refs)

    sys.exit(report(all_refs, root, args.verbose))


if __name__ == "__main__":
    main()
