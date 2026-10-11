#!/usr/bin/env python3
"""`make inbox` — lists the whole inbox in memory/inbox.md: open, snoozed (with date) and closed.
The SessionStart hook shows at most 3 open items so it doesn't become a banner nobody reads; this is the
full view on demand. Changes nothing. On error or missing file, says so and exits 0.
"""
import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "memory", "inbox.md")


def section(text, title):
    m = re.search(rf"^## {title}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def rows(block):
    out = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[\s\-:|]+\|$", line):
            continue
        cells = [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", line.strip("|"))]
        if len(cells) < 3 or cells[0].lower().startswith("date"):
            continue
        out.append(cells)
    return out


def clean(s, n=110):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\[\[(.+?)\]\]", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    return s if len(s) <= n else s[: n - 1] + "…"


def main():
    if not os.path.isfile(PATH):
        print("(memory/inbox.md does not exist — nothing to list)")
        return 0
    text = open(PATH, encoding="utf-8").read()
    today = datetime.date.today()
    open_items, snoozed = [], []
    for cells in rows(section(text, "Open")):
        if len(cells) < 4:
            continue
        date, what, _, status = cells[:4]
        m = re.search(r"(\d{4}-\d{2}-\d{2})", status) if "💤" in status else None
        if m:
            try:
                until = datetime.date.fromisoformat(m.group(1))
                (snoozed if until > today else open_items).append((date, what, until))
                continue
            except ValueError:
                pass
        if "✅" in status or "❌" in status:
            continue
        open_items.append((date, what, None))
    closed = rows(section(text, "Closed"))

    print("📥 Inbox — memory/inbox.md\n")
    if open_items:
        print(f"🆕 OPEN ({len(open_items)}), oldest first:")
        for date, what, due in sorted(open_items, key=lambda r: r[0]):
            note = f"  (snoozed until {due}, overdue)" if due else ""
            print(f"   [{date}] {clean(what)}{note}")
    else:
        print("🆕 OPEN: none.")
    if snoozed:
        print(f"\n💤 SNOOZED ({len(snoozed)}):")
        for date, what, until in sorted(snoozed, key=lambda r: r[2]):
            print(f"   [{date}] {clean(what)}  → back on {until}")
    if closed:
        print(f"\n✅❌ CLOSED ({len(closed)}):")
        for cells in closed:
            print(f"   [{cells[0]}] {clean(cells[1], 80)}  → {clean(cells[-1], 60)}")
    if len(open_items) >= 10:
        print(f"\n⚠️ {len(open_items)} open. The hook only shows 3, so the rest is invisible at session start:\n   triage is due, not a higher cap.")
    print("\nThis is an inbox, not a plan: nothing here starts without the person you work with saying so.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"(inbox: {e})")
        sys.exit(0)
