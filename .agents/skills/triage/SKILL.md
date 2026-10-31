---
name: triage
description: Evaluates a request BEFORE any work starts and says which rung of the calibration ladder it needs: nothing (edit and verify), a change folder (EPE), a product brief, a PRD, or codebase-context first; routes reviews, memory and retros to their skills. One message, no files, no work. The decision goes into the story it opens as a `Triage:` line. Use when the user says "/triage", "what does this need?", "is this a story or a PRD?", brings new work with no active change, or the skill-nudge hook suggests it.
argument-hint: [the request; defaults to the last user message]
---

# /triage — which rung does this request need?

The ladder lives in `AGENTS.md § Calibrate, don't ritualize`. This skill applies it to one request and writes the
verdict down, so the decision is reviewable instead of remembered. **Over-process is a defect too**: a PRD for a
typo costs as much credibility as code without a story.

## Procedure (cheap: read, decide, answer)
1. Read the request, `harness.json` (`flavor`, `code`, `tests`), whether `.epe/active` exists, whether `product/`
   exists and what it holds, and whether `AGENTS.md` has a filled `<!-- harness:context -->` block.
2. If there is an active change and the request belongs to it → **route to the phase it is in** (`make epe-status`).
   If it is a different thing, it does not get mixed in: new rung below.
3. Not new work? Route and stop: review of finished work → `/epe-4-review`; "note this", "compact", end of
   session → `/epe-memory`; "how did it go", loops, friction → `/session-retro`; a question → answer it. New work that
   the person wants taken to a reviewed PR without stopping ("don't stop", "like the last PRs") still gets its rung here,
   and then runs under `/epe-autopilot`.
4. Walk the rungs **from the bottom**; the lowest that fits wins, and you name the condition that would move it up:

| Rung | Signals | Next |
|---|---|---|
| **nothing** | typo, broken link, rename, memory entry, config value, a one-line answer; no `code` path, no decision, no gate, no chained artifacts | edit and verify; journal only if it was work |
| **change** | touches `code`, a decision, a gate or several chained artifacts; criteria can be written as Given/When/Then from the request alone; one story | `make epe-new SLUG=…` → `/epe-1-explore` |
| **brief** | several stories with one product or audience behind them and no `product/brief.md`; the request lists features, a "project", an "app", a "course", a "series" | `/product-brief` (one page), then stories |
| **PRD** | BMAD's rule: *more than one person must agree on what the product is, or more than one epic must not diverge*; stakeholders, phases, roadmap, a team | `/product-prd`, then `/product-tech-brief` if there is code |
| **codebase-context** | an existing codebase and `AGENTS.md` has no filled context block (`harness.json → code` empty, `make adopt` just ran) | `/codebase-context`, then one bounded change |

5. Development flavor, rung **change** or above: add the **Execution hint** the plan will have to confirm:
   `test→impl` if the change touches `code` and will have a test; `single` for config/docs; `parallel` never from
   triage (it needs the plan's interface contract).
6. At most **two** open questions, only if the rung depends on the answer. Otherwise assume and say so.

With `engine: openspec` the **change** rung's next command is still `make epe-new SLUG=<id>` (it runs
`openspec new change`), followed by `/opsx:propose` or `/epe-1-explore`.

## Output (exactly this, and nothing else)
```
Triage: <rung> — <one-line reason, with the signal you saw>
Next: <command or skill, copy-pasteable>
Execution hint: <single | test→impl | n/a>
Open questions: <at most two, or none>
```
If the rung is **change** or above and you then open the folder, the story's `**Triage:**` line gets
`<rung> — <reason> (YYYY-MM-DD)`.

## Rules
- You do not do the work, you do not open the folder, you do not write files. `/epe-0-new` does that after.
- Lower rung wins when two fit. "nothing" is a legitimate, frequent answer.
- Never upgrade to look thorough; never downgrade because the person is in a hurry. The reason must name a signal
  from the request or the repo, not a feeling.
- One message. If you need more than four lines, the request needs `/epe-1-explore`, not more triage.
