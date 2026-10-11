#!/usr/bin/env python3
"""Red before green, verified by git: the tests of a task were committed BEFORE the implementation and were not
touched since.

Finds the newest commit whose subject starts with `test` (`test:` / `test(scope):`) on the current branch since
--since (default: the merge-base with the default branch, or the root commit) and checks that the `tests` paths of
harness.json (or --tests) have no diff between that commit and the working tree. What it cannot check: that the
red run really failed; that is the orchestrator's job and its numbers go to evidence.md.

Also, if the active change's tasks.md (.epe/active, or --tasks) tags N tasks `test→impl`, there must be at least N
`test:` commits since the base: one red per group, so Execution granularity is verified, not remembered (two lab runs
collapsed everything into one red, 2026-10-08).
Exit 0 clean · 1 failure (no red commit, tests changed after it, or fewer reds than groups) · 2 not a git repo. Usage:
  python3 scripts/tdd-check.py [--since REF] [--tests PATH ...] [--tasks FILE] [--root DIR]
"""
import argparse
import json
import os
import subprocess
import sys


def git(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def default_since(root):
    for base in ("main", "master"):
        code, out = git(root, "merge-base", base, "HEAD")
        if code == 0 and out:
            _, head = git(root, "rev-parse", "HEAD")
            if out != head:
                return out
    code, out = git(root, "rev-list", "--max-parents=0", "HEAD")
    return out.splitlines()[-1] if code == 0 and out else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="", help="ref the task started from (default: merge-base with main/master, or the root commit)")
    ap.add_argument("--tests", nargs="*", default=None, help="test paths (default: harness.json → tests)")
    ap.add_argument("--tasks", default="", help="tasks.md to count `test→impl` groups (default: <.epe/active>/tasks.md)")
    ap.add_argument("--root", default=os.getcwd())
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    if git(root, "rev-parse", "--is-inside-work-tree")[0] != 0:
        print("tdd-check: not a git repository"); return 2
    tests = a.tests
    if tests is None:
        try:
            tests = json.load(open(os.path.join(root, "harness.json"), encoding="utf-8")).get("tests") or []
        except Exception:
            tests = []
    tests = [t for t in tests if isinstance(t, str) and t]
    if not tests:
        print("tdd-check: harness.json → tests is empty; nothing to check (fill it or pass --tests)"); return 1
    since = a.since or default_since(root)
    if not since:
        print("tdd-check: no commits yet; the red commit cannot exist"); return 1
    rng = f"{since}..HEAD" if git(root, "rev-parse", "HEAD")[1] != since else "HEAD"
    code, log = git(root, "log", "--format=%H %s", rng)
    red = ""
    reds = []
    for line in log.splitlines():
        sha, _, subject = line.partition(" ")
        if subject.startswith("test"):
            reds.append(sha)
            if not red:
                red = sha; red_subject = subject
    if not red:
        print(f"tdd-check: ✗ no `test:` commit in {rng}. The tester commits the failing tests before the implementer starts.")
        return 1
    tasks_file = a.tasks
    if not tasks_file:
        try:
            active = open(os.path.join(root, ".epe", "active"), encoding="utf-8").read().strip()
            tasks_file = os.path.join(root, active, "tasks.md")
        except FileNotFoundError:
            tasks_file = ""
    groups = 0
    if tasks_file and os.path.isfile(tasks_file):
        import re
        groups = len(re.findall(r"^\s*- \[[ xX]\].*test(?:→|->)impl", open(tasks_file, encoding="utf-8").read(), re.M))
    if groups and len(reds) < groups:
        print(f"tdd-check: ✗ tasks.md declares {groups} test→impl group(s) but only {len(reds)} `test:` commit(s) since the base "
              f"({rng}). One red commit per group: the plan approved that granularity.")
        return 1
    pathspecs = [t.rstrip("/") if not any(c in t for c in "*?[") else f":(glob){t}" for t in tests]
    code, diff = git(root, "diff", "--stat", red, "--", *pathspecs)
    if diff:
        print(f"tdd-check: ✗ test paths changed after the red commit {red[:8]} ({red_subject}):\n{diff}")
        print("The implementer does not touch tests; if a test was wrong, the fix goes back to the tester and gets its own `test:` commit.")
        return 1
    print(f"tdd-check: ✓ red commit {red[:8]} ({red_subject}); test paths {tests} unchanged since"
          + (f"; {len(reds)} red commit(s) for {groups} test→impl group(s)" if groups else "")
          + ". Red run numbers belong in evidence.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
