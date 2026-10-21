---
date: 2026-10-20
state: deferred
anchor: journal: 2026-10-20 · perfil-eventos (review)
---

B1/B2/O3 de perfil-eventos: tres `useSuspenseQuery` en serie en `/perfil`; editar invalida `["profile"]` sin necesidad; el fallback de carga de la ruta nueva es la tabla de items

**Verdict and why:** Rendimiento/pulido menor, sin presupuesto de latencia en el technical-brief; 2 de las 3 consultas en serie y el fallback venían de main

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-eventos (review)
