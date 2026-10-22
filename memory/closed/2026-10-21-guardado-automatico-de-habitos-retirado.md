---
date: 2026-10-21
state: frozen
anchor: journal: 2026-10-21 · perfil-habitos-ajustes (C-10…C-14)
---
A2, A4, A5, A6, A7, A8, A9, T2 y T4 (ronda 1 de perfil-habitos-ajustes, PR #32): defectos del guardado automático de hábitos (cuenta cruzada con otra pestaña, formulario viejo al reabrir, número sin salir del campo perdido o guardado a medias, 401/403 fuera de `handleApiError`, estado engañoso, fila de botones que salta, garantías de la cola sin prueba, "nada se guarda" falso con una pausa)

**Verdict and why:** Confirmados por reproducción, y sin objeto: Saúl Pérez decidió el 2026-10-21 quitar el guardado automático (design.md Decision 8): se guarda con "Guardar" por `useMutation` y la pantalla avisa antes de salir con cambios sin guardar. Para A5 el diseño nuevo además suprime los avisos de salida cuando el token cambió, para que nadie pueda quedarse y guardar con la sesión de otra cuenta. Solo se reabre si vuelve el guardado automático, en esta pantalla o en otra

**State:** 🔒 frozen

**Anchor (journal: date · title):** journal: 2026-10-21 · perfil-habitos-ajustes (C-10…C-14)
