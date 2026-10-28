---
date: 2026-10-26
state: deferred
anchor: journal: 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)
---
B2 de perfil-habitos-actividad-sueno (PR #34, ronda 1), instancia anterior: "¿Cuál fue?" con "Otra" del historial (`other_text`) acepta un texto invisible (`"​"`, `"ㅤ⠀"`) como contestado, porque `_is_filled` (`backend/app/models.py`, `.strip()`) y `HistoryEntryForm.tsx` (`.trim()`) no quitan caracteres de formato ni rellenos en blanco

**Verdict and why:** Confirmado por reproducción (`POST /profile/history` con `other_text: "​"` → 201, validador de backend, 2026-10-26). En este PR se arregla solo el nombre de "Otra" del ejercicio, campo nuevo; Saúl Pérez aprobó dejar el del historial como deuda (2026-10-26). Se paga con el mismo criterio (vacío tras quitar Cf, Zs, U+3164 y U+2800) en backend y pantalla, idealmente compartido con el del ejercicio

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)
