---
date: 2026-10-19
status: open
---

[2026-10-19] Las suites e2e heredadas del template (login, user-settings, admin) NO pasan en viewport móvil
384×832 (timeouts/elementos no visibles — visto en CI del PR #13 cuando el proyecto s26-ultra corrió sin
testMatch). El proyecto quedó acotado a health-records.spec.ts; extender la cobertura móvil al resto de la UI
(y arreglar esas pantallas en 384px) es trabajo propio, probablemente junto con la primera pasada responsive
general.
