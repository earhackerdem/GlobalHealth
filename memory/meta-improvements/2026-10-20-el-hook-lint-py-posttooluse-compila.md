---
date: 2026-10-20
status: applied
---

[2026-10-20 · Proposed] El hook `lint.py` (PostToolUse) compila con el `python3` del sistema (3.9 en macOS) y marca
como error de sintaxis el `except A, B:` sin paréntesis (PEP 758), que `ruff format` produce con Python 3.14
(`backend/app/api/routes/profile.py`, `deps.py`). Es un falso positivo que se ignora en cada edición. Propuesta
upstream: que `lint.py` use el intérprete del proyecto cuando exista (`uv run python`, `.venv/bin/python`) o
`harness.json → python`. Visto en perfil-eventos; queda en el inbox del template.

[2026-10-26 · Recurrencia] Volvió a bloquear a un `implementer` en perfil-habitos-actividad-sueno al editar
`routes/profile.py` (línea 222, ajena al cambio): el agente tuvo que diagnosticarlo como falso positivo para seguir.
Sigue sin aceptarse ni subir al template; candidato a decidir con Saúl Pérez antes de la próxima historia (harness
first).

**Where it lives:** earhackerdem/harness#6 (C-12, 0.4.1), `.claude/hooks/lint.py:29` (`project_python`). Verificado el 2026-10-31 en la actualización a 0.4.5: el hook encuentra `.venv/bin/python` (3.14.7) en la raíz y `backend/app/api/routes/profile.py:224` ya no da «py_compile FAILED» (el `python3` del sistema, 3.9.6, sí falla).
