#!/usr/bin/env python3
"""make harness-harvest SRC=../project — lessons from a project back into the template, read-only.

Compares the project's memory/meta-improvements.md entries (table rows and '- [date]' bullets) against this
template's, and prints the ones the template does not have yet. It changes nothing: the human decides what goes
upstream and how (inspired by harness2's persistent improvement harness, 2026-10)."""

import pathlib
import re
import sys


def entries(path: pathlib.Path) -> list[str]:
    if not path.exists():
        return []
    txt = path.read_text(encoding="utf-8")
    out: list[str] = []
    for line in txt.splitlines():
        s = line.strip()
        if (
            s.startswith("|")
            and not set(s) <= {"|", "-", " ", ":"}
            and not s.lower().startswith("| date")
        ):
            out.append(s)
    bullet = None
    for line in txt.splitlines():
        if re.match(r"^- \[\d{4}", line):
            if bullet:
                out.append(bullet)
            bullet = line.strip()
        elif bullet is not None and (line.startswith("  ") and line.strip()):
            bullet += " " + line.strip()
        else:
            if bullet:
                out.append(bullet)
            bullet = None
    if bullet:
        out.append(bullet)
    return out


def key(entry: str) -> str:
    return re.sub(r"\W+", "", entry.lower())[:90]


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1]:
        print("usage: make harness-harvest SRC=../project", file=sys.stderr)
        return 2
    src = pathlib.Path(sys.argv[1]).expanduser()
    proj = src / "memory" / "meta-improvements.md"
    if not proj.exists():
        print(f"✗ {proj} not found", file=sys.stderr)
        return 1
    template = (
        pathlib.Path(__file__).resolve().parent.parent
        / "memory"
        / "meta-improvements.md"
    )
    have = {key(e) for e in entries(template)}
    candidates = [e for e in entries(proj) if key(e) not in have]
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
        " (memory/meta-improvements.md + the skill/hook/doc they fix), and mark the project row as upstreamed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
