#!/usr/bin/env python3
"""Create missing workspace rule files from bundled UTF-8 templates."""

import argparse
import json
import os
from pathlib import Path
import sys


FILENAMES = ("AGENTS.md", "工作须知.md")
MARKER = "{{WORKSPACE_ROOT}}"
ASSETS = Path(__file__).resolve().parent.parent / "assets"


def find_existing(root, name):
    matches = [p for p in root.iterdir() if p.name.casefold() == name.casefold()]
    if len(matches) > 1:
        raise ValueError(f"Multiple case variants exist for {name}: {matches}")
    if not matches:
        return None
    path = matches[0]
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Existing target is not a regular file: {path}")
    return path


def initialize(root, dry_run=False):
    root = Path(root)
    if not root.is_absolute():
        raise ValueError("--root must be an absolute workspace path")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Workspace is not a directory: {root}")

    plans = []
    for name in FILENAMES:
        existing = find_existing(root, name)
        if existing is not None:
            plans.append((existing, None))
            continue
        template = (ASSETS / name).read_text(encoding="utf-8-sig")
        if MARKER not in template:
            raise ValueError(f"Missing workspace placeholder in template: {name}")
        rendered = template.replace(MARKER, str(root))
        if MARKER in rendered:
            raise ValueError(f"Unresolved workspace placeholder: {name}")
        plans.append((root / name, rendered))

    files = []
    for path, rendered in plans:
        if rendered is None:
            status = "preserved"
        elif dry_run:
            status = "would_create"
        else:
            try:
                # O_EXCL prevents overwriting a file created after preflight.
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
            except FileExistsError as exc:
                raise ValueError(f"Target appeared during creation; rerun inspection: {path}") from exc
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
            status = "created"
        files.append({"path": str(path), "status": status})
    return {"root": str(root), "dry_run": dry_run, "files": files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Existing absolute workspace root")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    args = parser.parse_args()
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        result = initialize(args.root, args.dry_run)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
