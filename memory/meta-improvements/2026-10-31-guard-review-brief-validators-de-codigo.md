---
date: 2026-10-31
status: proposed
---
`guard-review-brief.py` toma por subagente de revisión a un `implementer` cuyo prompt dice «validators» en el sentido de código (funciones validadoras de pydantic/Python)

**Why:** la regex `REVIEW` (`.claude/hooks/guard-review-brief.py:18`) incluye `\bvalidators?\b`. El 2026-10-31, en
validaciones-hoy-y-texto-invisible, bloqueó el brief de un `implementer` que decía «as the other validators there do»
(los validadores de `routes/profile.py`). Hizo falta relanzarlo con `NO-CLOSED:`. Propuesta upstream: no exigir el
índice cuando el `subagent_type` es `tester` o `implementer` (roles que el harness ya conoce, `guard-tests.py`), o
exigir que «validator» aparezca junto a una palabra de revisión.
**Where it lives:** template `earhackerdem/harness`, una rama `improve/` (vuelve con `make harness-update`)
