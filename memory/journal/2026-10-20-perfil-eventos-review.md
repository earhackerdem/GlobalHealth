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

**Siguiente:** `/epe-5-apply` (hecho, ver Apply abajo).

**Apply (2026-10-20):**
- **Fixers:** dos, con archivos disjuntos, con la orden de no descartar nada.
  - **Backend:** 6/6 aplicados (S4, H6, H7, C9, S5, T2).
  - **Frontend:** 18 aplicados (T1, C2, C3, C7, C8, A1, A2+C5, A3, B3, H1, H2, año futuro, F11, F6, E1, E2,
    O1, O2), con 1 rebote parcial: `aria-required` en `role="group"` es inválido en ARIA 1.2.
- **Orquestador:** aplicó C1 y C10a/b/c (evidence y validation).
- **Re-corrido desde limpio:** backend 195 passed, cobertura 96 %; mutantes 7/7 muertos; e2e del cambio 49
  passed en los dos proyectos; T1 verde con Node en Kiritimati. La suite completa como CI salió 145 passed en una
  de dos corridas; en la otra cayeron 2 heredados del template, que solos pasan 101/101.
- **Para Saúl:** las notas S4, C5 y O2 están en `evidence.md` § Apply. La meta-mejora del hook `lint.py` (Python
  del sistema contra PEP 758) queda como candidata.

**Exploración en Chrome tras el apply (2026-10-20).** Saúl Pérez notó que no la había corrido después del apply y
fijó el orden: primero explora el agente y, si no hay defectos, valida él; si los hay, el agente rehace o se
detiene si hace falta criterio humano. Saúl ya había validado a mano. Corrí la exploración: todos los hallazgos
del apply se comportan como se aprobaron, y la exploración no encontró defectos. Dos observaciones, sin deuda
nueva: el error de un campo se queda hasta reenviar (síntoma de H5, diferido) y tres `click()` programáticos
duplican (el doble clic real no). Detalle en `evidence.md` § Exploración en Chrome tras el apply. De paso, Saúl
vio tablas sin `_` en la BD (default de SQLModel); queda en el inbox para decidir con un ADR.
