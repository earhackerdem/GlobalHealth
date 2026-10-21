---
date: 2026-10-20
state: deferred
anchor: journal: 2026-10-20 · perfil-cronicas (review)
---

Deuda de perfil-cronicas: R2 (`unlink_diagnosis` se salta una fila ilegible sin `logger.warning`; comentario inexacto) · R8 ("¿Cuál?"/ChipGroup no expone obligatorio y el foco al error cae en un chip sin `aria-invalid`, heredado de la Story A) · R9a (selector de diagnósticos con `limit=1000` sin `staleTime`, N+1 de medicinas) · R10 (tratamiento de 2000 caracteres completo en el resumen) · R20 (errores del servidor enrutados por texto es-MX; el 422 de diagnóstico ajeno no tiene e2e) · R21 (`title ?? occurred_on` inalcanzable) · R22 (B-5 asertado por API, no en lo guardado) · R23 (`until` con estado no resuelto se descarta sin validar ni probar)

**Verdict and why:** Confirmados por los validadores; sin efecto visible o heredados, y sin presupuesto de latencia (precedentes ⏸️ B1/B2/O3 y H6-H10). Aceptados como deuda por Saúl Pérez

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-cronicas (review)
