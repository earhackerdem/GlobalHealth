#!/usr/bin/env python3
"""SessionStart hook: reminds up to 3 OPEN items from memory/inbox/ (oldest first), says how many it
hides and honours `status: snoozed YYYY-MM-DD`; reads the old memory/inbox.md too while a project has it.
A cap that lies is worse than no cap: with 10+ open items it says triage is due, not a higher cap.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _memory  # noqa: E402
from _config import root  # noqa: E402

MAX_SHOWN = 3
TRIAGE_THRESHOLD = 10


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    items = _memory.inbox(root(cwd))
    open_items = [(date, what, None) for date, what, _, _ in items["open"]]
    if not open_items:
        return 0
    shown = open_items[:MAX_SHOWN]
    hidden = len(open_items) - len(shown)
    out = ["📥 Open inbox items (memory/inbox/), a reminder, not this session's task:"]
    for date, what, _ in shown:
        what = re.sub(r"\*\*(.+?)\*\*", r"\1", what)
        out.append(f"  · [{date}] {what[:177] + '…' if len(what) > 180 else what}")
    if hidden:
        out.append(f"  … and {hidden} more not shown (`make inbox` lists them all).")
    if len(open_items) >= TRIAGE_THRESHOLD:
        out.append(f"  ⚠️ {len(open_items)} open: the inbox needs triage, not a higher cap.")
    out.append("  If the person you work with doesn't mention them, do NOT start them: ask whether any is for today.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(out)}},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
