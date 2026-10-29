# Design

Status: DRAFT

**En una frase:** el perfil suma un bloque «Trabajo» cifrado y 1:1, guardado entero con `PUT /profile/work`, que se
edita en su propio diálogo desde la tarjeta Datos básicos y se resume en una fila de esa tarjeta, sin ningún veredicto.

## Context

- El Perfil básico se muestra en `frontend/src/routes/_layout/perfil.tsx:72-115` (filas con `Row`, `:43`) y se edita
  en el diálogo `EditBasicData.tsx:115`, junto a `AddMeasurement`.
- Hábitos ya tiene el patrón de bloque 1:1: columna cifrada `habits` (`backend/app/models.py:443`), esquema cerrado
  (`_ClosedSchema`, `:861`), `GET`/`PUT /profile/habits` de reemplazo entero (`backend/app/api/routes/profile.py:659`,
  `:668`) con `_lock_profile` (`:146`) y su query en `frontend/src/components/Profile/queries.ts:31`.
- Saúl Pérez respondió las cuatro preguntas de la exploración el 2026-10-29 (`exploration.md` § 5): diálogo propio,
  una sola situación más «No puedo trabajar por mi salud», el detalle solo con «Trabajo», y sin «Cargar peso».

## Goals / Non-Goals

**Goals:** C-9 con T-1…T-6 de la spec delta.

**Non-Goals:** codificar la ocupación (catálogo NIOSH); el trabajo en el asistente de bienvenida (FR-027); la mascota
y sus «¿Por qué lo pedimos?» (D23, después de este cambio); el historial de trabajos anteriores más allá del de más
años; cualquier riesgo laboral calculado; una vista para el médico.

## Qué se toca / qué NO

| Se toca | NO se toca |
|---|---|
| `backend/app/models.py` (columna `work`, esquema `Work`, `normalize_work`), `backend/app/api/routes/profile.py` (`GET`/`PUT /profile/work`), una migración nueva | `PatientProfileUpdate` y `PUT /profile`, hábitos, el asistente de bienvenida |
| `frontend/src/components/Profile/EditWork.tsx` (nuevo), `perfil.tsx` (fila y botón), `queries.ts`, `frontend/src/locales/es-MX/profile.json`, cliente regenerado | `EditBasicData.tsx`, `ChipGroup.tsx`, `ui/*`, `HabitsForm.tsx` |
| Tests: `backend/tests/api/routes/test_profile_work.py` (nuevo), `frontend/tests/profile-work.spec.ts` (nuevo) y su entrada en el `testMatch` de `s26-ultra` (`frontend/playwright.config.ts:54`) | Las suites de las demás secciones |
| `product/dominio.md` § Trabajo, `product/prototipos/perfil-secciones.html` (C-9), `memory/research/ocupacion.md` (el dato de la IARC) | Las decisiones |

**Decisiones afectadas:** D18 (chips para las opciones; las exposiciones son múltiples sin datos propios, así que van en
chips), D20 (botones no disponibles mientras guarda), D22 (paleta) y D13 (cifrado) se aplican; ninguna cambia.

**Citadores que vencen:** la spec canónica (vía la delta); `product/dominio.md` § Trabajo (lista de situaciones, «cargar
peso», el `[ASSUMPTION]` del turno, «se pregunta todo siempre»); el prototipo de producto
(`perfil-secciones.html:153`, `:274-297`, con «Cargar peso» y los campos siempre visibles).

## Interface contract

Base `/api/v1`, detrás de `ConsentedUser`.

```
GET  /profile/work  -> 200 Work         # sin perfil o sin trabajo: todo null / vacío; leer no crea el perfil
PUT  /profile/work  body Work -> 200 Work (normalizado y guardado)   # reemplaza el bloque entero
                    -> 422 de esquema con loc ["body", <campo>] (y su índice en exposures)

Work (cerrado: una propiedad extra es 422):
  status:       "employed" | "looking" | "retired" | "homemaker" | "student" | "unable_health" | null
  occupation:   str, máx. 200 | null      # solo con employed
  longest_job:  str, máx. 200 | null      # con cualquier situación, también sin ella
  exposures:    list["dust" | "chemicals" | "loud_noise"], máx. 3, default []   # solo con employed
  no_exposures: bool, default false       # «Nada de esto»; solo con employed
  shift:        "day" | "night" | "rotating" | null                              # solo con employed
```

Normalización en el servidor, en este orden: recortar espacios (un texto vacío queda `null`, y el máximo se mide
después de recortar); quitar exposiciones repetidas; si `no_exposures` es `true`, `exposures` queda `[]`; si `status`
no es `employed`, `occupation`, `exposures`, `no_exposures` y `shift` quedan vacíos. Si todo queda vacío, la columna
guarda `null`.

Pantalla: en la tarjeta `profile-basic-data`, un botón «Editar trabajo» abre un diálogo con título «Tu trabajo» y
descripción «El médico lo pregunta porque lo que haces todo el día también es salud.». La tarjeta suma la fila
«Trabajo» con el resumen de la spec delta (ocupación o etiqueta de la situación · turno en minúsculas · «antes: » +
trabajo de más años tal cual · «expuesto a » + exposiciones en minúsculas separadas por «, »), o «Sin registrar».
Etiquetas es-MX: Trabajo · Busco trabajo · Jubilado o pensionado · Hogar · Estudio · No puedo trabajar por mi salud;
Polvo · Químicos o solventes · Ruido fuerte · Nada de esto; De día · De noche · Rotativo.

## Decisions

1. **Bloque propio con reemplazo entero, como hábitos**, no campos en `PUT /profile`: la exclusión de «Nada de esto» y
   el borrado según la situación son más simples sobre el bloque completo. Descartado: `PatientProfileUpdate` parcial.
2. **El servidor normaliza en vez de rechazar** lo que no aplica (otra situación, «Nada de esto» con exposiciones),
   como `normalize_habits` (`models.py:1096`). Rechaza solo lo que está fuera de las opciones o del largo.
3. **Diálogo propio** (Saúl Pérez, 2026-10-29). Descartados: el diálogo de datos básicos (8 campos) y una pantalla
   propia.
4. **«No puedo trabajar por mi salud»** se suma a las situaciones (Saúl Pérez). INEGI separa a quienes tienen
   «impedimentos personales» según un resumen de búsqueda [NOT VERIFIED en el original].
5. **Sin «Cargar peso»** (Saúl Pérez): ya lo pregunta el movimiento del día (C-7).
6. **Turno con evidencia:** la IARC clasificó el trabajo nocturno en el Grupo 2A (vol. 124, consultado 2026-10-29); se
   registra en `memory/research/ocupacion.md` y el dominio pierde el `[ASSUMPTION]`.
7. **Regla de cierre de la revisión**, decidida antes de la primera ronda: si una ronda después de la primera trae solo
   hallazgos bajos, quedan como deuda registrada y se archiva. Saúl Pérez puede elegir archivar sin revisión, como en
   la paleta.

## Test plan (one row per scenario, mandatory)

| # | Spec · scenario | Test | Dónde |
|---|---|---|---|
| 1 | Guardar el trabajo y verlo en la tarjeta (T-1) | pytest: `PUT` con employed, «Chofer de transporte», `["loud_noise"]`, rotating → 200 y GET igual. e2e: abrir «Editar trabajo», contestar, guardar, ver «Chofer de transporte · rotativo · expuesto a ruido fuerte» en la tarjeta y las respuestas al reabrir | pytest + Playwright |
| 2 | Todo es opcional (T-2) | pytest: `PUT {}` → 200, todo vacío, la columna queda `null`; GET sin perfil no lo crea. e2e: guardar sin contestar → «Sin registrar» | pytest + Playwright |
| 3 | «Nada de esto» y una exposición se excluyen (T-3) | pytest: `no_exposures: true` con `["dust"]` → se guarda sin exposiciones. e2e: Polvo → Nada de esto quita Polvo; Químicos quita Nada de esto | pytest + Playwright |
| 4 | Jubilado con el trabajo de más años (T-4) | pytest: retired con «Minero» y además `occupation`/`shift` → se descartan, «Minero» queda. e2e: con «Jubilado o pensionado» no se ven a qué te dedicas, exposiciones ni turno; tarjeta «Jubilado o pensionado · antes: Minero» | pytest + Playwright |
| 5 | Cambiar de situación borra lo del trabajo (T-6) | pytest: guardar employed completo y después looking con el mismo cuerpo → GET sin occupation, exposiciones ni shift; «Taxista» queda. e2e: cambiar a «Busco trabajo», guardar, tarjeta «Busco trabajo · antes: Taxista» y al reabrir con «Trabajo» los campos vacíos | pytest + Playwright |
| 6 | Fuera de opciones o de largo | pytest: status, exposición o turno desconocidos, texto de 201 tras recortar, una propiedad extra, `exposures` de 4 → 422 con su `loc`; GET sin cambios; «  Albañil  » se guarda recortado y «   » queda `null`. e2e: el campo no deja escribir más de 200 | pytest + Playwright |
| 7 | Solo del paciente y cifrado (T-5) | pytest: el otro usuario recibe su trabajo vacío; «Chofer de transporte» no aparece en claro en la fila; sin consentimiento, GET y PUT → 403 | pytest |
| 8 | Sin veredicto (C-6) y accesibilidad, D20 | pytest: la respuesta no trae campos de riesgo. e2e: cada grupo de chips tiene nombre accesible; con el `PUT` retenido, «Guardar» y los chips no están disponibles; ninguna palabra de riesgo en el diálogo ni en la tarjeta; a 384 px el diálogo no se desborda | pytest + Playwright |

## Non-functional constraints addressed

- **NFR-001 / D13:** columna `EncryptedString` (fila 7).
- **NFR-004:** `ConsentedUser` en las dos rutas (fila 7).
- **NFR-008 / C-6:** sin riesgo ni veredicto (fila 8).
- **NFR-012 / D15:** textos en `profile.json`.
- **Accesibilidad:** grupos de chips con nombre, foco al abrir el diálogo, prueba a 384 px en `s26-ultra` (fila 8).

## Risks / Trade-offs

- **Migración de una columna** que admite nulos, como la de hábitos: lo guardado antes lee el trabajo vacío.
- **El texto libre no se codifica:** «chofer» y «conductor» quedan distintos para la IA. Es lo que el dominio decidió.
- **Al cambiar de situación se pierde lo del trabajo** sin aviso (T-6). Es lo que se decidió; si en la validación
  molesta, un aviso es un cambio aparte.

## Migration Plan

Una revisión de Alembic que agrega `patient_profile.work` (texto cifrado, nulo por defecto) y su `downgrade` que la
quita. Sin migración de datos.

## Gate that closes the work

1. La suite completa de pytest del backend, truly green, cobertura ≥ 90 % y mypy limpio.
2. `profile-work.spec.ts` en chromium y s26-ultra, truly green, y la suite completa como CI contra la imagen
   reconstruida.
3. `make tdd-check` verde.
4. `openspec validate perfil-trabajo --strict` limpio.
5. La exploración en Chrome hecha por el agente, sin defectos; la revisión con la regla de la Decision 7 (o el archivo
   sin revisión si Saúl Pérez lo elige); el archivo como último commit del PR. Después, la validación de Saúl Pérez con
   `validation.md`. El merge es humano.

## Open Questions

Ninguna bloqueante. Se aprueban con el prototipo: el máximo de 200 caracteres, el resumen de la tarjeta y los textos.
