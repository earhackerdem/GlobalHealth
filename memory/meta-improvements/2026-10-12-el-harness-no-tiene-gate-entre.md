---
date: 2026-10-12
status: applied
---

[2026-10-12 · ✅ Applied 0.2.0: `make install-hooks`, verificado 2026-10-20 en el Makefile] El harness no tiene gate entre "commit verde local" y "push": tres fallos de pre-commit en CI
(PR #2 de GlobalHealth) fueron pushes sin pasada prek local. Propuesta: make install-hooks que instale un pre-push
corriendo prek sobre el diff vs la rama base (hoy instalado ad-hoc en .git/hooks/pre-push de este repo).
