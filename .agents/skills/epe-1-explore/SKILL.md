---
name: epe-1-explore
description: EXPLORE phase of the EPE cycle. Takes the story (or brief) of the active change, validates it is complete, checks EACH acceptance criterion against what already exists (repo code, dependencies, primary sources) citing file:line or URL with date, detects non-functional constraints and classifies the change. Writes exploration.md. Does not plan or edit. Use when the user says "/epe-1-explore", "explore this story", "does this already exist?", "research before writing", or brings acceptance criteria.
argument-hint: [path to story.md; defaults to the active change in .epe/active]
---

# /epe-1-explore — what already exists and what does not fit?

Produces `exploration.md` in the change folder. **Entry gate**: no complete story, no exploration; no accepted
exploration, no plan.

## Phase 0 — load
1. Read `story.md` (argument or `.epe/active`). If it does not exist, send to `/epe-0-new`.
2. Read the **titles** of `memory/decisions/` (`ls`, or `grep -h '^## D' memory/decisions/*.md`) and `make closed`; open
   only the entries the story's `Origin:` or criteria touch. `memory/research/` only when a criterion carries a number or
   an external claim.
   Do not re-litigate or re-research what is already decided or on record.
3. In the content flavor also load `Skill(produce-content)` (stance and sources).
4. If `product/` exists, read `product/technical-brief.md` (the NFR budget and the stack are **given**: §4 starts from
   them, and the stack is not re-litigated) and the epic the story's `Origin:` line points to in `product/prd.md` (the
   FR/NFR ids it must cover). A story without `Origin:` in a project with a PRD is a question for the author, not a
   blocker.
5. Load with the Skill tool every skill listed in `harness.json → phase_skills.explore` (the project's domain
   skills: platform catalogs, stack conventions, where "what already exists" lives in this stack). They say *where to
   look and how to cite*; this skill says the order and the gate.

## With `engine: openspec`
The input is `proposal.md` plus the scenarios under `specs/` (or the request, if `/opsx:propose` has not run yet).
Phase 1 validates scenarios instead of AC (GIVEN with data, THEN observable); Phase 2's matrix has one row per
scenario; the deliverable is `exploration.md` in the OpenSpec change folder. `openspec list --specs` and
`openspec show <spec> --type spec` tell what the product already promises: a change that would MODIFY a requirement
says so in the proposal's Capabilities.

## Phase 1 — validate the input (without this, stop)
- Story "As a <concrete role>, I want…, so that…" (or a brief with audience, goal and message). Generic role = ❌.
- Each criterion with **Given / When / Then** and concrete data; a non-observable "Then" = ❌.
- A criterion that **imposes a technical solution** is marked ⚠️: it is explored anyway, but questioned.
If there is any ❌: write `exploration.md` with §1 only and ask for completion. **Do not go on.**

**Greenfield shortcut (measured: the full matrix on an empty repo costs turns and finds nothing).** If no file exists
under `harness.json → code`, §2 is one line per criterion ("❌ New — greenfield") plus, once, what the platform or
standard library already gives for the whole story; skip the repo search and go to Phase 3.

## Phase 2 — coverage matrix per criterion (the heart)
For **each** criterion, in this order, always citing something the reader can open:
1. **What the repo already does** (`grep` before claiming; `file:line`).
2. **What the dependencies / platform already do** (official docs, specific version).
3. **Primary sources** for every external claim: URL + date consulted, tagged **[VERIFIED]** or
   **[OPINION/HYPE]**. Empirical before documentary if the tool is at hand.
4. Classify: ✅ Exists (configuration/usage ticket) · 🟡 Partial (extend it) · ❌ New · ⛔ Infeasible under the
   project's constraints (mandatory alternative).
5. In §3 record what **looked useful and was not**, and why.

## Phase 3 — non-functional constraints
Start from the NFR budget in `product/technical-brief.md` if it exists: for each NFR the change touches, say how it is
met or at risk; a change that needs to break the budget changes the brief and its ADR in the same PR, not silently.
Without a budget, go through: deployment platform, security, privacy and confidentiality (nothing from a client or
employer that is not public), performance, licensing, language, accessibility. Each 🔴 turns the criterion into ⛔ and
requires an alternative.

## Phase 4 — classification and questions
**Configuration** · **Extension** · **New** · **Infeasible: redesign or escalate**. Blocking questions: at most 4,
with options and your recommendation first. Cosmetic matters are declared as assumptions with a default.

## Deliverable
1. `exploration.md` using the `templates/<flavor>/exploration.md` template from `epe-0-new`.
2. Summary in chat: criterion × coverage table, 🔴/🟡, classification, questions.
3. Next: `/epe-2-plan` once the person you work with accepts the matrix.

## Hard rules
- **Cite or stay silent**: no claim without `file:line` or URL with date.
- Do not write code or final content here. You may leave hints for the plan in §5 (hook point, one line per idea).
