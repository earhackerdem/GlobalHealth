#!/usr/bin/env python3
"""Mechanical sweep of the repo's memory/ and of the agent's PRIVATE memory (~/.claude/projects/<slug>/memory/).

Repo memory (one file per entry): two decision files with the same id (two branches took it), an entry with an
unknown status or no date, an old single file (inbox.md…) that is still there or came back, and lines of
CHANGELOG.md that no fragment renders (an entry written by hand instead of in changelog.d/).

NOT a gate: always exits 0. It generates leads for /epe-memory. What a script can decide: broken [[x]]
links, MEMORY.md pointers to missing files and memories without a pointer, frontmatter without `type:`,
paths of this repo that no longer exist, PRs treated as live that are closed (only with `gh`). What it
cannot: whether the content is still true. Noise rule measured at origin: a PR cited as provenance never expires.
"""
import argparse
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".claude", "hooks"))
import _memory  # noqa: E402

LIVE_CONTEXT = re.compile(r"not merged|unmerged|pending merge|awaiting|waiting|still open|remains open|yet to merge|"
                          r"sin fusionar|pendiente de fusi|todav[ií]a abierto|sigue abierto", re.I)
ALREADY_FIXED = re.compile(r"corrected|fixed|amendment|used to say|no longer (?:exists|applies|lives)|MERGED|CLOSED|"
                           r"was merged|previous version|corregid[ao]|enmienda|dec[ií]a|ya no (?:existe|aplica|vive)", re.I)
PR_RE = re.compile(r"PR\s*\*{0,2}\s*#(\d+)")
PATH_RE = re.compile(r"`((?:\.claude|\.agents|memory|scripts|docs|changes)/[A-Za-z0-9_./-]+)`")
LINK_RE = re.compile(r"\[\[([a-z0-9][a-z0-9#-]*)\]\]")
POINTER_RE = re.compile(r"\]\(([A-Za-z0-9_-]+\.md)\)")
TYPE_RE = re.compile(r"^\s*type:\s*(user|feedback|project|reference)\s*$", re.M)


def memory_dir(repo):
    slug = str(repo).replace("/", "-")
    d = pathlib.Path.home() / ".claude" / "projects" / slug / "memory"
    return d if d.is_dir() else None


def pr_state(num, repo):
    try:
        r = subprocess.run(["gh", "pr", "view", num, "--json", "state", "-q", ".state"], cwd=repo,
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() or None
    except Exception:
        return None


def repo_leads(repo):
    leads = list(_memory.problems(str(repo)))
    changelog = repo / "CHANGELOG.md"
    if (repo / "changelog.d").is_dir() and changelog.is_file():
        rendered = _memory.render_changelog(str(repo))
        stray = [ln for ln in changelog.read_text(encoding="utf-8").splitlines() if ln.strip() and ln not in rendered]
        if stray:
            leads.append(("CHANGELOG.md", f"{len(stray)} line(s) no fragment renders, e.g. «{stray[0][:80]}»: "
                                          "move them to a changelog.d/ fragment, then `make changelog`"))
    print("== Repo memory (memory/, changelog.d/)")
    for where, msg in leads:
        print(f"   ✗ {where}: {msg}")
    if not leads:
        print("   ✓ one file per entry, ids unique, statuses known.")
    return leads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir")
    ap.add_argument("--root")
    args = ap.parse_args()
    repo = pathlib.Path(args.root or os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())).resolve()
    repo_leads(repo)
    print("\n== Private memory")
    mem = pathlib.Path(args.dir).resolve() if args.dir else memory_dir(repo)
    if not mem or not mem.is_dir():
        print("ℹ  No private memory directory to sweep (yet).")
        return 0
    files = sorted(p for p in mem.glob("*.md") if p.name != "MEMORY.md")
    index = mem / "MEMORY.md"
    itxt = index.read_text(encoding="utf-8") if index.is_file() else ""
    leads, names = [], {p.stem for p in files}
    for f in files:
        txt = f.read_text(encoding="utf-8")
        if not TYPE_RE.search(txt):
            leads.append((f.name, "⚠", "frontmatter without `type:` (user|feedback|project|reference)"))
        for slug in sorted(set(LINK_RE.findall(txt))):
            if slug.split("#")[0] not in names and not slug.startswith("decisions"):
                leads.append((f.name, "✗", f"broken link: [[{slug}]]"))
        for m in PATH_RE.finditer(txt):
            path = m.group(1)
            if (repo / path).exists():
                continue
            window = txt[max(0, m.start() - 160):m.end() + 160]
            if not ALREADY_FIXED.search(window):
                leads.append((f.name, "✗", f"missing path: `{path}`"))
        for m in PR_RE.finditer(txt):
            window = txt[max(0, m.start() - 160):m.end() + 160]
            if not LIVE_CONTEXT.search(window) or ALREADY_FIXED.search(window):
                continue
            st = pr_state(m.group(1), repo)
            if st and st != "OPEN":
                leads.append((f.name, "✗", f"PR #{m.group(1)} is {st} but the text treats it as live"))
    if itxt:
        pointed = set(POINTER_RE.findall(itxt))
        for p in sorted(pointed):
            if not (mem / p).is_file():
                leads.append(("MEMORY.md", "✗", f"points to `{p}`, which does not exist"))
        for f in files:
            if f.name not in pointed:
                leads.append(("MEMORY.md", "⚠", f"`{f.name}` has no pointer in the index"))
    if not leads:
        print(f"✓ {len(files)} memories swept: no mechanical leads.")
    else:
        current = None
        for name, sign, detail in leads:
            if name != current:
                print(f"\n📄 {name}")
                current = name
            print(f"   {sign} {detail}")
        print(f"\n{len(leads)} leads in {len(files)} memories.")
    print("\nℹ  Not a gate, and it cannot see whether the content is still true: /epe-memory reads that.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ℹ  check-memory skipped due to an error: {e}")
        sys.exit(0)
