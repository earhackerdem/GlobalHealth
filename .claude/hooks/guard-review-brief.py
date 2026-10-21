#!/usr/bin/env python3
"""PreToolUse hook (Agent|Task): an adversarial-review subagent must carry the closed-verdicts index
(`make closed`, rendered from memory/closed/) INSIDE its prompt: subagents don't inherit context, and if the
index doesn't travel they re-litigate what was already decided. Checks presence, not judgement. Narrow trigger: only prompts that declare themselves a review
(adversarial/finder/validator/epe-4-review). The fixer of /epe-5-apply is exempt.
Escape: "NO-CLOSED: <reason>" in the prompt. Limitation: doesn't see agent() inside a Workflow.
Blocks via exit 2. Exit 0 on error.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _memory  # noqa: E402
from _config import root  # noqa: E402

REVIEW = re.compile(r"adversarial|\bfinders?\b|\bvalidators?\b|epe-4-review|\blens (F-|of )", re.I)
APPLYING = re.compile(r"epe-5-apply|\bfixer\b|apply (each|the|these)\s+(approved\s+)?findings?", re.I)
ESCAPE = "NO-CLOSED:"


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") not in ("Agent", "Task"):
        return 0
    prompt = (data.get("tool_input") or {}).get("prompt") or ""
    if not isinstance(prompt, str) or not prompt.strip():
        return 0
    if not REVIEW.search(prompt) or ESCAPE in prompt or APPLYING.search(prompt):
        return 0
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    marks = _memory.closed_markers(root(cwd))
    if not marks or any(m in prompt for m in marks):
        return 0
    sys.stderr.write(
        "🔒 Adversarial-review subagent WITHOUT the closed-verdicts index.\n"
        "The prompt does not contain the output of `make closed` (memory/closed/). Paste it LITERALLY with the rule: "
        "🔒 don't report · ↩️ only with new evidence · ⏸️ goes to debt · 🧩 only the missing instances.\n"
        f'If this subagent doesn\'t need it, write "{ESCAPE} <reason>" in the prompt.\n')
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
