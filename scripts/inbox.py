#!/usr/bin/env python3
"""`make inbox` — lists the whole inbox in memory/inbox/: open, snoozed (with date) and closed.
The SessionStart hook shows at most 3 open items so it doesn't become a banner nobody reads; this is the
full view on demand. Reads the old memory/inbox.md too while a project has it. Changes nothing; exits 0.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, ".claude", "hooks"))
import _memory  # noqa: E402


def main():
    root = os.environ.get("HARNESS_ROOT") or ROOT
    items = _memory.inbox(root)
    clean = _memory.clean
    if not any(items.values()):
        print("(memory/inbox/ is empty — nothing to list)")
        return 0
    open_items, snoozed, closed = items["open"], items["snoozed"], items["closed"]
    print("📥 Inbox — memory/inbox/\n")
    if open_items:
        print(f"🆕 OPEN ({len(open_items)}), oldest first:")
        for date, what, due, _ in open_items:
            note = f"  (snoozed until {due}, overdue)" if due else ""
            print(f"   [{date}] {clean(what, 110)}{note}")
    else:
        print("🆕 OPEN: none.")
    if snoozed:
        print(f"\n💤 SNOOZED ({len(snoozed)}):")
        for date, what, until, _ in snoozed:
            print(f"   [{date}] {clean(what, 110)}  → back on {until or 'no date'}")
    if closed:
        print(f"\n✅❌ CLOSED ({len(closed)}):")
        for date, what, _, e in closed:
            print(f"   [{date}] {clean(what, 80)}  → {e.status}")
    if len(open_items) >= 10:
        print(f"\n⚠️ {len(open_items)} open. The hook only shows 3, so the rest is invisible at session start:\n"
              "   triage is due, not a higher cap.")
    print("\nThis is an inbox, not a plan: nothing here starts without the person you work with saying so.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"(inbox: {e})")
        sys.exit(0)
