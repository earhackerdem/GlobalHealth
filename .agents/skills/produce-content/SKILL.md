---
name: produce-content
description: Content production core (posts, lessons, scripts, articles, documentation) for content-flavor projects. Skeptical stance, dated primary sources, [VERIFIED] vs [OPINION/HYPE], the record rules (memory/research/), citer inventory, confidentiality boundary, house style (content/STYLE.md) and a cold-reader pass. Loaded by /epe-1-explore and /epe-3-execute. Use when the user wants to write, edit or review a post, lesson, script, article or any piece for an audience.
---

# /produce-content — rules, one line each

| # | Rule |
|---|---|
| a | **Every request is a hypothesis to verify**: list the assumptions and key terms and mark which are unverified before writing. |
| b | **Dated primary sources** (official docs, repos, authors), not secondary blogs. Empirical before documentary if the tool is at hand. |
| c | Separate **[VERIFIED]** (source + date) from **[OPINION/HYPE]**. Hype may come in, labeled and grounded: *what it really is → where it is practiced*. |
| d | **The record rules**: a figure recorded in `memory/research/` is cited with **the same authority the record gives it**, never more. Adding a survey, window or baseline the record does not have is a defect no gate sees. |
| e | **Two records of the same datum that disagree are a defect** before writing anything. The more conservative one rules until you go back to the source. A load-bearing figure is re-verified even if recorded. |
| f | **Citer inventory** before changing an example, datum, name or thesis: other pieces, tables, diagrams (text inside a PNG is only visible by opening it), `memory/`. Everything that cites it expires in the same commit, and the list is re-run **at close**. |
| g | **Confidentiality boundary**: nothing from a client, employer or student that is not public. Your own experience and lessons, yes; others' material, names and data, no. If in doubt, declare it as a blocking question. |
| h | **House style** in the project's `content/STYLE.md` (voice, language, length, what is forbidden). If it does not exist, the first change writes it and the person you work with approves it. |
| i | **Self-contained scenarios**: each piece defines what it needs where it needs it; it does not depend on the reader having read another. |
| j | **Cold reader at close**: run each section through the `cold-reader` agent. Its stumbles are hypotheses you verify; `NO STUMBLES` is frequent. |
| k | **A contrast that does not discriminate does not verify**: pick the case where the hypotheses would give different results. |
| l | **Record-keeping**, one file per record: decisions to `memory/decisions/`, facts to `memory/research/`, work to `memory/journal/`. |

## Definition of Done for a piece
- [ ] Assumptions listed and verified (a-c); sources with URL and date.
- [ ] Figures and quotes with their record's authority (d-e); record updated if re-verified.
- [ ] Citer inventory done at start and re-run at close (f).
- [ ] Nothing confidential (g); house style (h); self-contained (i).
- [ ] Cold reader run and stumbles resolved or declared (j).
- [ ] The change's `evidence.md` and `validation.md` written; journal entry.

Explore/Plan/Execute and the PR flow live in `AGENTS.md` and the `epe-*` skills; here only what is specific to
producing content.
