#!/usr/bin/env python3
"""Stop hook: if the session wrote code (`code` paths) or agentic layer and left no entry in
memory/journal/, blocks the close ONCE with a reminder; afterwards it lets it through.
Source: the transcript (Edit/Write and mentions of memory/journal in Bash). No transcript → exit 0.
Known limitation: what is written through the shell (cat, sed, heredoc) is not seen as work.
"""
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import is_code, is_harness, load, relative  # noqa: E402

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


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("stop_hook_active"):
        return 0
    transcript = data.get("transcript_path") or ""
    if not transcript or not os.path.isfile(transcript):
        return 0
    sid = data.get("session_id") or "nosession"
    marker = os.path.join(tempfile.gettempdir(), f"harness-journal-warned-{sid}")
    if os.path.exists(marker):
        return 0
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    cfg = load(cwd)
    rels = [relative(r, cwd) for r in written_paths(transcript)]
    rels = [r for r in rels if r]
    work = sorted(r for r in rels if is_code(r, cfg) or is_harness(r))
    if not work or any(JOURNAL.search(r) for r in rels):
        return 0
    open(marker, "w").close()
    print(json.dumps({"decision": "block", "reason": (
        "This session wrote substantial work and left no journal entry. Before closing, create "
        "memory/journal/YYYY-MM-DD-slug.md with: who → intent → what was done → verification → debt. "
        "Files touched: " + ", ".join(work[:8]) + (" …" if len(work) > 8 else "")
        + ". If it really doesn't deserve a journal entry, say so in one line and close.")}, ensure_ascii=False))
    return 0


sys.exit(main())
