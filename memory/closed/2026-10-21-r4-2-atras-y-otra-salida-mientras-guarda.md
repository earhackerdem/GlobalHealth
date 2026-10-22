---
date: 2026-10-21
state: deferred
anchor: journal: 2026-10-21 · perfil-habitos-ajustes (C-10…C-14)
---
R4-2 (ronda 4 de perfil-habitos-ajustes): en hábitos, atrás del navegador mientras guarda y luego otra salida dentro de la app ("‹ Mi perfil médico") reemplaza la salida retenida; la primera nunca se resuelve: si el guardado falla, la URL queda en `/perfil` con el formulario a la vista y el historial salta una entrada

**Verdict and why:** Confirmado por reproducción (10/10). Diferido por Saúl Pérez: camino raro, sin pérdida de datos, y arreglarlo pide manejar dos bloqueos a la vez de TanStack Router. Declarado en `openspec/changes/perfil-habitos-ajustes/evidence.md` § Deuda. Se reabre si aparece en otra pantalla con salida retenida o si TanStack Router cambia cómo encadena bloqueos

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-21 · perfil-habitos-ajustes (C-10…C-14)
