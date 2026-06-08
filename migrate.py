#!/usr/bin/env python3
"""
migrate.py — Reorganise the engineering-standards repository.

Moves all flat files into two folders:
  standards/   ← 14 documentation files (00-INDEX.md … 12-ai-engineering.md)
  templates/   ← 7 template files

Then updates 25 bare template references in 4 files so they
consistently use the templates/ prefix.

Usage:
    python migrate.py [--repo PATH] [--dry-run]

Options:
    --repo PATH   Root of the git repository (default: current directory)
    --dry-run     Show what would happen without touching any files

Prerequisites:
    Run from inside a clean git working tree (no uncommitted changes).
    git must be available in PATH.
"""

import re
import subprocess
import sys
import argparse
from pathlib import Path


# ── File manifest ──────────────────────────────────────────────────────────

STANDARDS = [
    "00-INDEX.md",
    "00A-AI-OPERATING-PROTOCOL.md",
    "01-core-principles.md",
    "02-technology-radar.md",
    "03-api-design.md",
    "04-database-standards.md",
    "05-frontend-standards.md",
    "06-testing-strategy.md",
    "07-security-standards.md",
    "08-observability.md",
    "09-devops-cicd.md",
    "10-git-workflow.md",
    "11-project-management.md",
    "12-ai-engineering.md",
]

TEMPLATES = [
    "adr-template.md",
    "pr-template.md",
    "incident-report.md",
    "data-inventory.md",
    "briefing-template.md",
    "proposal-template.md",
    "project-master-template.md",
]

# ── Text replacements ──────────────────────────────────────────────────────
# Format: (file_path_after_move, regex_pattern, replacement, label)
#
# All patterns use negative lookbehind (?<!templates/) so the script is
# idempotent — running it twice never double-prefixes a reference.
#
# Files are referenced by their POST-MOVE paths (standards/X or templates/X).
# The script applies replacements after git mv, so the paths already exist.

REPLACEMENTS = [

    # ── standards/00-INDEX.md ──────────────────────────────────────────────
    # Status table   (L54–60):  all 7 templates listed bare in backticks
    # Nav table      (L126–128): 3 business templates listed bare in backticks

    (
        "standards/00-INDEX.md",
        r"(?<!templates/)`adr-template\.md`",
        "`templates/adr-template.md`",
        "00-INDEX  `adr-template.md`  → `templates/adr-template.md`",
    ),
    (
        "standards/00-INDEX.md",
        r"(?<!templates/)`pr-template\.md`",
        "`templates/pr-template.md`",
        "00-INDEX  `pr-template.md`  → `templates/pr-template.md`",
    ),
    (
        "standards/00-INDEX.md",
        r"(?<!templates/)`incident-report\.md`",
        "`templates/incident-report.md`",
        "00-INDEX  `incident-report.md`  → `templates/incident-report.md`",
    ),
    (
        "standards/00-INDEX.md",
        r"(?<!templates/)`data-inventory\.md`",
        "`templates/data-inventory.md`",
        "00-INDEX  `data-inventory.md`  → `templates/data-inventory.md`",
    ),
    (
        "standards/00-INDEX.md",
        r"(?<!templates/)`briefing-template\.md`",
        "`templates/briefing-template.md`",
        "00-INDEX  `briefing-template.md`  → `templates/briefing-template.md`",
    ),
    (
        "standards/00-INDEX.md",
        r"(?<!templates/)`proposal-template\.md`",
        "`templates/proposal-template.md`",
        "00-INDEX  `proposal-template.md`  → `templates/proposal-template.md`",
    ),
    (
        "standards/00-INDEX.md",
        r"(?<!templates/)`project-master-template\.md`",
        "`templates/project-master-template.md`",
        "00-INDEX  `project-master-template.md`  → `templates/project-master-template.md`",
    ),

    # ── standards/12-ai-engineering.md ────────────────────────────────────
    # 8× bare `adr-template.md` and 2× bare `data-inventory.md`
    # NOTE: does NOT touch `docs/data-inventory.md` (destination path, different context)

    (
        "standards/12-ai-engineering.md",
        r"(?<!templates/)`adr-template\.md`",
        "`templates/adr-template.md`",
        "12-ai-engineering  `adr-template.md`  → `templates/adr-template.md`  (8×)",
    ),
    (
        "standards/12-ai-engineering.md",
        r"(?<!templates/)`data-inventory\.md`",
        "`templates/data-inventory.md`",
        "12-ai-engineering  `data-inventory.md`  → `templates/data-inventory.md`  (2×)",
    ),

    # ── templates/briefing-template.md ────────────────────────────────────
    # L26: (→ project-master-template.md)
    # L30: → project-master-template.md — The document created FROM this briefing

    (
        "templates/briefing-template.md",
        r"(?<!templates/)project-master-template\.md",
        "templates/project-master-template.md",
        "briefing-template  project-master-template.md  → templates/project-master-template.md  (2×)",
    ),

    # ── templates/proposal-template.md ────────────────────────────────────
    # L42:  Read the project-master-template.md to understand what the
    # L57:  → briefing-template.md — Source of client requirements
    # L58:  → project-master-template.md — Internal document created after…

    (
        "templates/proposal-template.md",
        r"(?<!templates/)project-master-template\.md",
        "templates/project-master-template.md",
        "proposal-template  project-master-template.md  → templates/project-master-template.md  (2×)",
    ),
    (
        "templates/proposal-template.md",
        r"(?<!templates/)briefing-template\.md",
        "templates/briefing-template.md",
        "proposal-template  briefing-template.md  → templates/briefing-template.md  (1×)",
    ),
]


# ── Helpers ────────────────────────────────────────────────────────────────

def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def check_prerequisites(repo: Path) -> None:
    """Verify the repo is in the expected state. Exits with code 1 on failure."""
    errors = []

    # git must be available and this must be a repo
    result = run_git(["status", "--porcelain"], repo)
    if result.returncode != 0:
        errors.append(
            f"'git status' failed in {repo}.\n"
            "  Is this the root of a git repository?"
        )
    elif result.stdout.strip():
        errors.append(
            "Working tree has uncommitted changes.\n"
            "  Please commit or stash them first so that git mv shows\n"
            "  clean renames in 'git log' (not delete + add).\n"
            f"  Dirty files:\n{result.stdout.rstrip()}"
        )

    # All expected flat files must exist at the repo root
    missing = [f for f in STANDARDS + TEMPLATES if not (repo / f).exists()]
    if missing:
        errors.append(
            "Expected files not found at repo root:\n"
            + "".join(f"    {f}\n" for f in missing)
        )

    # Target folders must not already exist (guard against partial migration)
    for folder in ["standards", "templates"]:
        if (repo / folder).is_dir():
            errors.append(
                f"Folder '{folder}/' already exists in {repo}.\n"
                "  This script is designed to run once on a flat repo.\n"
                "  If the migration was partially applied, resolve manually."
            )

    if errors:
        print("\n  ❌  PREREQUISITES FAILED — no changes made\n")
        for err in errors:
            for line in err.splitlines():
                print(f"  • {line}")
        print()
        sys.exit(1)


def apply_replacements(repo: Path, dry_run: bool) -> list[tuple[str, int]]:
    """
    Apply all REPLACEMENTS entries. Returns list of (label, substitution_count).

    In live mode, files are read from their post-move paths (standards/ or templates/).
    In dry-run mode, files haven't been moved yet, so we fall back to the flat
    root location (strip the leading folder prefix) for counting purposes.
    """
    def resolve_path(filepath: str) -> Path:
        """Return the readable path for a file, accounting for dry-run state."""
        post_move = repo / filepath
        if post_move.exists():
            return post_move
        if dry_run:
            # e.g. "standards/00-INDEX.md" → "00-INDEX.md"
            flat_name = Path(filepath).name
            flat_path = repo / flat_name
            if flat_path.exists():
                return flat_path
        return post_move  # will 404 cleanly below

    # Group by file so we read/write each file exactly once
    by_file: dict[str, list[tuple[str, str, str]]] = {}
    for filepath, pattern, replacement, label in REPLACEMENTS:
        by_file.setdefault(filepath, []).append((pattern, replacement, label))

    results: list[tuple[str, int]] = []

    for filepath, ops in by_file.items():
        readable_path = resolve_path(filepath)
        write_path = repo / filepath  # always the post-move path for writing

        if not readable_path.exists():
            results.append((f"FILE NOT FOUND: {filepath}", 0))
            continue

        original = readable_path.read_text(encoding="utf-8")
        current = original

        for pattern, replacement, label in ops:
            count = len(re.findall(pattern, current))
            current = re.sub(pattern, replacement, current)
            results.append((label, count))

        if not dry_run and current != original:
            write_path.write_text(current, encoding="utf-8")

    return results


def git_mv_file(src: str, dst: str, repo: Path, dry_run: bool) -> bool:
    """Run 'git mv src dst'. Returns True on success."""
    if dry_run:
        return True
    result = run_git(["mv", src, dst], repo)
    if result.returncode != 0:
        print(f"  ❌  git mv {src} → {dst}  ({result.stderr.strip()})")
        return False
    return True


# ── Migration orchestrator ─────────────────────────────────────────────────

def migrate(repo: Path, dry_run: bool) -> None:
    repo = repo.resolve()
    prefix = "DRY RUN — " if dry_run else ""

    print(f"\n{'═' * 62}")
    print(f"  {prefix}Engineering Standards Migration")
    print(f"  Repository: {repo}")
    print(f"{'═' * 62}\n")

    if dry_run:
        print("  ℹ️   Dry-run mode: nothing will be written to disk.\n")
    else:
        check_prerequisites(repo)

    # ── Step 1: Create directories ─────────────────────────────────────────
    print(f"  {'─' * 58}")
    print("  STEP 1 — Create directories")
    print(f"  {'─' * 58}")
    for folder in ["standards", "templates"]:
        target = repo / folder
        if not dry_run:
            target.mkdir(exist_ok=True)
        verb = "would create" if dry_run else "created    "
        print(f"  📁 {verb}  {folder}/")
    print()

    # ── Step 2: Move standards ──────────────────────────────────────────────
    print(f"  {'─' * 58}")
    print("  STEP 2 — Move standards documents  →  standards/")
    print(f"  {'─' * 58}")
    moved = 0
    for f in STANDARDS:
        ok = git_mv_file(f, f"standards/{f}", repo, dry_run)
        verb = "would move" if dry_run else "moved     "
        icon = "✅" if ok else "❌"
        print(f"  {icon} {verb}  {f}")
        if ok:
            moved += 1
    print(f"\n  {moved}/{len(STANDARDS)} files moved\n")

    # ── Step 3: Move templates ──────────────────────────────────────────────
    print(f"  {'─' * 58}")
    print("  STEP 3 — Move templates  →  templates/")
    print(f"  {'─' * 58}")
    moved = 0
    for f in TEMPLATES:
        ok = git_mv_file(f, f"templates/{f}", repo, dry_run)
        verb = "would move" if dry_run else "moved     "
        icon = "✅" if ok else "❌"
        print(f"  {icon} {verb}  {f}")
        if ok:
            moved += 1
    print(f"\n  {moved}/{len(TEMPLATES)} files moved\n")

    # ── Step 4: Update bare template references ─────────────────────────────
    print(f"  {'─' * 58}")
    print("  STEP 4 — Update bare template references  (4 files, 25 refs)")
    print(f"  {'─' * 58}")
    results = apply_replacements(repo, dry_run)
    total = 0
    for label, count in results:
        verb = "would change" if dry_run else "changed     "
        icon = "✅" if count > 0 else "⚠️ "
        print(f"  {icon} {count:>2}×  {verb}  {label}")
        total += count
    print(f"\n  {total} substitutions {'would be made' if dry_run else 'made'}\n")

    # ── Done ────────────────────────────────────────────────────────────────
    print(f"  {'─' * 58}")
    if dry_run:
        print("  DRY RUN COMPLETE — no files were modified.")
        print()
        print("  To apply:  python migrate.py --repo .")
    else:
        print("  MIGRATION COMPLETE")
        print()
        print("  Recommended next steps:")
        print("  1.  python lint_refs.py --root .     ← should report 0 broken")
        print("  2.  git diff --cached                ← review staged renames")
        print("  3.  git diff                         ← review text substitutions")
        print('  4.  git add -A && git commit -m \\')
        print('        "chore: reorganise into standards/ and templates/ folders"')
    print(f"  {'─' * 58}\n")


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reorganise the engineering-standards repo into standards/ and templates/."
    )
    parser.add_argument(
        "--repo", type=Path, default=Path("."),
        help="Root of the git repository (default: current directory)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would happen without modifying any files",
    )
    args = parser.parse_args()
    migrate(args.repo, args.dry_run)


if __name__ == "__main__":
    main()
