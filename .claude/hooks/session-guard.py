#!/usr/bin/env python3
"""SessionStart hook: concurrency guardrail between sessions.

Injects the current branch, LIVE worktrees (not zombies whose branch is already merged) and the
uncommitted changes that ALREADY existed at start, and leaves a per-session snapshot so that
`guard-git-add.py` can tell "someone else's changes" from "mine". Silent outside a git repo.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile


def git(args, cwd):
    try:
        out = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=5)
        return out.stdout if out.returncode == 0 else None
    except Exception:
        return None


def parse_worktrees(porcelain):
    worktrees, path, branch = [], None, None
    for line in porcelain.splitlines():
        if line.startswith("worktree "):
            path = line[len("worktree "):]
        elif line.startswith("branch "):
            branch = line[len("branch "):].replace("refs/heads/", "")
        elif line.startswith("detached"):
            branch = "(detached)"
        elif line.strip() == "":
            if path is not None:
                worktrees.append((path, branch or "(?)"))
            path, branch = None, None
    if path is not None:
        worktrees.append((path, branch or "(?)"))
    return worktrees


def classify_others(others, cwd):
    """ZOMBIE = branch with its own commits already merged into origin/main (or main). When in doubt, LIVE."""
    base = None
    for ref in ("origin/main", "main"):
        if git(["rev-parse", "--verify", "--quiet", ref], cwd) is not None:
            base = ref
            break
    if base is None:
        return others, []
    live, zombies = [], []
    for p, b in others:
        if not b or b == "(detached)":
            live.append((p, b))
            continue
        try:
            own = (git(["rev-list", "--count", f"{base}..{b}"], cwd) or "0").strip()
            if own == "0":
                live.append((p, b))
                continue
            r = subprocess.run(["git", "merge-base", "--is-ancestor", b, base], cwd=cwd, capture_output=True, timeout=5)
            (zombies if r.returncode == 0 else live).append((p, b))
        except Exception:
            live.append((p, b))
    return live, zombies


def snapshot_path(session_id):
    key = hashlib.sha1((session_id or "nosession").encode()).hexdigest()[:16]
    return os.path.join(tempfile.gettempdir(), f"harness-session-guard-{key}.json")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    session_id = data.get("session_id", "")
    project_dir = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    branch = git(["branch", "--show-current"], project_dir)
    if branch is None:
        return 0
    branch = branch.strip() or "(detached)"
    status = git(["status", "--porcelain"], project_dir) or ""
    dirty = [l[3:] for l in status.splitlines() if l.strip()]
    worktrees = parse_worktrees(git(["worktree", "list", "--porcelain"], project_dir) or "")
    others = [(p, b) for (p, b) in worktrees if os.path.abspath(p) != os.path.abspath(project_dir)]
    live, zombies = classify_others(others, project_dir)

    try:
        with open(snapshot_path(session_id), "w") as fh:
            json.dump({"dirty_at_start": dirty, "branch": branch}, fh)
    except Exception:
        pass

    lines = ["🔎 Concurrency guardrail (SessionStart):", f"- Directory: {project_dir}", f"- Current branch: {branch}"]
    warn = []
    if live:
        lines.append(f"- There are {len(live)} other LIVE worktree(s) in this repo:")
        lines += [f"    · {p}  [{b}]" for p, b in live]
        warn.append("Other sessions may exist: work ONLY in your branch/worktree, don't touch files in other directories.")
    else:
        lines.append("- ✅ No other live worktrees. Don't create one \"just in case\": alone, a branch is enough.")
    if zombies:
        lines.append(f"- 🧟 …and {len(zombies)} ZOMBIE worktree(s) (branch already merged): not concurrency; `make worktrees-clean`.")
    if dirty:
        lines.append(f"- ⚠️ The tree ALREADY had {len(dirty)} uncommitted change(s) at start:")
        lines += [f"    · {f}" for f in dirty[:8]]
        if len(dirty) > 8:
            lines.append(f"    · … and {len(dirty) - 8} more")
        warn.append("Those changes are NOT yours. Another session may be working in THIS directory: no `git add -A`; "
                    "stage only your paths. If you don't recognise them, stop and confirm.")
    if branch in ("main", "master"):
        warn.append(f"You are on `{branch}`. Before committing, create a `<type>/<slug>` branch (PR by default).")
    if warn:
        lines += ["", "WARNINGS:"] + [f"  ⚠️ {w}" for w in warn]
    else:
        lines.append("- ✅ No concurrency signals: clean tree and no conflicting worktrees.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(lines)}},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
