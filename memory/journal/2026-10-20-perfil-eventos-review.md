# 2026-10-20 · perfil-eventos: review adversarial (PR #20)

**Quién:** Saúl Pérez (author) invocó `/epe-4-review` en la misma sesión que ejecutó el cambio.
Para compensar que el autor revisara su propia obra:
- finders y validadores fueron agentes independientes, sin las justificaciones del autor;
- `closed.md` viajó en cada prompt.

**Qué:** 1 ronda.
- **Finders:** 5 lentes (casa, seguridad, criterios, restricciones, tests) → 38 hallazgos únicos + 2 de la
  exploración del autor.
- **Validación:** 3 validadores (backend, frontend, tests/docs) reprodujeron con probes HTTP, mutantes,
  Playwright contra la build y relojes en otras zonas horarias.
- **Resultado:** 1 alto, 6 medios, ~28 bajos, 3 dudosos, 4 fuera de alcance, 3 falsos positivos.
- **El alto (T1):** el e2e de mediciones (`profile.spec.ts:83-87,396`) calcula "hoy" con el reloj del runner
  (UTC en el contenedor de CI) y falla de 00:00 a 06:00 UTC. Es el gemelo del defecto que la tarea 1.0
  arregló solo en el backend.
- **Errores propios en `evidence.md` (C10a/b):** afirmaba "ningún fallo en specs del cambio" sobre 2 fallos no
  identificados, y omitía el CI verde del PR.
- **PR:** comentarios finder y validator publicados con marcador.

**Gate (Saúl Pérez):**
- **Aprueba:** bloques 1–5 (T1 y huecos de tests, accesibilidad A1/A2/A3/B3, textos F11/E1/F6/H1/H2 y año
  aproximado futuro, evidence/validation, endurecer backend C9/S5/T2/S4/H6/H7), más E2 (cambiar "El médico
  verá…"), O1 (distinguir tarjetas) y O2 (grupo sanguíneo hablado).
- **No aprueba:** bloque 6 (diferibles) ni bloque 7 (deuda fuera del cambio). Quedan en `closed.md`: 6 filas ⏸️
  y 1 🔒 de falsos positivos.

**Siguiente:** `/epe-5-apply`.
