# PRD — <product>

Date: YYYY-MM-DD · Author: <name (role)> · Status: draft | agreed by <names> on YYYY-MM-DD · Brief: product/brief.md

## 1. Context and goals
<Two paragraphs from the brief: problem, audience, outcomes O1…On.>

## 2. Functional requirements
| ID | As a … | The system shall … (observable) | Priority (M/S/C/W) | Outcome |
|---|---|---|---|---|
| FR-001 | | | M | O1 |

## 3. Non-functional requirements (measurable; unknown → NEEDS CLARIFICATION)
| ID | Attribute | Stimulus → response → measure | Priority | Source |
|---|---|---|---|---|
| NFR-001 | performance efficiency | <100 concurrent users browsing → page renders → p95 < 500 ms> | M | |
| NFR-002 | security | | M | |
| NFR-003 | compliance / privacy | | | |
| NFR-004 | hosting / operations | | | |
| NFR-005 | language / accessibility | | | |

Attributes: performance efficiency · reliability · security · maintainability · portability · usability · compatibility ·
functional suitability · hosting/operations · compliance/privacy · data residency · language · accessibility · licensing.

## 4. Epics
### E1 — <outcome>
Covers: FR-…, NFR-… · Stories:
- US-01 As a <role>, I want <capability>, so that <benefit>.
- US-02 …

### E2 — …

## 5. Traceability
| Outcome | Epic | FR | NFR |
|---|---|---|---|

## 6. Out of scope and open questions
- Out: …
- Q1 … (options, recommendation)

## 7. Technology notes for the technical brief (not decisions)
- <"FR-007 implies real-time updates"; "NFR-003 implies EU data residency">
