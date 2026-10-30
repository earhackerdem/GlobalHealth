---
date: 2026-10-29
status: proposed
---

El hook `lint.py` compila el Python con el intérprete del sistema, no con el del proyecto

**Qué pasa:** `.claude/hooks/lint.py:34` corre `sys.executable -m py_compile`. El hook se lanza con
`#!/usr/bin/env python3`, que en este Mac es Python 3.9.6. El backend pide `>=3.14` (`backend/pyproject.toml:5`) y
usa la sintaxis de PEP 758 (`except json.JSONDecodeError, ValidationError:` en
`backend/app/api/routes/profile.py:224`). Por eso cada edición de ese archivo da un falso «py_compile FAILED». Lo
reportó el implementer del cambio `perfil-trabajo` el 2026-10-29. El orquestador verificó la versión y la línea.

**Propuesta:** que el hook compile con el intérprete del proyecto cuando exista uno. Por ejemplo `uv run python`
dentro del directorio que tenga `pyproject.toml` con `requires-python`, o el `.venv` del proyecto, y si no, como hoy.
Una alarma falsa en cada edición enseña a ignorar el hook.

**Dónde va:** upstream, en el template del harness (`~/projects/personal/harness`, rama `improve/`), y vuelve con
`make harness-update`. No se edita en el proyecto: `.claude/hooks/` es vendorizado.

**Estado:** propuesto. Según AGENTS.md («Harness first»), va antes de la siguiente historia de producto. Lo decide
Saúl Pérez.
