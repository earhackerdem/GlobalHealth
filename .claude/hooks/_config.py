"""Harness configuration: `harness.json` at the project root. Imported by the hooks.

The harness works with no configuration (defaults), with one caveat: without `code` the plan gate
(`gate-plan.py`) watches no path, because it does not know what counts as code.

Keys:
  flavor             development | content | mixed (informational, used by skills and templates)
  changes_dir        folder of EPE change folders (one folder per change)
  engine             epe (change folders under changes_dir) | openspec (openspec/changes/<id>, make engine-openspec)
  openspec_version   pinned OpenSpec CLI version used by the engine scripts
  plan_file          file inside the active change that carries `Status: APPROVED` (default plan.md; design.md under openspec)
  code               path prefixes (relative to the root) that require an approved plan and count as
                     work for the journal. In a content project, the content folder IS the code.
  tests              prefixes or globs of test paths (e.g. "tests/", "src/**/*.test.ts"). Used by
                     guard-tests.py (a tester edits only tests; an implementer never edits them) and by
                     scripts/tdd-check.py. Empty = the barrier is off.
  roles              auto (default: tester/implementer only for tickets with 3+ criteria or 2+ implementation
                     files) | always | never. Read by the plan skill; tdd-check verifies commits either way.
  exempt             prefixes or globs that never require a plan (memory/, docs/, product/, the agentic layer,
                     changes_dir; "vendor/*/docs/" exempts that folder inside every vendored repo). README* and
                     CHANGELOG* are always exempt. `code` accepts the same prefixes or globs.
  phase_skills       {"explore": [skill…], "plan": […], "execute": […], "review": […]}: the project's domain
                     skills (platform catalogs, stack conventions, house templates) that the EPE skills load in
                     their Phase 0. The generic cycle learns the stack from them instead of being forked.
  protected_branches branch names that never receive a direct push
  blocked_commands   [{"pattern": regex, "reason": text}] added by guard-commands to the base rules
  skill_hints        [{"skill": name, "pattern": regex, "only_without_active"?: bool}] for the skill-nudge hook
  lint               true/false: PostToolUse lint.py (py_compile, json, xml, bash -n)
  browser_hosts      extra hosts the browser tools may navigate to (guard-browser.py), besides localhost,
                     127.0.0.1, [::1], *.localhost and *.test; "host" exact or ".domain" with its subdomains
"""
import fnmatch
import json
import os
import subprocess

HARNESS = (".claude/", ".agents/", "scripts/", ".github/", ".cursor/")
HARNESS_FILES = ("Makefile", "harness.json", "AGENTS.md", "CLAUDE.md")

DEFAULTS = {
    "name": "",
    "flavor": "development",
    "changes_dir": "changes",
    "engine": "epe",
    "plan_file": "plan.md",
    "code": [],
    "tests": [],
    "exempt": ["memory/", "docs/", "product/", ".claude/", ".agents/", ".github/", ".cursor/", ".vscode/"],
    "protected_branches": ["main", "master", "release", "production", "prod"],
    "blocked_commands": [],
    "browser_hosts": [],
    "skill_hints": [],
    "phase_skills": {},
    "lint": True,
}


def root(cwd):
    """Root of the MAIN worktree (harness.json and profile.env live there). Without git, the cwd."""
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        if common:
            return os.path.dirname(common)
    except Exception:
        pass
    return cwd


def load(cwd):
    cfg = dict(DEFAULTS)
    path = os.path.join(root(cwd), "harness.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            cfg.update({k: v for k, v in data.items() if v is not None})
    except Exception:
        pass
    changes = (cfg.get("changes_dir") or "changes").strip("/") + "/"
    exempt = list(cfg.get("exempt") or [])
    if changes not in exempt:
        exempt.append(changes)
    cfg["exempt"] = exempt
    cfg["code"] = [p for p in (cfg.get("code") or []) if isinstance(p, str) and p]
    cfg["tests"] = [p for p in (cfg.get("tests") or []) if isinstance(p, str) and p]
    return cfg


def relative(path, cwd):
    """Path relative to the project root, with / separators. None if outside the project."""
    if not path:
        return None
    base = os.path.realpath(root(cwd))
    absolute = path if os.path.isabs(path) else os.path.join(cwd, path)
    try:
        rel = os.path.relpath(os.path.realpath(absolute), base)
    except ValueError:
        return None
    if rel.startswith(".."):
        return None
    return rel.replace("\\", "/")


def matches(rel, patterns):
    """Prefix ("src/") or glob ("vendor/*/docs/") match of a relative path against a list."""
    for p in patterns or []:
        p = (p or "").strip("/")
        if not p:
            continue
        if any(ch in p for ch in "*?["):
            if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel, p + "/*"):
                return True
        elif rel.startswith(p + "/") or rel == p:
            return True
    return False


def is_exempt(rel, cfg):
    name = os.path.basename(rel)
    if name.startswith("README") or name.startswith("CHANGELOG"):
        return True
    return matches(rel, cfg["exempt"])


def is_code(rel, cfg):
    """Does this path require an approved plan? `code` prefixes or globs minus the exempt ones."""
    if not rel or is_exempt(rel, cfg):
        return False
    return matches(rel, cfg["code"])


def is_test(rel, cfg):
    """Is this path a test? `tests` entries are prefixes ("tests/") or globs ("src/**/*.test.ts")."""
    if not rel:
        return False
    for p in cfg.get("tests") or []:
        if any(ch in p for ch in "*?["):
            if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(os.path.basename(rel), p):
                return True
            if "**" in p and fnmatch.fnmatch(rel, p.replace("**/", "")):
                return True
        elif rel.startswith(p.strip("/") + "/") or rel == p.strip("/"):
            return True
    return False


def is_harness(rel):
    """Is it the repo's own agentic layer? Counts as work for the journal."""
    if not rel:
        return False
    return rel.startswith(HARNESS) or rel in HARNESS_FILES or rel.startswith("scripts/")
