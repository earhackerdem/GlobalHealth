#!/usr/bin/env python3
"""SessionStart hook: tells the agent WHO it is working with and in which PROFILE.

Reads NAME, ROLE and PROFILE from .claude/profile.env in the main worktree (local file, ignored by
git; created by `make profile`). No email on purpose: the agent does not need it and a versioned
roster would expose the team's. WARNS, never blocks: without a profile it asks to attribute neutrally.
Exits 0 on any error.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _profile import WARNS, read_profile  # noqa: E402


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    p = read_profile(cwd)
    name, role, profile = p.get("NAME", ""), p.get("ROLE", ""), p.get("PROFILE", "supervised")

    if name and role:
        if profile == WARNS:
            rule = "   Autonomous profile: guardrails warn instead of blocking.\n"
        else:
            rule = ("   Supervised profile: no code edits without an APPROVED plan.md; pushes to protected branches, "
                    "force and merge are blocked. Delivery ends at the PR.\n")
        text = (
            f"👤 You work with {name} ({role}) · PROFILE={profile} (.claude/profile.env).\n"
            + rule
            + f"- In the journal, decisions and PRs attribute by name and role (\"{name} asked…\"), never \"the user\"."
        )
    else:
        text = (
            "👤 No local profile (.claude/profile.env): you don't know who you are working with.\n"
            "- Ask for name, role and profile (supervised/autonomous) up front and offer `make profile`.\n"
            "- Without a profile the hooks assume PROFILE=supervised (the safe mode).\n"
            "- Until you know, attribute neutrally (\"it was requested\", \"the person in this session\")."
        )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
