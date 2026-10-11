# What each IDE reads and enforces

A single source of rules (`AGENTS.md`) and a single skills folder (`.agents/skills/`); the rest are bridges.

| | Claude Code | Cursor | VS Code (Copilot) | Antigravity |
|---|---|---|---|---|
| **Rules** | `CLAUDE.md` with `@AGENTS.md` (import; Claude reads `AGENTS.md` natively only when no `CLAUDE.md`/`CLAUDE.local.md` exists, v2.1.277+) | `AGENTS.md` + `.cursor/rules/harness.mdc` | `AGENTS.md` (`chat.useAgentsMdFile`) + `.github/copilot-instructions.md` | `AGENTS.md` + `.agents/rules/epe.md` |
| **Skills** | `.claude/skills/*` = symlinks (`make skills-link`) | `.agents/skills/` directly | `.agents/skills/` directly | `.agents/skills/` directly |
| **Hooks** | all (`.claude/settings.json`) | `.cursor/hooks.json`: sessionStart and beforeShellExecution | `.github/hooks/guardrails.json`: all | none |
| **Plan gate** | blocks / warns | **no pre-edit event**: discipline | blocks / warns | discipline |
| **Tester/implementer barrier** (`guard-tests`) | blocks / warns, by the subagent's `agent_type` | no pre-edit event: `make tdd-check` only | blocks / warns with `HARNESS_ROLE` | `make tdd-check` only |
| **Terminal guard** | blocks / warns | blocks / asks for confirmation | blocks / warns | discipline |
| **Agents** (`.claude/agents/`) | yes | no | no | no |

The hooks are a single set in `.claude/hooks/`: `_harness.py` recognizes each IDE's payload and answers with its
blocking JSON. Exit is always 0: the block goes in the JSON.

**Consequence for profiles**: the supervised profile is only truly protected in Claude Code and VS Code. In Cursor
the terminal guard works but not the plan gate; in Antigravity nothing is enforced.

**Verification status**: the hooks are tested live in Claude Code; in Cursor and VS Code only with the payloads from
their documentation, not inside the IDE. Sources (2026-10-07): code.claude.com/docs/en/skills · cursor.com/docs/{skills,rules,hooks}
· code.visualstudio.com/docs/agent-customization/{agent-skills,custom-instructions,hooks} · antigravity.google/docs/{skills,rules}.

## Maintenance
- New skill: folder at `.agents/skills/<name>/SKILL.md` and `make skills-link`. `make skills-check` reviews it.
- New hook: in `.claude/hooks/`, reading with `_harness.read()` and answering with `_harness.respond()`;
  register it in `.claude/settings.json`, `.github/hooks/guardrails.json` and, if Cursor has the event, `.cursor/hooks.json`.
- Project `make` recipes go in `project.mk` (included by the harness Makefile, never updated over).
- The plan gate reads `harness.json → plan_file` (default `plan.md`): point it at `design.md` or an OpenSpec artifact if the plan lives there.
- Test a hook: `make hook-test HOOK=gate-plan PAYLOAD_FILE=/tmp/p.json PROFILE=supervised` (the payload goes in a file: if it were inline, `guard-commands` would read it as a command).
