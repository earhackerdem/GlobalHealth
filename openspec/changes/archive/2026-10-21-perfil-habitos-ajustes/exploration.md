# Exploration — perfil-habitos-ajustes

Fecha: 2026-10-21 · Entrada: `proposal.md` (C-10…C-14), con el feedback de Saúl Pérez al validar la C1 y sus respuestas
del mismo día (A: un solo cambio con lo técnico; B: horas al día en leña; C: vapeador "todos los días / algunos días"
con días de los últimos 30, más edades; D: orden #30 → este cambio → C2 → deudas → investigación de UX).

## 1. Input validation

| Check | Result |
|---|---|
| As/I want/so that story with a concrete role | ✅ "Como paciente, quiero contar desde cuándo y cuánto tomo, vapeo o me expongo al humo de leña, y que lo que contesto se guarde solo…" |
| Every AC in Given/When/Then with concrete data | 🟡 C-10…C-14 son observables y llevan sus opciones literales; los Given/When/Then con datos van en la spec delta, como en la C1 |
| No imposed technical solution | ⚠️ C-14 dice "los límites vienen del contrato del backend": lo pidió Saúl Pérez ("sacar las validaciones del spec"). Se explora igual y se verificó que es viable (§2) |

## 2. Coverage matrix per criterion

| AC | Coverage | Where (file:line / dependency / URL + date) | Missing |
|---|---|---|---|
| C-10 alcohol, edad de inicio | 🟡 Partial (patrón de tabaco) | `AlcoholHabit` solo tiene `quit_age` (`backend/app/models.py:858-860`); tabaco ya tiene inicio y fin con la regla "inicio ≤ fin" (`models.py:879-883`, `:973-986`); el formulario la repite a mano (`HabitsForm.tsx:298-302`). Ítem estándar: LOINC 63634-0, edad del primer consumo sin probaditas (`memory/research/habitos.md#vapeo-inicio`) | `start_age` en "Lo dejé" y "Actual", con "≤ dejó" y "≤ edad actual"; normalizar a null en "Nunca" |
| C-11 vapeador con frecuencia y edades | 🟡 Partial | Hoy es un texto `HabitStatus` (`models.py:904`) y un chip (`HabitsForm.tsx:83,108,325,615`). Medida: PATH "todos los días / algunos días" + días de los últimos 30; no hay medida validada en pods (`memory/research/habitos.md#vapeo-inicio`) | Pasa a objeto como `TobaccoHabit`: `status`, `frequency` (`daily`/`some_days`), `days_last_30` (1–30), `start_age`, `quit_age` |
| C-12 leña como rango + horas al día | 🟡 Partial | `WoodSmokeHabit` = `status` + `years` (`models.py:896-898`, normalización `:936-939`). Medida mexicana: horas-año = años × horas al día (Pérez-Padilla 1996, `memory/research/humo-lena.md`) | `start_age`, `quit_age` (solo "Antes"), `hours_per_day` (1–24); sin calcular horas-año (C-6) |
| C-13 se guarda solo | ❌ New | Hoy un solo "Guardar" que navega a `/perfil` (`HabitsForm.tsx:389-401`, `:423-432`) y "Cancelar" (`:691`). El `PUT` reemplaza el cuestionario completo (`profile.py`, perfil-habitos Decision 2), así que guardar a cada cambio es repetir el mismo `PUT`. No hay utilidad de *debounce* en el repo (grep `debounce`: 0) | Guardado con espera corta, uno a la vez y solo si todo es válido; estado accesible (`aria-live`); quitar "Guardar"/"Cancelar" (ver §6) |
| C-14 errores al momento, límites del contrato | 🟡 Partial | Ya hay validación en el cliente, pero solo al enviar (`HabitsForm.tsx:274-302`) y con los límites copiados (`max: 130` ×4, `:132-178`, deuda R19). El generador del proyecto (`@hey-api/openapi-ts` 0.97.3) trae plugin `zod` compatible con Zod 4; generado en el scratchpad desde `frontend/openapi.json`, da `cigarettes_per_day: z.int().gte(1).lte(100)` y edades `gte(0).lte(130)`, exactos al backend (2026-10-21). Zod ya se usa en formularios (`Records/PrescriptionForm.tsx`, `AddDiagnosis.tsx`) | Agregar el plugin a `frontend/openapi-ts.config.ts`; validar cada número con el esquema generado al salir del campo; las reglas entre campos ("≤ edad actual", "inicio ≤ fin") en una sola función del cliente, igual que `habits_errors` en el servidor |
| Datos guardados en la forma anterior | ⚠️ Riesgo | `_stored_habits` lee con el esquema cerrado (`extra="forbid"`, `models.py:855`; `profile.py:616-626`): una fila con `vaping: "current"` o `wood_smoke.years` ya no valida y **se leería entera como vacía** (camino de R2) | Conversión al leer (validador `mode="before"`): `vaping` texto → `{status}`; `wood_smoke.years` se descarta. Sin migración: solo hay cuentas de prueba locales (no hay flujo de despliegue en `.github/workflows/`) |
| C-6 sin interpretación | ✅ Regla vigente | `openspec/specs/records/patient-profile/spec.md:415-425` | Se extiende la prueba negativa a "horas-año" |
| Cifrado, aislamiento, consentimiento | ✅ Exists | Mismo `GET/PUT /profile/habits` y columna `EncryptedString` | Nada nuevo |

## 3. What looked useful and was discarded (and why)

- **Vapeadores o pods por semana:** sin medida validada; los dispositivos no son comparables (`habitos.md#vapeo-inicio`).
- **"Veces al día" en el vapeador:** predice las caladas con r = .58 y a la gente le cuesta reportarlo; Saúl Pérez
  eligió días de los últimos 30.
- **Calcular horas-año en la app:** sería un puntaje (C-6, NFR-008). Se guardan los datos crudos; el médico calcula.
- **Guardar el borrador en el navegador (localStorage):** dejaría datos de salud en una computadora compartida, y el
  listener de pestañas (N1) recarga al cambiar de cuenta. Se guarda en el servidor, cifrado.
- **Guardar también un campo inválido como null:** borraría lo que ya estaba guardado en ese campo. Mientras haya un
  error, no se guarda nada y la pantalla lo dice.
- **Migración de datos (descifrar, convertir, cifrar):** no hay datos reales; una conversión al leer basta y no deja
  filas a medias.
- **React Hook Form + `zodResolver` para toda la pantalla:** el formulario ya tiene su propio estado por bloque con
  reglas de visibilidad; rehacerlo agranda el cambio. Se usan los esquemas generados solo para los límites.

## 4. Non-functional constraints detected

| Constraint | Status | How it is met |
|---|---|---|
| NFR-001 / D13: cifrado en reposo | 🟢 | Mismo JSON cifrado; nada en el navegador (§3) |
| NFR-008 / C-6: sin interpretación | 🟢 | Sin horas-año ni puntajes; se extiende la prueba negativa |
| D18: chips para opciones | 🟢 | "Todos los días / Algunos días" en chips |
| WCAG 2.2: estado del guardado | 🟡 | Un mensaje de estado con `role="status"` (`aria-live="polite"`) que no robe el foco; errores junto a su campo (R5) |
| Carga de red | 🟡 | Un `PUT` por pausa y uno a la vez (si llega otro cambio, se manda el último al terminar) |
| Móvil 384 px | 🟡 | Tres números más; el estado del guardado visible sin tapar contenido |
| es-MX (D15) | 🟢 | Textos en `profile.json` |

## 5. Change classification

**Extension** de la C1 (mismo endpoint y pantalla), con una pieza **New** (guardado automático) y una de
configuración (plugin `zod` del generador). Ejecución sugerida: dos grupos `test→impl` (backend, frontend) como en la C1.

## 6. Blocking questions (max 4)

1. **¿Qué pasa con "Guardar" y "Cancelar"?** Con el guardado automático:
   - **(a) Recomendado:** se quitan. La pantalla dice "Guardando…", "Guardado" o "Sin guardar: corrige el campo
     marcado", y queda un botón "Volver a mi perfil" que antes de salir manda lo pendiente. Se pierde el "deshacer"
     que daba "Cancelar".
   - (b) Se quedan los dos, y el guardado automático solo protege contra salir sin querer.

Supuestos (se toman salvo que digas otra cosa):
- La edad de inicio del alcohol se pide en "Lo dejé" y en "Actual", como el tabaco.
- "Todos los días / Algunos días" y los días de los últimos 30 solo con vapeador "Actual" (para "Antes" no aplica).
- Las horas al día de leña se piden en "Antes" y en "Actual"; la edad de fin solo en "Antes".
- Los números se guardan al salir del campo; los chips, al tocarlos (con una espera corta).
- Lo guardado en la forma anterior: el vapeador conserva su respuesta; los "años" de leña se descartan y se pide la
  edad de inicio.

## 7. Sources consulted

- Código: `backend/app/models.py`, `backend/app/api/routes/profile.py`, `frontend/src/components/Profile/HabitsForm.tsx`,
  `frontend/openapi-ts.config.ts`, spec canónica `records/patient-profile` (2026-10-21).
- Generación de prueba del plugin `zod` en el scratchpad, sin tocar el repo (2026-10-21).
- `memory/research/habitos.md#vapeo-inicio` y `memory/research/humo-lena.md` (fuentes primarias citadas ahí, 2026-10-21).
