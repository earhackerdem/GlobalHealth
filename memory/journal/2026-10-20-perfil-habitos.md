# 2026-10-20 · perfil-habitos (Story C1: sustancias y humo)

**Quién:** Saúl Pérez (author) con el agente (orquestador), con tester e implementer por grupo.

## Intención
Llenar la tarjeta "Hábitos" (FR-028). En la exploración Saúl Pérez partió la Story C en dos ("1. Dos") y aceptó
las recomendaciones: el servidor descarta lo que no aplica y las edades imposibles se rechazan junto a su campo.
Esta es la C1: alcohol con el AUDIT-C, tabaco y vapeador, humo ajeno y humo de leña, sin puntajes (C-6).

## Qué se hizo
- `patient_profile.habits` cifrado (migración `7d3e9a1c5b42`), `GET/PUT /profile/habits` con normalización y
  errores 422 con `loc` (para no enrutar por el texto, hallazgo R20 de la Story B).
- Pantalla `/perfil/habitos`, `ChipMultiGroup` (chips de selección múltiple con opción excluyente, D18) y la
  tarjeta enlazada con "Sin llenar" / "Con datos".
- El gate pidió la frase literal: Saúl Pérez escribió "procece" y después "plan approved".

## Verificación
Backend 289 passed (cobertura 96 %), grupo 2 101 passed (chromium + s26-ultra), suite Playwright completa 203
passed en 2 de 3 corridas (la otra, el flake heredado de `login.spec.ts:87`). Exploración en Chrome sin defectos.
Números en `openspec/changes/perfil-habitos/evidence.md`.

## Sorpresas
- `localhost:8000` resuelve a `::1`, donde contesta el contenedor; el `fastapi dev` ajeno (PID 1076) solo escucha en
  `127.0.0.1`. Con la imagen vieja, el navegador no veía las rutas nuevas y `make migrate` no migraba. Se reconstruyó
  la imagen.
- La ventana de Chrome de la sesión anterior quedó en 114 px y no aceptaba cambios de tamaño; una pestaña nueva sí.

## Deuda
Ver evidence.md § Deuda.
