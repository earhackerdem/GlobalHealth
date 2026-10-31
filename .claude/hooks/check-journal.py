#!/usr/bin/env python3
"""Stop hook: if the session wrote code (`code` paths) or agentic layer and left no entry in
memory/journal/, blocks the close ONCE with a reminder; afterwards it lets it through.
Source: the transcript (Edit/Write and mentions of memory/journal in Bash). No transcript → no journal check.
Known limitation: what is written through the shell (cat, sed, heredoc) is not seen as work.
It also blocks if a memory entry the branch or the working tree touched has a broken frontmatter (C-16), once per set
of problems (a new broken entry later in the session blocks again; the same set does not): the
source is git (against the base branch, plus uncommitted and untracked files), so it sees what the shell wrote too,
and an entry already broken on the base does not count. Same rules as doctor (`_memory.entry_problems`).
"""
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import is_code, is_harness, load, relative  # noqa: E402
from _memory import entry_kind, file_problems  # noqa: E402

JOURNAL = re.compile(r"(^|/)memory/journal/[^/]+\.md$")


def written_paths(transcript):
    paths = set()
    with open(transcript, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if '"tool_use"' not in line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            for block in ((ev.get("message") or {}).get("content") or []):
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name, inp = block.get("name") or "", block.get("input") or {}
                if name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
                    fp = inp.get("file_path") or inp.get("notebook_path")
                    if fp:
                        paths.add(fp)
                elif name == "Bash":
                    for m in re.finditer(r"[\w./-]*memory/journal/[\w.-]+\.md", inp.get("command") or ""):
                        paths.add(m.group(0))
    return paths


def _git(cwd, *args):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=10)
    return r.stdout.splitlines() if r.returncode == 0 else None


def _git_paths(cwd, *args):
    """Paths from a `-z` git listing, unquoted (git quotes non-ASCII names otherwise: «señal.md»)."""
    r = subprocess.run(["git", *args, "-z"], cwd=cwd, capture_output=True, text=True, timeout=10)
    return [p for p in r.stdout.split("\0") if p] if r.returncode == 0 else []


def touched_entries(cwd):
    """(worktree top, [rel]) of the memory entries this branch changed against its base, plus uncommitted and untracked."""
    top = (_git(cwd, "rev-parse", "--show-toplevel") or [""])[0]
    if not top:
        return "", []
    head = (_git(top, "symbolic-ref", "--quiet", "--short", "HEAD") or [""])[0]
    origin = (_git(top, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD") or [""])[0]
    rels = set()
    for base in (origin, "origin/main", "origin/master", "main", "master"):
        if base and base != head and _git(top, "rev-parse", "--verify", "--quiet", base + "^{commit}"):
            rels.update(_git_paths(top, "diff", "--name-only", "--diff-filter=AMR", base + "...HEAD"))
            break
    rels.update(_git_paths(top, "diff", "--name-only", "--diff-filter=AMR", "HEAD"))
    rels.update(_git_paths(top, "ls-files", "--others", "--exclude-standard"))
    return top, sorted(r for r in rels if entry_kind(r))


def memory_problems(cwd):
    top, rels = touched_entries(cwd)
    return [(r, m) for r in rels for m in file_problems(os.path.join(top, r), r)]


def memory_reason(bad):
    return ("A memory entry this branch touched does not parse as one (make inbox, make closed and doctor read it); "
            "fix its frontmatter before closing: " + "; ".join(f"{r}: {m}" for r, m in bad[:8])
            + (" …" if len(bad) > 8 else "") + ".")


def journal_reason(data, cwd):
    transcript = data.get("transcript_path") or ""
    if not transcript or not os.path.isfile(transcript):
        return ""
    cfg = load(cwd)
    rels = [relative(r, cwd) for r in written_paths(transcript)]
    rels = [r for r in rels if r]
    work = sorted(r for r in rels if is_code(r, cfg) or is_harness(r))
    if not work or any(JOURNAL.search(r) for r in rels):
        return ""
    return ("This session wrote substantial work and left no journal entry. Before closing, create "
            "memory/journal/YYYY-MM-DD-slug.md with: who → intent → what was done → verification → debt. "
            "Files touched: " + ", ".join(work[:8]) + (" …" if len(work) > 8 else "")
            + ". If it really doesn't deserve a journal entry, say so in one line and close.")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("stop_hook_active"):
        return 0
    sid = data.get("session_id") or "nosession"
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    tmp = tempfile.gettempdir()
    reasons = []
    # memory: the marker keeps the problems it already reported, so the same set does not block twice but a new one
    # (another entry broken later in the session) does
    marker = os.path.join(tmp, f"harness-memory-warned-{sid}")
    try:
        bad = memory_problems(cwd)
        seen = open(marker, encoding="utf-8").read() if os.path.exists(marker) else ""
        now = "\n".join(f"{r}\t{m}" for r, m in bad)
        if bad and now != seen:
            with open(marker, "w", encoding="utf-8") as f:
                f.write(now)
            reasons.append(memory_reason(bad))
    except Exception:
        pass
    marker = os.path.join(tmp, f"harness-journal-warned-{sid}")
    if not os.path.exists(marker):
        try:
            reason = journal_reason(data, cwd)
        except Exception:
            reason = ""
        if reason:
            open(marker, "w").close()
            reasons.append(reason)
    if reasons:
        print(json.dumps({"decision": "block", "reason": "\n\n".join(reasons)}, ensure_ascii=False))
    return 0


sys.exit(main())
