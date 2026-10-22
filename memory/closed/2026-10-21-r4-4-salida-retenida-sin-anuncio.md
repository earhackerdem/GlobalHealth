---
date: 2026-10-21
state: frozen
anchor: journal: 2026-10-21 · perfil-habitos-ajustes (C-10…C-14)
---
R4-4 (ronda 4 de perfil-habitos-ajustes): en hábitos, una salida retenida mientras guarda no se anuncia a un lector de pantalla (no hay texto en vivo durante la espera)

**Verdict and why:** Dudoso para el validador: no rompe el contrato (design.md pide la espera "sin diálogo"; D20 pide mostrar que se envía, y "Guardando…" lo hace; R2-5 ya se resolvió así) y el resultado sí se anuncia (el aviso de sonner en `aria-live` o el foco al campo con el error). Saúl Pérez aprobó no aplicarlo. Se reabre con una prueba con lector de pantalla que muestre a alguien perdido en la espera

**State:** 🔒 frozen

**Anchor (journal: date · title):** journal: 2026-10-21 · perfil-habitos-ajustes (C-10…C-14)
