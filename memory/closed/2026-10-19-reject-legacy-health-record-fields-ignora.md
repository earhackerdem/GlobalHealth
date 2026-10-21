---
date: 2026-10-19
state: frozen
anchor: journal: 2026-10-19 · receta-mexicana (apply)
---

`reject_legacy_health_record_fields` ignora campos retirados con null explícito (`{"dose": null}` pasa sin 422, models.py `v is not None`)

**Verdict and why:** Decisión de Saúl Pérez: se queda así — convención JSON null=ausente, documentada en el código; solo afectaría clientes externos y la app está en desarrollo

**State:** 🔒 frozen

**Anchor (journal: date · title):** journal: 2026-10-19 · receta-mexicana (apply)
