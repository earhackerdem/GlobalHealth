---
date: 2026-10-11
state: frozen
anchor: journal: 2026-10-11 · cuenta-consentimiento (review)
---

"SyntaxError en deps.py/tests (except A, B sin paréntesis): la API no arranca"

**Verdict and why:** Falso positivo reproducido: es PEP 758, legal en el Python 3.14 del proyecto (pyproject, .python-version, Dockerfile, CI); 73/73 verdes en ese head. Residual real ya aplicado: paréntesis restaurados para el hook lint.py (python del sistema)

**State:** 🔒 frozen

**Anchor (journal: date · title):** journal: 2026-10-11 · cuenta-consentimiento (review)
