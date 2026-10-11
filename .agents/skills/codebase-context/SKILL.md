---
name: codebase-context
description: Brownfield entry. Verifies (never generates) what an agent would otherwise rediscover at high cost in an existing codebase, and proposes a short block for AGENTS.md between <!-- harness:context --> markers: frozen paths, generated files, conventions that differ from ecosystem defaults, observed pitfalls, where work lands, required tool versions. Excludes repo overviews, directory trees and tech-stack lists. Then opens ONE bounded first change instead of documenting the system. Use when the user says "/codebase-context", "existing codebase", "brownfield", "legacy", "I inherited this repo", "onboard the agent".
argument-hint: [path to the repo root; defaults to the current project]
---

# /codebase-context — verify, don't document

Four SDD tools agree: *"You do not need to recreate an existing system from specifications"* (Spec Kit); *"you write
specs only for what you're about to change"* (OpenSpec); BMAD retired its `document-project` because *"agents read
code better than prose about code, and the copy goes stale"*. What survives is a **short, verified block** of what the
code cannot tell you by reading it. This skill writes that block and nothing else.

## Procedure
1. **Inventory what already claims to be the truth**: `README*`, `CONTRIBUTING*`, `AGENTS.md`/`CLAUDE.md`, ADRs,
   CI config, lint/format config, `package.json`/`pyproject`/`Makefile` scripts, `.env.example`, `CODEOWNERS`.
   For every claim you might copy, **verify it against the code or the config** (does the path exist? does the script
   run? is the version pinned?). Stale docs are the main source of wrong context: a claim you cannot verify is not
   written; it goes to the "unverified" list for the human.
2. **Collect only what qualifies** (each line with its evidence `file:line` or command):
   - frozen or generated paths (don't edit by hand), build outputs, vendored code;
   - conventions that **differ from the ecosystem default** (test runner, formatter, branch naming, commit prefixes,
     folder for migrations), not the defaults themselves;
   - required tool versions and how the project pins them;
   - observed pitfalls: things that break silently, env vars that must exist, order-dependent setup;
   - where work lands: which folders are "code" (→ `harness.json` → `code`), where tests live, how to run them.
   **Exclude**: repo overview, directory tree, tech-stack list, anything the agent reads better from the code.
3. **Propose the block**, 15-40 lines, between markers:
   ```
   <!-- harness:context -->
   ## Codebase context (verified YYYY-MM-DD)
   - …
   <!-- /harness:context -->
   ```
   Show it to the human **before** writing. Writing into `AGENTS.md` is the human's call (or the agent's, once approved);
   content outside the markers is never touched. For Claude Code, `CLAUDE.md` already imports `AGENTS.md`.
4. **Configure the harness**: `harness.json` → `code`, `blocked_commands` (deploy, migrations on prod, drop database),
   `skill_hints` for the stack. Run `make doctor`.
5. **Open one bounded first change** (`make epe-new SLUG=…`): something small, reviewable and reversible, with its
   `Origin:` line. The first change is how the context gets tested; the system is not documented first.
6. Journal entry listing what was verified, what was left unverified, and what was deliberately excluded.

## Maintenance (same rules as BMAD's project-context)
- **Refresh** after real code changes: re-verify paths and versions.
- **Record** a pitfall only after someone has actually hit it, with the date.
- **Audit**: the block ends *smaller or equal, never larger*. A rule leaves when what it governs no longer exists, not
  because nothing broke lately.
