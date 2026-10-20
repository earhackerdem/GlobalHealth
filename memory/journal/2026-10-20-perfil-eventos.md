# 2026-10-20 · perfil-eventos (Story A de FR-028): apertura y exploración

**Quién:** Saúl Pérez (author) pidió "procede con la story a" sobre el prototipo v4. El gate del discovery se
cerró para la Story A y se abrió el PR #18.

**Qué:** se abrió `openspec/changes/perfil-eventos/` con los criterios A-1…A-9 del prototipo en el proposal. La
rama sale de la del discovery y se rebasa sobre `main` antes del PR. Exploración:
- **Clasificación:** extensión de `records/patient-profile`.
- **Ya existe:** el cifrado, el consentimiento, el aislamiento con 404 idéntico y el patrón catálogo + "otra".
- **Es nuevo:** el estado "ninguna", "cuándo" por edad/etapa/año y los cuatro formularios.
- **Se rompe a propósito:** `frontend/tests/profile.spec.ts:280-300`, que asierta las secciones sin captura.
- **Dependencia:** el archive necesita el PR #17.
- **Preguntas al gate:** modelo genérico o tipado, qué va en claro, pantalla o diálogo, y los dos tropiezos del
  inbox (Alembic y el reformateo de tests).

**Gate de la exploración y plan:** Saúl Pérez aceptó la matriz eligiendo las 4 recomendaciones:
- tabla genérica;
- nada en claro;
- una pantalla por sección;
- un PR `fix/` antes (PR #19).

Con eso quedó el plan en DRAFT: spec delta (1 MODIFIED + 5 ADDED, 23 scenarios), design con el Interface contract
y los citers (`profile.spec.ts:14,52,280-300`, `perfil.tsx:148`, `profile.json:79`) y tasks en grupos 0 (rebase),
1 (backend, test→impl), 2 (frontend, test→impl) y 3 (cierre). `openspec validate --strict` limpio.

**Defecto encontrado al preparar los merges:** el `test-backend` del PR #17 (solo docs) falló en
`test_profile.py:259` con `'2026-10-19' == '2026-10-20'`. El test usa `date.today()` en UTC, mientras el servidor
fecha en America/Mexico_City (`profile.py:204`). Falla cada día de 00:00 a 06:00 UTC, no en una ventana de
milisegundos como suponía la fila diferida de closed.md (2026-10-19). Se relanzó el job fuera de la ventana y el
arreglo entra como tarea 1.0 de esta story.

**Ejecución (Saúl Pérez: "plan approved", con #17, #18 y #19 mergeados):**
- **0.1:** rebase sobre `main` (quedaron solo los commits del cambio). El MODIFIED tuvo que conservar el
  scenario base "Secciones listadas sin captura", redefinido; ahora son 24 scenarios.
- **1.0:** el test de mediciones usaba la fecha local del runner. Rojo reproducido con TZ=Asia/Tokyo; verde en
  Tokio, UTC y México. closed.md reabre el flake con evidencia.
- **Grupo 1, backend (test→impl):** tester 22 rojos (90af786); implementer verde al primer intento. Suite
  completa 190 passed, 0 failed, 0 skipped, cobertura 96 %, mypy limpio, tdd-check ✓.
- **Grupo 2, frontend (test→impl):** tester 17 rojos / 6 verdes (6c7dfca), incluido el citer de
  profile.spec. El implementer agotó sus turnos ya en verde; el orquestador re-corrió: 23 passed en chromium,
  tsc y biome limpios, tdd-check ✓. Estabilidad: 221/221 con `--repeat-each=5` en ambos proyectos.
- **Suite Playwright completa como CI:** 4 de 6 corridas limpias; las caídas (`reset-password`, de Mailpit, y 2
  no identificadas) quedan ajenas a los specs del cambio y declaradas como deuda.
- **Exploración en Chrome:** sin defectos funcionales. Dos hallazgos de texto para el review: "Listo" duplicado
  en el aviso, y "El médico verá que lo respondiste", que promete E3/E4.

**Sorpresas de entorno:**
- El daemon de Docker Desktop tardó en bajar imágenes base (proxy `http.docker.internal:3128`). Mientras tanto
  el backend se probó con `docker compose cp`; el rebuild terminó más tarde.
- Ya había un Vite tuyo en `:5173`; se usó sin matarlo.

**Deuda al inbox:** `validate_birth_date` con `date.today()` del servidor, y la red del daemon de Docker.
