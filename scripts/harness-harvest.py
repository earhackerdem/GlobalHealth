#!/usr/bin/env python3
"""make harness-harvest SRC=../project — lessons from a project back into the template, read-only.

Compares the project's meta-improvements (memory/meta-improvements/, or the old single file) against this
template's, and prints the ones the template does not have yet. It changes nothing: the human decides what goes
upstream and how (inspired by harness2's persistent improvement harness, 2026-10)."""

import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".claude", "hooks"))
import _memory  # noqa: E402


def entries(root: pathlib.Path) -> list[str]:
    """One line per meta-improvement: its date and title, from memory/meta-improvements/ (or the old single file)."""
    return [f"{e.date} · {e.title}" for e in _memory.entries(str(root), "meta-improvements")]


def key(entry: str) -> str:
    return re.sub(r"\W+", "", entry.lower())[:90]


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1]:
        print("usage: make harness-harvest SRC=../project", file=sys.stderr)
        return 2
    src = pathlib.Path(sys.argv[1]).expanduser()
    if not (src / "memory").is_dir():
        print(f"✗ {src}/memory not found", file=sys.stderr)
        return 1
    proj = src / "memory" / "meta-improvements"
    template = pathlib.Path(__file__).resolve().parent.parent
    have = {key(e) for e in entries(template)}
    candidates = [e for e in entries(src) if key(e) not in have]
    if not candidates:
        print(
            f"✓ nothing to harvest: every entry in {proj} is already in the template's meta-improvements."
        )
        return 0
    print(f"{len(candidates)} candidate lesson(s) in {proj} not in the template yet:\n")
    for e in candidates:
        print(f"  · {e[:240]}")
    print(
        "\nHarvest is read-only: bring the ones that generalize into the template via its own change"
        " (memory/meta-improvements/ + the skill/hook/doc they fix), and mark the project row as upstreamed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
