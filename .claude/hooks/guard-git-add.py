#!/usr/bin/env python3
"""PreToolUse hook (Bash): stops `git add -A`/`git add .`/`git commit -a` ONLY if the tree was already
dirty when the session started (snapshot from session-guard.py): a sign that another session is working
in this same directory and a broad add would sweep its work. Started clean → stays out of the way.

Parses the command instead of grepping it: heredoc bodies are dropped, each `&&`/`;`/`|` segment is
tokenised with shlex, `git` global options (`-C <dir>`) and a preceding `cd <dir>` are honoured (another
repo is not this snapshot's business), and flags are only read before `-m`/`-F` values, so a commit message
containing `-authors` is not `commit -a` (false positive measured in the lab, 2026-10-08).
Blocks via exit 2 + stderr. Exit 0 on error.
"""
import hashlib
import json
import os
import re
import shlex
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import root  # noqa: E402

HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\1\s*$", re.S | re.M)
SEPARATORS = re.compile(r"\s*(?:&&|\|\||;|\||\n)\s*")
VALUE_FLAGS = {"-m", "--message", "-F", "--file", "-C", "--reuse-message", "-c", "--reedit-message",
               "--author", "--date", "-t", "--template", "--fixup", "--squash", "--trailer"}


def snapshot_path(session_id):
    key = hashlib.sha1((session_id or "nosession").encode()).hexdigest()[:16]
    return os.path.join(tempfile.gettempdir(), f"harness-session-guard-{key}.json")


def tokens(segment):
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def broad_add(args):
    for a in args:
        if a == "--":
            return False
        if a in ("-A", "--all", "-u", "--update", "--no-ignore-removal", ".", ":/", "*"):
            return True
        if a.startswith("-") and not a.startswith("--") and ("A" in a[1:] or "u" in a[1:]):
            return True
    return False


def commit_all(args):
    skip = False
    for a in args:
        if skip:
            skip = False
            continue
        if a == "--":
            return False
        if a in VALUE_FLAGS:
            skip = True
            continue
        if a in ("-a", "--all"):
            return True
        if a.startswith("-") and not a.startswith("--") and "=" not in a and "a" in a[1:]:
            return True
    return False


def broad_git(cmd, base):
    """True if some `git add`/`git commit` segment is broad AND targets this repo."""
    cwd_dir = base
    for seg in SEPARATORS.split(HEREDOC.sub("", cmd)):
        seg = seg.strip()
        if not seg or seg.startswith(("#", "echo ", "printf ")):
            continue
        t = tokens(seg)
        if not t:
            continue
        if t[0] == "cd" and len(t) > 1:
            cwd_dir = os.path.realpath(os.path.join(cwd_dir, os.path.expanduser(t[1])))
            continue
        if t[0] in ("sudo", "env", "command"):
            t = t[1:]
        if not t or t[0] != "git":
            continue
        i, target = 1, cwd_dir
        while i < len(t) and t[i].startswith("-"):
            if t[i] == "-C" and i + 1 < len(t):
                target = os.path.realpath(os.path.join(cwd_dir, os.path.expanduser(t[i + 1])))
                i += 2
            elif t[i].startswith("-C") and len(t[i]) > 2:
                target = os.path.realpath(os.path.join(cwd_dir, t[i][2:]))
                i += 1
            elif t[i] in ("-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(t):
                i += 2
            else:
                i += 1
        if i >= len(t):
            continue
        sub, args = t[i], t[i + 1:]
        if os.path.realpath(target) != os.path.realpath(base):
            continue
        if sub == "add" and broad_add(args):
            return True
        if sub == "commit" and commit_all(args):
            return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command", "")
    if not cmd or "git" not in cmd:
        return 0
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if not broad_git(cmd, root(cwd)):
        return 0
    try:
        with open(snapshot_path(data.get("session_id", ""))) as fh:
            dirty = json.load(fh).get("dirty_at_start", [])
    except Exception:
        return 0
    if not dirty:
        return 0
    preview = ", ".join(dirty[:6]) + (" …" if len(dirty) > 6 else "")
    sys.stderr.write(
        "⛔ Concurrency guardrail: blocked a broad `git add`/`git commit -a`.\n"
        f"When this session started the tree ALREADY had {len(dirty)} uncommitted change(s): {preview}.\n"
        "That suggests another session in this same directory; a broad add would sweep its work.\n"
        "→ Stage ONLY the paths you created/edited: `git add <path1> <path2> …`.\n"
        "→ If there is another session, isolate yourself in your own worktree/branch before committing.\n")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
