#!/usr/bin/env python3
"""Worktree inventory and cleanup: tells LIVE worktrees from ZOMBIES.

Why: `git worktree list` cannot tell a worktree with work in progress from one whose branch was merged two
weeks ago and nobody removed. The SessionStart hook used to count that raw total and announced "26 more
active worktrees" when the truly active ones were zero (measured in origin: 20 of 22 were already merged).
A session read that as concurrency, isolated itself "just in case", and the content ended up in a window the
person didn't have open.

Definitions (the same the hook uses):
  ZOMBIE = its branch has its own commits and is an ancestor of origin/main (or main if there is no remote),
           i.e. already merged, and it is NOT the main worktree nor the current one. Nothing is lost by
           removing it: the work lives in history.
  LIVE   = everything else: unmerged branch, detached, or with local changes.

Safety, in this order: never touches the MAIN worktree nor the one it runs from; a zombie with uncommitted
changes is NOT removed (reported apart); by default removes nothing (dry run): ask for --clean explicitly.

Usage:
  make worktrees           # inventory: live, zombie and dirty (deletes nothing)
  make worktrees-clean     # removes clean zombies
  python3 scripts/worktrees.py [--clean]
"""
import subprocess
import sys
import os


def git(args, cwd=None):
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True,
                           text=True, timeout=15)
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None


def parse_worktrees(porcelain):
    """[(path, branch|None, detached)] from `git worktree list --porcelain`."""
    out, path, branch, det = [], None, None, False
    for line in porcelain.splitlines():
        if line.startswith("worktree "):
            path, branch, det = line[9:], None, False
        elif line.startswith("branch "):
            branch = line[7:].replace("refs/heads/", "")
        elif line.strip() == "detached":
            det = True
        elif line.strip() == "":
            if path:
                out.append((path, branch, det))
            path, branch, det = None, None, False
    if path:
        out.append((path, branch, det))
    return out


def base_ref():
    """origin/main if it exists; otherwise main. None if neither."""
    for ref in ("origin/main", "main"):
        if git(["rev-parse", "--verify", "--quiet", ref]) is not None:
            return ref
    return None


def merged(branch, base):
    """True only if the branch has its OWN commits and all of them are already in `base`.

    A freshly created branch (0 own commits) is also an ancestor of main, so a bare `--is-ancestor` would mark
    it merged and the cleanup would remove the worktree of a session that just started. No own commits → LIVE."""
    propios = (git(["rev-list", "--count", f"{base}..{branch}"]) or "0").strip()
    if propios == "0":
        return False
    r = subprocess.run(["git", "merge-base", "--is-ancestor", branch, base],
                       capture_output=True)
    return r.returncode == 0


def dirty(path):
    s = git(["status", "--porcelain"], cwd=path)
    return bool(s and s.strip())


def main():
    clean = "--clean" in sys.argv

    porcelain = git(["worktree", "list", "--porcelain"])
    if porcelain is None:
        print("Not a git repo (or `git worktree` failed): nothing to do.")
        return 0

    base = base_ref()
    if base is None:
        print("Neither `origin/main` nor `main` found: cannot decide what is merged, so nothing is removed.")
        return 0

    principal = (git(["rev-parse", "--path-format=absolute", "--git-common-dir"]) or "").strip()
    principal = os.path.dirname(principal) if principal.endswith(".git") else None
    actual = (git(["rev-parse", "--show-toplevel"]) or "").strip()

    live, zombies, dirty_ones = [], [], []
    for path, branch, det in parse_worktrees(porcelain):
        real = os.path.realpath(path)
        protegido = real in (os.path.realpath(principal or ""), os.path.realpath(actual or ""))
        if protegido or det or not branch:
            live.append((path, branch or "(detached)", "protected" if protegido else "no branch"))
        elif not merged(branch, base):
            live.append((path, branch, "unmerged branch"))
        elif dirty(path):
            dirty_ones.append((path, branch))
        else:
            zombies.append((path, branch))

    print(f"Comparison base: {base}\n")
    print(f"🟢 LIVE ({len(live)}) — untouched:")
    for p, b, reason in live:
        print(f"    {b}  ·  {reason}\n        {p}")
    if dirty_ones:
        print(f"\n⚠️  ZOMBIES WITH UNCOMMITTED CHANGES ({len(dirty_ones)}) — NOT removed:")
        for p, b in dirty_ones:
            print(f"    {b}\n        {p}")
        print("    The branch is merged, but the tree has unsaved work.")
        print("    Look yourself and decide: `git -C <path> status`.")
    print(f"\n🧟 CLEAN ZOMBIES ({len(zombies)}) — branch already merged into {base}:")
    for p, b in zombies:
        print(f"    {b}\n        {p}")

    if not zombies:
        print("\n✓ Nothing to clean.")
        return 0

    if not clean:
        print(f"\n(dry run: nothing removed. `make worktrees-clean` would remove those {len(zombies)}.)")
        return 0

    print()
    removed = 0
    for p, b in zombies:
        r = subprocess.run(["git", "worktree", "remove", p],
                           capture_output=True, text=True)
        if r.returncode == 0:
            print(f"  ✓ removed  {b}")
            removed += 1
        else:
            print(f"  ✗ could not remove {b}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else '?'}")
    subprocess.run(["git", "worktree", "prune"], capture_output=True)
    print(f"\nDone: {removed} worktree(s) removed. The branches remain in history; only the working folders are gone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
