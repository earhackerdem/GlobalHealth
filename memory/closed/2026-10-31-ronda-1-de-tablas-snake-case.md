---
date: 2026-10-31
state: frozen
anchor: journal: 2026-10-31 · tablas-snake-case: las cinco tablas del default de SQLModel en snake_case (D25)
---
Ronda 1 de tablas-snake-case (PR #49): F7 se congela; F1–F6 se corrigieron en el PR

**Verdict and why:** gate por delegación de Saúl Pérez (author), 2026-10-31. **F7:** `alembic upgrade --sql`, sin
conexión, falla en `c4a9e1d7b2f5`, porque la migración lee el catálogo para renombrar lo que exista. Ya era así en
`a7f3c9e21d54`, que también usa `op.get_bind()`, y ninguna receta, CI ni documento usa `--sql`. Si algún día se
necesita SQL sin conexión, se revisa con esa necesidad delante.

**State:** 🔒 frozen

**Anchor (journal: date · title):** journal: 2026-10-31 · tablas-snake-case: las cinco tablas del default de SQLModel en snake_case (D25)
