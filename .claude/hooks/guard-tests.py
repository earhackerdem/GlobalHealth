#!/usr/bin/env python3
"""PreToolUse edit hook (Edit|Write|MultiEdit|NotebookEdit; also VS Code): the information barrier between the
tester and the implementer of a development task.

  role `tester`      may edit only `tests` paths (harness.json); editing other `code` is blocked.
  role `implementer` may edit anything except `tests` paths.
  no role            silent. `tests` empty → silent (the barrier is off).
The role is the subagent's `agent_type` (Claude Code passes it to hooks inside subagents) or HARNESS_ROLE in the
environment (other harnesses, sequential sessions, `make hook-test`). PROFILE=supervised blocks, autonomous warns.
Memory, docs and the agentic layer (`exempt`) are never blocked. Exit is always 0; the block travels in the JSON.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import is_code, is_exempt, is_test, load, relative  # noqa: E402
from _harness import file_path, read, respond, role  # noqa: E402
from _profile import blocks, read_profile  # noqa: E402

ROLES = ("tester", "implementer")


def verdict(rel, cfg, who):
    """Reason to stop, or '' if the edit is fine for this role."""
    if who not in ROLES or not cfg.get("tests") or not rel or is_exempt(rel, cfg):
        return ""
    test = is_test(rel, cfg)
    if who == "implementer" and test:
        return (f"the implementer does not edit tests ({rel}). A test that looks wrong goes back to the tester with "
                "the reason; it is not adjusted to pass.")
    if who == "tester" and not test and is_code(rel, cfg):
        return (f"the tester does not edit implementation ({rel}). Tests are written from the criteria and the "
                "interface contract, not from the code.")
    return ""


def main():
    ev = read()
    if not ev:
        return 0
    fp = file_path(ev)
    if not fp:
        return 0
    cfg = load(ev["cwd"])
    rel = relative(fp, ev["cwd"])
    who = role(ev)
    reason = verdict(rel, cfg, who)
    if not reason:
        return 0
    msg = f"Tester/implementer barrier: {reason}"
    if blocks(read_profile(ev["cwd"]).get("PROFILE")):
        return respond(ev, "block", "BLOCKED (supervised profile). " + msg)
    return respond(ev, "warn", "Warning (autonomous profile): " + msg)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
