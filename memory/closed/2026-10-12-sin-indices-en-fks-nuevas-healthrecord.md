---
date: 2026-10-12
state: frozen
anchor: journal: 2026-10-12 · expediente-registros (review)
---

Sin índices en FKs nuevas (healthrecord.owner_id, healthrecordattachment.record_id): seq scan por listado

**Verdict and why:** Paridad con el template (item.owner_id tampoco); irrelevante a la escala actual; añadirlos cuando el volumen lo pida

**State:** 🔒 frozen (pagado)

**Anchor (journal: date · title):** journal: 2026-10-12 · expediente-registros (review)

**Pagado (2026-10-31):** bd-candados-indices-y-log, PR #48. La migración `26de7399b12f` indexa las 9 llaves foráneas que no tenían índice, y `test_every_foreign_key_has_an_index` vigila el catálogo.
