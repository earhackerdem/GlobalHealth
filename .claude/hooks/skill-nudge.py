#!/usr/bin/env python3
"""UserPromptSubmit hook: if the prompt touches a topic with its own skill (harness.json → skill_hints),
suggests loading it, once per skill per session. Doesn't fire on "/commands" nor when the user asks to
draft a prompt that merely mentions the topic. A rule with "only_without_active": true (e.g. triage) fires only
when there is no active change (.epe/active), which is exactly when the calibration ladder gets skipped.
"""
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import load, root  # noqa: E402

_META = re.compile(r"\b(draft\w*|write\w*|prepare\w*|red[aá]ct\w*|escrib\w*|prepar\w*)\b[^.?!\n]{0,40}\b(mega)?prompts?\b")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    prompt = (data.get("prompt") or "").lower()
    if not prompt or prompt.startswith("/") or _META.search(prompt):
        return 0
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    sid = data.get("session_id") or "nosession"
    hits = []
    active = os.path.isfile(os.path.join(root(cwd), ".epe", "active"))
    for rule in load(cwd).get("skill_hints") or []:
        try:
            if rule.get("only_without_active") and active:
                continue
            if re.search(rule["pattern"], prompt, re.I):
                marker = os.path.join(tempfile.gettempdir(), f"harness-nudge-{rule['skill']}-{sid}")
                if not os.path.exists(marker):
                    open(marker, "w").close()
                    hits.append(rule["skill"])
        except Exception:
            continue
    if hits:
        text = ("Hint (project hook): the prompt touches topics with their own skill; consider invoking "
                + ", ".join(f"Skill({s})" for s in hits) + " before working.")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": text}},
                         ensure_ascii=False))
    return 0


sys.exit(main())
