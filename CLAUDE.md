# CLAUDE.md

@AGENTS.md

The line above imports the repo rules from **AGENTS.md**, the single source shared with Cursor, Copilot, Codex and
Antigravity: Claude Code loads them with this file at every start (an `@` import, not a reminder to go read them).
Keep it first. This file only adds what is specific to Claude Code.

## What can't be hooked
The **skeptical partner** principle (AGENTS.md) is enforced by no hook: it depends on you. Before executing anything
substantive, name the assumption, verify it and offer an alternative. It's the rule most easily forgotten in a hurry.

## Active hooks (`.claude/settings.json`)
| Event | Hook | What it does |
|---|---|---|
| SessionStart | `profile.py` | who you work with and their PROFILE (supervised blocks / autonomous warns) |
| SessionStart | `session-guard.py` | branch, live/zombie worktrees, dirty tree from someone else (snapshot for `guard-git-add`) |
| SessionStart | `inbox.py` | up to 3 open items from `memory/inbox/` |
| SessionStart | `memory-compaction.py notify` | unswept compactions (`/epe-memory`) |
| UserPromptSubmit | `skill-nudge.py` | suggests the skill for the topic (`harness.json` → `skill_hints`), once per session |
| PreToolUse Bash | `guard-commands.py` | push to protected branches, force, merge, reset --hard, rm -rf, plus `blocked_commands` |
| PreToolUse Bash | `guard-git-add.py` | blocks `git add -A`/`commit -a` if you started with someone else's changes |
| PreToolUse Edit/Write | `gate-plan.py` | editing `code` requires `.epe/active` + `plan.md` with `Status: APPROVED` |
| PreToolUse Edit/Write | `guard-tests.py` | inside a `tester` subagent, only `tests` paths; inside an `implementer`, never `tests` (role = `agent_type`, or `HARNESS_ROLE`) |
| PreToolUse Agent | `guard-review-brief.py` | an adversarial-review subagent must carry the closed index (`make closed`) in its prompt |
| PreToolUse Chrome | `guard-browser.py` | the browser tools are allowed without a prompt (exploratory pass), and navigation is fenced to local files (`file://`), localhost, `*.localhost`, `*.test` and `harness.json → browser_hosts`; blocks in both profiles |
| PostToolUse Edit/Write | `lint.py` | py_compile · json · xml · bash -n over `code` and the agentic layer |
| Stop | `check-journal.py` | if you wrote work but no journal entry, blocks the close once |
| PreCompact | `memory-compaction.py mark` | leaves the breadcrumb to sweep later |

The same hooks run in VS Code (`.github/hooks/`) and, those with an event, in Cursor (`.cursor/hooks.json`);
`_harness.py` adapts the format (docs/ides.md). On any error, hooks exit 0: they never break the flow.
Documented escapes: `NO-CLOSED: <reason>` in the prompt of a subagent that isn't a review one.

## Known limit of the edit hooks
`gate-plan`, `lint` and `check-journal` see the Edit/Write tools. **What gets written through Bash (`cat`, `sed`,
heredoc) they don't see**, and in bypass mode the agent tends to write that way (measured at origin: 10 writes, 0
warnings). This isn't fixed by parsing the command (every unforeseen form would be a false negative): it's declared,
and in those sessions the rule depends on you again. If you're starting with this repo, start in the default mode or
`acceptEdits`.

## Private memory vs repo memory
Your private memory (`~/.claude/projects/<slug>/memory/`) keeps how to work with this repo and this person.
Everything another person or session needs to read goes to the repo's `memory/`. When in doubt, the repo.
`/epe-memory` sweeps both.

## Agents
`cold-reader` (one section, no context: where it stumbles) and `dod-checker` (checklist against artifact). Their
results are hypotheses the writer verifies, never the close. `tester` and `implementer` execute one development task
each side of the barrier (`/epe-3-execute`); you re-run red and green yourself and you commit, they don't.
