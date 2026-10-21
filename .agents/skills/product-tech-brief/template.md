# Technical brief — <product>

Date: YYYY-MM-DD · Author: <name (role)> · Status: draft | agreed · Source: product/prd.md | product/brief.md

## 1. Team and existing stack (answered first, verbatim)
| Question | Answer |
|---|---|
| Team (size, seniority, maintainer) | |
| Languages / frameworks in use today | |
| Databases / hosting / CI in use today | |
| Fluency and preferences | |
| Budget, deadline, licensing, compliance | |
| Existing codebase to live in or integrate with | <none · path/repo; `/codebase-context` run on YYYY-MM-DD> |
| Platform per surface (web / desktop / Android / iOS / PWA) and the deciding factor | |
| Interaction mode of the heavy criteria (photo-first, offline, camera, notifications) | |
| Expected users / concurrency (now · in 1 year; defaults recorded as assumptions) | |
| Local development environment (DB in Docker? deps manager? one-command run?) | |

**Verdict:** <existing stack wins · no stack: candidates below>

## 2. Where the requirements strain the existing stack (if any)
| Requirement | Strain | Options (cost) | Decision |
|---|---|---|---|

## 3. Candidate stacks (only without an existing stack)
| Option | Buys | Costs | Maturity / hiring | Hosting fit | NFRs met / at risk | Sources |
|---|---|---|---|---|---|---|
| A (recommended) | | | | | | |
| B | | | | | | |

**Recommendation and what would change it:** …

## 4. NFR budget (every change inherits this)
| ID | Attribute | Stimulus → response → measure | Proof (test) | Status |
|---|---|---|---|---|
| NFR-001 | performance efficiency | | | agreed · NEEDS CLARIFICATION |
| NFR-002 | reliability (backup, RPO/RTO, uptime) | | | |
| NFR-003 | security (authn/z, secrets, dependencies) | | | |
| NFR-004 | maintainability (tests, lint, docs) | | | |
| NFR-005 | portability / hosting | | | |
| NFR-006 | usability / accessibility | | | |
| NFR-007 | compliance / privacy / data residency | | | |
| NFR-008 | language / i18n | | | |
| NFR-009 | observability | | | |
| NFR-010 | cost ceiling | | | |

## 5. Decisions recorded
| ADR | Decision | File |
|---|---|---|
| D<n> | <stack / platform / database> | memory/decisions/D<n>-slug.md |

## 6. Consequences for the harness
- `harness.json` → `code`: <folders> · `blocked_commands`: <deploy, drop db…> · skills to add: <stack skills>
