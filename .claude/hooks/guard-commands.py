#!/usr/bin/env python3
"""PreToolUse terminal hook (Bash; also VS Code, Copilot CLI and Cursor beforeShellExecution).
With PROFILE=supervised it blocks the irreversible or what a human decides; with autonomous it warns.

Base rules: push --force, push to protected branches (harness.json), gh pr merge, git branch -D,
git reset --hard, rm -rf outside temp dirs. `blocked_commands` in harness.json adds the project's own
(e.g. deploy, drop database). Ignores what sits inside heredocs and echo/printf.
Inside a tester/implementer role (agent_type or HARNESS_ROLE) it also stops shell writes into `code` or
`tests` paths (`>`, `>>`, `tee`, `sed -i`, `cp`, `mv`): the barrier (guard-tests) only sees Edit/Write, so a
heredoc into src/ would cross it unseen (measured in the lab, 2026-10-08). Write with Edit/Write instead.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import is_code, is_test, load, relative  # noqa: E402
from _harness import command, read, respond, role  # noqa: E402
from _profile import blocks, read_profile  # noqa: E402

HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\1\s*$", re.S | re.M)
SEPARATORS = re.compile(r"\s*(?:&&|\|\||;|\||\n)\s*")


def rules(cfg):
    protected = "|".join(re.escape(r) for r in cfg["protected_branches"]) or "main"
    base = [
        (re.compile(r"\bgit\s+push\b.*(\s--force(-with-lease)?\b|\s-f\b)"),
         "never force-push shared branches. If the branch is wrong, open another one."),
        (re.compile(r"\bgit\s+push\b[^\n]*(?:\s|:)(" + protected + r")(?:/\S*)?(?=\s|$)"),
         "no direct pushes to protected branches. Push your <type>/<slug> branch and open a PR."),
        (re.compile(r"\bgh\s+pr\s+merge\b"), "merging is a human decision, never the agent's."),
        (re.compile(r"\bgit\s+branch\s+(-D|--delete\s+--force)\b"), "force-deleting branches is irreversible."),
        (re.compile(r"\bgit\s+reset\s+--hard\b"), "discards work with no way back; stash or branch first."),
        (re.compile(r"\brm\s+-rf?\s+/(?!tmp/|private/tmp/)"), "rm -rf outside temp directories."),
    ]
    for r in cfg.get("blocked_commands") or []:
        try:
            base.append((re.compile(r["pattern"]), r.get("reason", "blocked by harness.json")))
        except Exception:
            continue
    return base


def segments(cmd):
    without_heredoc = HEREDOC.sub("", cmd)
    out = []
    for seg in SEPARATORS.split(without_heredoc):
        seg = seg.strip()
        if not seg or seg.startswith("#") or seg.startswith("echo ") or seg.startswith("printf "):
            continue
        out.append(seg)
    return out


WRITE_TARGETS = [
    re.compile(r"(?:^|[^<>])>{1,2}\s*([^\s;&|]+)"),
    re.compile(r"\btee\s+(?:-a\s+)?([^\s;&|]+)"),
    re.compile(r"\bsed\s+-i\S*\s+(?:-e\s+)?(?:'[^']*'|\"[^\"]*\"|\S+)\s+([^\s;&|]+)"),
    re.compile(r"\b(?:cp|mv)\s+(?:-\S+\s+)*\S+\s+([^\s;&|]+)"),
]


def role_write(cmd, cfg, cwd, who):
    """Reason if a tester/implementer writes into code/tests through the shell; '' otherwise."""
    if who not in ("tester", "implementer"):
        return ""
    import shlex
    for seg in segments(cmd):
        targets = []
        if re.search(r"\bsed\s+-i", seg):  # sed -i [suffix] [-e script]… FILE: the file is the last token
            try:
                targets.append(shlex.split(seg)[-1])
            except ValueError:
                targets.append(seg.split()[-1])
        for pat in WRITE_TARGETS:
            targets.extend(pat.findall(seg))
        for target in targets:
            if True:
                rel = relative(target, cwd)
                if rel and (is_test(rel, cfg) or is_code(rel, cfg)):
                    return (f"inside the {who} role, {rel} must be written with Edit/Write so the barrier "
                            "(guard-tests) sees it; shell writes bypass it.")
    return ""


def evaluate(cmd, profile, cfg, cwd=None, who=""):
    reason = role_write(cmd, cfg, cwd or os.getcwd(), who)
    if reason:
        if not blocks(profile):
            return "warn", f"Warning (autonomous profile): {reason}"
        return "block", f"BLOCKED by the supervised profile: {reason}"
    cmd = "\n".join(segments(cmd))
    if not cmd:
        return None, None
    for pattern, reason in rules(cfg):
        if pattern.search(cmd):
            if not blocks(profile):
                return "warn", f"Warning (autonomous profile): \"{cmd[:80]}\" {reason}"
            return "block", (f"BLOCKED by the supervised profile (.claude/profile.env): \"{cmd[:120]}\"\n"
                             f"Reason: {reason}\n"
                             "If it is really needed, the supervisor runs it or switches to PROFILE=autonomous.")
    return None, None


def main():
    ev = read()
    if not ev:
        return 0
    cmd = command(ev)
    if not cmd:
        return 0
    cfg = load(ev["cwd"])
    level, text = evaluate(cmd, read_profile(ev["cwd"]).get("PROFILE"), cfg, ev["cwd"], role(ev))
    if not level:
        return 0
    return respond(ev, level, text)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
