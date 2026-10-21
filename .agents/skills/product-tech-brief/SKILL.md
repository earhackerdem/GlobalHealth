---
name: product-tech-brief
description: Decides "with what" and "how well" after the brief or PRD, before the first plan. Step 1 is a BLOCKING question: is there a team, and what stack, platform and budget does it already have? (if a stack exists, it wins). Otherwise proposes 2-3 candidate stacks from the PRD constraints with trade-offs, favouring boring technology. Fixes the NFR budget as measurable statements (ISO 25010 + operational), records stack choices as ADRs in memory/decisions/ and writes product/technical-brief.md, which every change's exploration inherits. Use when the user says "/product-tech-brief", "which stack", "which framework/language", "non-functional requirements", "NFRs", "technical brief".
argument-hint: [path to prd or brief; defaults to product/prd.md, else product/brief.md]
---

# /product-tech-brief — the team first, then the stack, then how well

The PRD is technology-agnostic on purpose. Spec Kit decides the stack in `plan.md` ("Technical Context"), BMAD with an
architect *"favoring boring technology, developer productivity, and trade-offs over verdicts"*. None of them asks the
one question that decides most real projects: **who is going to build and maintain this, and what do they already
use?** This skill asks it first and refuses to continue without the answer.

## Procedure
1. **Blocking question, one round, before anything else:**
   - Is there a development team (or a maintainer)? How many, what seniority?
   - What languages, frameworks, databases, hosting and CI do they use **today**? What are they fluent in?
   - Budget and deadline for infrastructure and tooling; licensing constraints; compliance (data residency, PII).
   - **Platform, explicit**: web, desktop, mobile Android/iOS, or PWA — per audience surface, naming the factor
     that decides it (where the user physically is, offline needs, camera, store distribution).
   - **Interaction mode of the heavy criteria** (read discovery's processes if they exist): photo/camera-first
     vs forms, offline capture, notifications — one question per criterion that smells like UI.
   - **Expected users and concurrency**, now and in a year. Unknown numbers get an explicit default recorded
     as an assumption (e.g. "≤100 users, single region"), never silence: the NFR budget needs a number.
   - **Local development environment**: DB in Docker or native? venv/dependency manager? what does
     "run it on my machine" take? (lesson from origin: stack and hosting decided, local env undecided → ad-hoc ADR).
   - Brownfield: is there an existing codebase this must live in or integrate with? (then run `/codebase-context` first
     if `AGENTS.md` has no `<!-- harness:context -->` block).
   Write the answers verbatim in §1. **If a stack exists, it wins**: the brief only records where the PRD strains it
   (a requirement the stack cannot meet) and the alternatives, with cost.
2. **Only without an existing stack**: derive 2-3 candidate stacks from the PRD's FR/NFR and the team's fluency. Each
   with: what it buys, what it costs, maturity and hiring pool, hosting fit, and the NFRs it meets or risks. Recommend
   one, bias to boring technology, say the second-best. Every factual claim about a technology is **[VERIFIED]** with a
   dated source or marked **[OPINION]**; no "X is faster" from memory.
3. **NFR budget**: take every NFR-### (or write them from the brief) and make them measurable: stimulus → response →
   measure, with the test that will prove each one (load test, pen test checklist, lighthouse score, backup restore
   drill, uptime SLO). Unknown numbers stay `NEEDS CLARIFICATION` with the question and a default. Categories: ISO 25010
   (performance efficiency, reliability, security, maintainability, portability, usability, compatibility, functional
   suitability) plus operational (hosting/operations, compliance/privacy, data residency, language/i18n,
   accessibility, licensing, observability, cost ceiling).
4. **Record**: `product/technical-brief.md` from `template.md`; each stack or platform choice as an ADR
   `memory/decisions/D<n>-slug.md` (`make decision-next`; decision, why, discarded alternatives); `harness.json` → `code` with the real source
   folders; `blocked_commands` if the platform has dangerous operations (deploy, drop database).
5. Tell the author what every change inherits from now on: `/epe-1-explore` §4 starts from the NFR budget; `/epe-2-plan`
   must say how each affected NFR is met; a change that needs to break the budget changes the brief **and** the ADR
   in the same PR.

## Rules
- No stack proposal before the team answer. If the author says "no team yet, I will build it", the team is the author:
  their fluency is the constraint.
- Trade-offs, not verdicts. Two sentences per option, a recommendation, and what would make you change it.
- The brief fixes decisions, not designs: diagrams and module layout belong to each change's `plan.md`.
