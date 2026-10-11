# Instructions for Copilot (VS Code)

The rules of this repo live in **[AGENTS.md](../AGENTS.md)**: read it in full before working and follow it (EPE
cycle, supervised/autonomous profiles, skeptical partner, memory in the repo). Skills live in `.agents/skills/` and
VS Code discovers them on its own.

The guardrails in `.claude/hooks/` also run here from `.github/hooks/guardrails.json` when the local agent's hooks
are enabled; if not, the same rules apply **by discipline**: without an approved `plan.md`, nothing marked as `code`
in `harness.json` gets edited, and the supervised profile never merges or pushes to protected branches.
What each IDE reads and enforces: `docs/ides.md`.
