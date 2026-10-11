#!/usr/bin/env python3
"""PreToolUse edit hook (Edit|Write|MultiEdit; also VS Code and Copilot CLI): the deterministic gate of
the EPE cycle. Cursor has no pre-edit event: there the gate is discipline.

Editing a `code` path (harness.json) requires an active change with an approved plan:
  - `.epe/active` at the root contains the change path (e.g. changes/C-01-slug)
  - `<change>/<plan_file>` contains the line `Status: APPROVED` (harness.json → plan_file, default plan.md; set it
    to design.md or an OpenSpec artifact when the plan lives there: no bridge file needed)
PROFILE=supervised → blocks. PROFILE=autonomous → warns once per session.
/epe-2-plan writes it on "plan approved"; /epe-6-archive removes it. Exit is always 0.
"""
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import is_code, load, relative, root  # noqa: E402
from _harness import file_path, read, respond  # noqa: E402
from _profile import blocks, read_profile  # noqa: E402


def plan_approved(base, plan_file="plan.md"):
    active = os.path.join(base, ".epe", "active")
    try:
        change = open(active, encoding="utf-8").read().strip()
    except FileNotFoundError:
        return False, "there is no active change (.epe/active does not exist; `make epe-new SLUG=<slug>`)"
    plan = os.path.join(base, change, plan_file)
    if not os.path.isfile(plan):
        return False, f"the active change \"{change}\" has no {plan_file}"
    if not re.search(r"^Status:\s*APPROVED", open(plan, encoding="utf-8").read(), re.M):
        return False, f"{change}/{plan_file} has no line `Status: APPROVED`"
    return True, ""


def main():
    ev = read()
    if not ev:
        return 0
    fp = file_path(ev)
    if not fp:
        return 0
    cfg = load(ev["cwd"])
    rel = relative(fp, ev["cwd"])
    if not rel or not is_code(rel, cfg):
        return 0
    ok, detail = plan_approved(root(ev["cwd"]), cfg.get("plan_file") or "plan.md")
    if ok:
        return 0
    msg = (f"EPE gate: you are about to edit code ({rel}) but {detail}.\n"
           "Cycle order: /epe-1-explore → /epe-2-plan (the person you work with writes \"plan approved\") → /epe-3-execute.")
    profile = read_profile(ev["cwd"]).get("PROFILE")
    if not blocks(profile):
        marker = os.path.join(tempfile.gettempdir(), f"harness-gate-plan-warned-{ev['sid']}")
        if os.path.exists(marker):
            return 0
        open(marker, "w").close()
        return respond(ev, "warn", "Warning (autonomous profile, shown once per session): " + msg)
    return respond(ev, "block", "BLOCKED (supervised profile). " + msg)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
