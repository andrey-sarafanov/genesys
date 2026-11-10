#!/usr/bin/env python3
"""List or copy reviewed local skill folders. No network calls or tenant actions."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

SKILLS = ("genesys-reporting", "genesys-cx-as-code", "genesys-performance-investigator")
SOURCE_ROOT = Path(__file__).resolve().parent / "skills"

def files_for(source: Path):
    entries = list(source.rglob("*"))
    if source.is_symlink() or any(p.is_symlink() for p in entries):
        raise ValueError(f"Symlink in skill source: {source.name}")
    if not (source / "SKILL.md").is_file():
        raise ValueError(f"Missing SKILL.md: {source}")
    return [p for p in entries if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")]

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List skills, file counts and helper scripts; do not install")
    parser.add_argument("--skill", action="append", choices=SKILLS, help="Install only this skill; repeat to select several (default: all)")
    parser.add_argument("--dest", type=Path, default=Path.home() / ".agents" / "skills", help="Skills destination (default: ~/.agents/skills)")
    parser.add_argument("--dry-run", action="store_true", help="Validate selection and show destinations without writing")
    args = parser.parse_args(argv)
    try:
        selected = list(dict.fromkeys(args.skill or SKILLS))
        for name in selected:
            files = files_for(SOURCE_ROOT / name)
            if args.list:
                helpers = [p.relative_to(SOURCE_ROOT / name).as_posix() for p in files if p.parent.name == "scripts"]
                print(f"{name} ({len(files)} files)")
                print(f"  Instructions: skills/{name}/SKILL.md")
                print("  Helpers: " + (", ".join(helpers) if helpers else "none; instruction/reference skill"))
        if args.list:
            return 0
        destination = args.dest.expanduser().resolve()
        source_resolved = SOURCE_ROOT.resolve()
        if destination == source_resolved or source_resolved in destination.parents:
            raise ValueError("Destination must not be inside this repository's source skills/ tree.")
        for name in selected:
            target = destination / name
            if target.exists() or target.is_symlink():
                raise ValueError(f"Already exists: {target}. Nothing installed. Choose another --dest, or review/back up the existing skill first.")
        for name in selected:
            target = destination / name
            print(f"{'Would install' if args.dry_run else 'Installing'} {name} -> {target}")
        if args.dry_run:
            print("Dry run complete. No files written.")
            return 0
        destination.mkdir(parents=True, exist_ok=True)
        for name in selected:
            shutil.copytree(SOURCE_ROOT / name, destination / name,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        print("Installed. The skills should be detected automatically; reopen your client if they do not appear.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Install stopped: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
