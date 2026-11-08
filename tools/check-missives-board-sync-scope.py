#!/usr/bin/env python3
"""Verify that an applied Missives board candidate matches its reviewed source manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def git(source: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--manifest", type=Path, default=Path("fixes/missives-board-sync-source-manifest.json"))
    args = parser.parse_args()
    source = args.source.resolve()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    base = manifest["base_commit"]
    actual_commit = git(source, "rev-parse", "HEAD")
    if actual_commit != base:
        raise SystemExit(f"Wrong source base: expected {base}, got {actual_commit}")

    actual_names = set(git(source, "diff", "--name-only", base).splitlines())
    actual_names.update(git(source, "ls-files", "--others", "--exclude-standard").splitlines())
    expected_files: dict[str, str | None] = manifest["files"]
    expected_names = set(expected_files)
    if actual_names != expected_names:
        raise SystemExit(
            f"Source scope mismatch: missing={sorted(expected_names-actual_names)}, "
            f"unexpected={sorted(actual_names-expected_names)}"
        )

    for relative, expected_hash in expected_files.items():
        path = source / relative
        if expected_hash is None:
            if path.exists():
                raise SystemExit(f"Expected deleted source still exists: {relative}")
            continue
        if not path.is_file():
            raise SystemExit(f"Manifest source file is missing: {relative}")
        content = path.read_bytes().replace(b"\r\n", b"\n")
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != expected_hash:
            raise SystemExit(f"Source hash mismatch: {relative}")

    print(json.dumps({"base_commit": base, "changed_files": len(actual_names), "manifest": "verified"}, indent=2))


if __name__ == "__main__":
    main()
