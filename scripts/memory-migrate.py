#!/usr/bin/env python3
"""make memory-migrate [DRY_RUN=1] — the old single memory files become one file per entry.

memory/inbox.md, closed.md, decisions.md, research.md and meta-improvements.md become folders with one file per
record (layout in .claude/hooks/_memory.py); each file's title, legend and stray prose go to the folder's README.md.
CHANGELOG.md keeps rendering the same text, now from changelog.d/_legacy.md plus one fragment per future change.

Lossless by check, not by intent: before anything is written, every non-empty line of every old file must be found
in the new files (a table row counts when each of its cells is), except the table structure itself (`## Open`,
`## Closed`, header and separator rows). One line missing and nothing is written. Record text is moved, never
rewritten. Idempotent: entries already present in a folder are skipped, so a second run, or a run after a branch
brought an old file back, only adds what is new. Exit 0 done or nothing to do · 1 coverage failed · 2 misuse.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), ".claude", "hooks"))
import _memory as M  # noqa: E402

TEMPLATES = os.path.join(os.path.dirname(HERE), ".agents", "skills", "epe-0-new", "templates", "common")
WRITING = "## Writing an entry"


def norm(s):
    s = s.replace("\\|", "|").strip()
    s = re.sub(r"^-\s+", "", s)
    return re.sub(r"\s+", " ", s)


def structural(line, legend_open):
    s = line.strip()
    if re.match(r"^## (open|closed|abiertos?|cerrados?)\s*$", s, re.I):
        return True
    if s.startswith("|"):
        if M.SEP_ROW.match(s) and not legend_open:
            return True
        cells = M._cells(s)
        return cells[0].lower() in ("date", "fecha")
    return False


def missing(source, haystack):
    """Non-structural lines of `source` that the new files do not carry."""
    out, legend = [], False
    for line in source.splitlines():
        s = line.strip()
        if not s:
            legend = False
            continue
        if s.startswith("|") and not M.SEP_ROW.match(s):
            first = M._cells(s)[0]
            legend = legend or not (M.DATE.fullmatch(first) or first.lower() in ("date", "fecha"))
        elif not s.startswith("|"):
            legend = False
        if structural(line, legend):
            continue
        if norm(s) in haystack:
            continue
        if s.startswith("|") and all(norm(c) in haystack for c in M._cells(s) if c):
            continue
        out.append(line)
    return out


def writing_section(kind):
    path = os.path.join(TEMPLATES, "memory", kind, "README.md")
    if not os.path.isfile(path):
        return ""
    text = M.read(path)
    i = text.find(WRITING)
    return text[i:].strip() if i >= 0 else ""


def plan_kind(root, kind):
    """(files {relpath: text}, entries, notes, source) for one old file, or None when there is none."""
    src = M.monolith(root, kind)
    if not os.path.isfile(src):
        return None
    source = M.read(src)
    readme_lines, found = M.parse_monolith(source, kind)
    folder = os.path.join("memory", kind)
    existing = M.load_dir(root, kind)
    have = {M.key(e) for e in existing}
    taken = {e.stem for e in existing}
    files, new, notes = {}, [], []
    for e in found:
        if M.key(e) in have:
            continue
        have.add(M.key(e))
        stem = e.stem if kind in ("decisions", "research") else f"{e.date}-{M.slugify(e.title)}"
        base, n = stem, 2
        while stem in taken:
            stem, n = f"{base}-{n}", n + 1
        taken.add(stem)
        e.stem = stem
        files[os.path.join(folder, stem + ".md")] = e.text()
        new.append(e)
        if e.note:
            notes.append(f"{stem}: {e.note}")
    readme_path = os.path.join(folder, "README.md")
    readme = "\n".join(readme_lines).strip("\n")
    howto = writing_section(kind)
    current = M.read(os.path.join(root, readme_path)) if os.path.isfile(os.path.join(root, readme_path)) else ""
    if not current:
        files[readme_path] = readme + ("\n\n" + howto if howto and WRITING not in readme else "") + "\n"
    else:
        extra = [ln for ln in readme_lines if ln.strip() and norm(ln) not in norm_text(current)]
        if extra:
            files[readme_path] = current.rstrip("\n") + f"\n\n## Carried over from {kind}.md\n\n" + "\n".join(extra) + "\n"
    return files, new, notes, source


def norm_text(text):
    return "\n".join(norm(ln) for ln in text.splitlines())


def plan_changelog(root):
    old = os.path.join(root, "CHANGELOG.md")
    legacy = os.path.join("changelog.d", "_legacy.md")
    if not os.path.isfile(old) or os.path.isfile(os.path.join(root, legacy)):
        return {}
    files = {legacy: M.read(old)}
    howto = os.path.join(TEMPLATES, "changelog.d", "README.md")
    if os.path.isfile(howto) and not os.path.isfile(os.path.join(root, "changelog.d", "README.md")):
        files[os.path.join("changelog.d", "README.md")] = M.read(howto)
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=os.path.dirname(HERE))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "memory")):
        print(f"✗ {root}/memory does not exist", file=sys.stderr)
        return 2

    plans = {k: p for k in M.KINDS if (p := plan_kind(root, k))}
    changelog = plan_changelog(root)
    if not plans and not changelog:
        print("✓ nothing to migrate: memory is already one file per entry.")
        return 0

    failures = []
    for kind, (files, _, _, source) in plans.items():
        already = "\n".join(M.read(e.path) for e in M.load_dir(root, kind))
        haystack = norm_text("\n".join(files.values()) + "\n" + already)
        readme = os.path.join(root, "memory", kind, "README.md")
        if os.path.isfile(readme):
            haystack += "\n" + norm_text(M.read(readme))
        failures += [(f"memory/{kind}.md", ln) for ln in missing(source, haystack)]
    if failures:
        print(f"✗ coverage check failed: {len(failures)} line(s) of the old files would be lost. Nothing written.")
        for where, line in failures[:40]:
            print(f"   {where}: {line[:160]}")
        return 1

    verb = "would write" if args.dry_run else "wrote"
    for kind, (files, new, notes, _) in plans.items():
        counts = {}
        for e in new:
            counts[e.status or "-"] = counts.get(e.status or "-", 0) + 1
        summary = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
        print(f"memory/{kind}.md → memory/{kind}/: {verb} {len(new)} entries" + (f" ({summary})" if summary else "")
              + (", README.md" if any(p.endswith("README.md") for p in files) else ""))
        for e in new[:3]:
            print(f"   · {e.stem}.md")
        if len(new) > 3:
            print(f"   · … {len(new) - 3} more")
        for n in notes:
            print(f"   ⚠ {n}")
    if changelog:
        print(f"CHANGELOG.md → changelog.d/_legacy.md: {verb}; CHANGELOG.md is rendered from changelog.d/ from now on")
    print("Coverage: every non-empty line of the old files is in the new ones.")
    if args.dry_run:
        print("\nDry run: nothing written. Without DRY_RUN the old files are removed after writing.")
        return 0

    for files in [p[0] for p in plans.values()] + [changelog]:
        for rel, text in files.items():
            path = os.path.join(root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
    if changelog:
        with open(os.path.join(root, "CHANGELOG.md"), "w", encoding="utf-8") as fh:
            fh.write(M.render_changelog(root))
    for kind in plans:
        os.remove(M.monolith(root, kind))
    print("\nOld files removed. Next: `make inbox`, `make closed`, `make memory-check`, then commit memory/ "
          "changelog.d/ CHANGELOG.md in their own PR (merge open PRs that touch memory first, or re-run this after).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
