---
date: 2026-10-20
status: proposed
---

[2026-10-20 · Proposed] El hook `lint.py` (PostToolUse) compila con el `python3` del sistema (3.9 en macOS) y marca
como error de sintaxis el `except A, B:` sin paréntesis (PEP 758), que `ruff format` produce con Python 3.14
(`backend/app/api/routes/profile.py`, `deps.py`). Es un falso positivo que se ignora en cada edición. Propuesta
upstream: que `lint.py` use el intérprete del proyecto cuando exista (`uv run python`, `.venv/bin/python`) o
`harness.json → python`. Visto en perfil-eventos; queda en el inbox del template.
