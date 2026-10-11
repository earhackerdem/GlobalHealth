---
trigger: glob
globs: "changes/**"
description: EPE cycle (Explore · Plan · Execute) when touching a change folder
---

When touching a change folder, respect the order and the templates in `.agents/skills/epe-0-new/templates/<flavor>/`:
`story.md` (input with acceptance criteria) → `exploration.md` → `plan.md` (one test per criterion; nothing is
edited until `Status: APPROVED`) → `tasks.md` → `evidence.md` → `validation.md` (non-technical, for whoever approves).
The detail of each phase is in `.agents/skills/epe-*/SKILL.md`. The general rules, in `AGENTS.md`.
