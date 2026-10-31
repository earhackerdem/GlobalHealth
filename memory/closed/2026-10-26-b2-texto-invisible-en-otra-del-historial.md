---
date: 2026-10-26
state: frozen
anchor: journal: 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)
---
B2 de perfil-habitos-actividad-sueno (PR #34, ronda 1), instancia anterior: "¿Cuál fue?" con "Otra" del historial (`other_text`) acepta un texto invisible (`"​"`, `"ㅤ⠀"`) como contestado, porque `_is_filled` (`backend/app/models.py`, `.strip()`) y `HistoryEntryForm.tsx` (`.trim()`) no quitan caracteres de formato ni rellenos en blanco

**Verdict and why:** Confirmado por reproducción (`POST /profile/history` con `other_text: "​"` → 201, validador de backend, 2026-10-26). En este PR se arregla solo el nombre de "Otra" del ejercicio, campo nuevo; Saúl Pérez aprobó dejar el del historial como deuda (2026-10-26). Se paga con el mismo criterio (vacío tras quitar Cf, Zs, U+3164 y U+2800) en backend y pantalla, idealmente compartido con el del ejercicio

**State:** 🔒 frozen (pagado)

**Anchor (journal: date · title):** journal: 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)

**Pagado (2026-10-31):** validaciones-hoy-y-texto-invisible, PR #47. `_is_filled` usa `_is_blank` (`backend/app/models.py`) y la pantalla del historial usa `isBlank` (`frontend/src/components/Profile/text.ts`), compartido con hábitos; también la caja de «cuándo». No se vuelve a reportar.
