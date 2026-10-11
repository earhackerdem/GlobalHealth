#!/usr/bin/env python3
"""Cursor sessionStart: runs the startup hooks from .claude/hooks and returns their text as
additional_context (Cursor's format). Exits 0 on error."""
import json
import os
import subprocess
import sys

ROOT = os.environ.get("CURSOR_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOOKS = [["profile.py"], ["session-guard.py"], ["inbox.py"], ["memory-compaction.py", "notify"]]


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ""
    parts = []
    for h in HOOKS:
        path = os.path.join(ROOT, ".claude", "hooks", h[0])
        if not os.path.isfile(path):
            continue
        try:
            res = subprocess.run([sys.executable, path, *h[1:]], input=raw, capture_output=True, text=True, timeout=20, cwd=ROOT)
        except Exception:
            continue
        out = (res.stdout or "").strip()
        if not out:
            continue
        try:
            out = (json.loads(out).get("hookSpecificOutput") or {}).get("additionalContext") or ""
        except Exception:
            pass
        if out:
            parts.append(out)
    if parts:
        print(json.dumps({"additional_context": "\n\n".join(parts)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
