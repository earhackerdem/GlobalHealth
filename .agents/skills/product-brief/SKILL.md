---
name: product-brief
description: First artefact of the optional product layer. Writes product/brief.md in one page (problem, audience, outcomes, constraints, out of scope, open questions) through a short interview, and tells the author whether a PRD is worth it (only if more than one person must agree on the product or more than one epic must not diverge). Use when the user says "/product-brief", "let's define the product", "write the brief", "I have an idea for a project", or starts a greenfield project with no product/ folder.
argument-hint: [one-line idea, or path to notes]
---

# /product-brief — one page before the first story

The EPE cycle starts at `story.md`. For a one-story project that is enough. When there is a product behind the stories,
the brief fixes intent once so stories carry an `Origin:` and nobody re-litigates the "why". It is **optional** and it
is **one page**: if it grows, you need a PRD, not a longer brief.

## Procedure
1. Read `memory/decisions.md` and `memory/research.md` if they exist (do not contradict them). If `product/brief.md`
   exists, you are updating it: say what changes.
2. **Interview in one round** (ask only what the notes don't answer): the problem and who has it today; who the user
   is and what they can do after; what "done" looks like in 3-5 measurable outcomes; hard constraints (deadline, budget,
   platform, compliance, language); what is explicitly out of scope.
3. Write `product/brief.md` from `template.md` (create `product/` with `make product-init` if missing). Every claim about
   users or market is **[VERIFIED]** with a source or marked **[ASSUMPTION]**; the harness is a skeptical partner, not
   a note-taker.
4. **Decide the next step, and say it**: apply the rule *"you need a PRD when more than one person must agree on what
   the product is, or more than one epic must not diverge; otherwise skip it"* (BMAD). If skipped, go to
   `/product-tech-brief` (stack and NFR budget) or straight to `make epe-new SLUG=…` with `Origin: product/brief.md`.
5. Journal entry; if the brief fixes a durable decision (target platform, excluded segment), record it as an ADR.

## Rules
- One page. Bullet points over prose. No technology in the brief: that is `/product-tech-brief`'s job.
- Outcomes are measurable or they are wishes. "Users like it" is not an outcome; "80% of invited users complete the
  first task without help" is.
- The brief is not a gate: no hook reads it. Its value is traceability (`Origin:` lines) and not repeating the interview.
