---
name: product-prd
description: Writes product/prd.md only when coordination needs it (more than one person must agree on the product, or more than one epic must not diverge). Technology-agnostic: functional requirements FR-###, non-functional requirements NFR-### by quality attribute with MoSCoW priority, epics with their stories as one-liners, and a traceability table. Splits an epic into change folders with make epe-new … STORY=. Use when the user says "/product-prd", "write the PRD", "we need to agree on the product", "several epics", or the brief said a PRD is needed.
argument-hint: [path to brief; defaults to product/brief.md]
---

# /product-prd — agree on the product once, then split it

A PRD is a coordination document, not a ritual. Spec Kit and Kiro don't have one; BMAD makes it optional and sized to
the need. Here it exists for one reason: when several people or several epics must not diverge. **If the brief's
"next step" says no PRD, do not write one.**

## Procedure
1. Read `product/brief.md` (or send to `/product-brief`), `memory/decisions.md`, `memory/research.md`.
2. **Stay technology-agnostic.** The PRD says what the system must do and how well, never with what. If a requirement
   smuggles a technology ("with WebSockets", "in Postgres"), rewrite it as the behaviour it wants and leave a note for
   `/product-tech-brief`.
3. Write `product/prd.md` from `template.md`:
   - **FR-###**: one observable behaviour each, with the user and the trigger. No "and".
   - **NFR-###**: by quality attribute (ISO 25010: performance efficiency, reliability, security, maintainability,
     portability, usability, compatibility, functional suitability) plus operational (hosting, compliance and privacy,
     data residency, language, accessibility, licensing). Each **measurable**: stimulus → response → measure. Unknown
     numbers are written as `NEEDS CLARIFICATION`, never invented. `/product-tech-brief` turns them into the budget.
   - **MoSCoW** on every FR/NFR.
   - **Epics**: an outcome each, with its stories as one-liners ("As a <role>, I want …, so that …") and the FR/NFR
     they cover. Traceability table outcome → epic → FR/NFR.
4. **Split**: for each story the team starts, `make epe-new SLUG=<id-slug> STORY=<file>` or write the story from the
   flavor template with `Origin: product/prd.md § epic N`. One story per change folder. Acceptance criteria are written
   at the story, not in the PRD (the PRD has requirements; the story has Given/When/Then).
5. Journal entry; durable product decisions as ADRs. Hand off to `/product-tech-brief` before the first `/epe-2-plan`.

## Rules
- Declarative requirements (the rule), not scenarios (the example): scenarios live in each change's exploration/plan.
- Every FR/NFR has an id; stories and later `exploration.md` cite them. Renumbering is a change, not a tidy-up.
- When the PRD and a story disagree, the story is wrong or the PRD is stale; fix the one that lies, in the same PR.
