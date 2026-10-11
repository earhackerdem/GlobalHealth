#!/usr/bin/env python3
"""Compaction breadcrumb + startup notice. One file, three modes:
    PreCompact   → `mark`    (writes the breadcrumb; PreCompact cannot talk to the model, measured)
    SessionStart → `notify`  (one line, only if a sweep is pending)
    make memory-swept → `swept` (records that memory was swept)
Compacting does NOT delete the transcript: the breadcrumb points to transcript_path so the sweep can
happen later with /epe-memory. State lives in ~/.claude/projects/<slug>/ (outside the repo).
"""
import datetime
import json
import os
import pathlib
import sys


def state_dir(cwd):
    slug = str(pathlib.Path(cwd).resolve()).replace("/", "-")
    d = pathlib.Path.home() / ".claude" / "projects" / slug
    return d if d.is_dir() else None


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "notify"
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    base = state_dir(cwd)
    if not base:
        return 0
    log = base / "compactions.jsonl"
    if mode == "swept":
        (base / "last-sweep").write_text(datetime.datetime.now().isoformat(timespec="seconds"), encoding="utf-8")
        print("✓ memory sweep recorded; the startup notice is reset.")
        return 0
    if mode == "mark":
        with log.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"when": datetime.datetime.now().isoformat(timespec="seconds"),
                                "trigger": data.get("trigger"), "session_id": data.get("session_id"),
                                "transcript": data.get("transcript_path")}, ensure_ascii=False) + "\n")
        return 0
    if not log.is_file():
        return 0
    mark = base / "last-sweep"
    since = mark.read_text(encoding="utf-8").strip() if mark.is_file() else ""
    pending = []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if not since or row.get("when", "") > since:
            pending.append(row)
    if not pending:
        return 0
    n = len(pending)
    print(f"🧠 {n} compaction{'' if n == 1 else 's'} without a memory sweep since the last one.\n"
          f"   Raw transcript of the latest: {pending[-1].get('transcript')}\n"
          "   If this session closes substantial work, invoke /epe-memory. It is not a task on its own.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
