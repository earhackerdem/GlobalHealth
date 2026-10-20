# Exploration — perfil-cronicas

Date: 2026-10-20 · Base branch: `feat/perfil-cronicas` (sale de `origin/main` con perfil-eventos ya mergeado y
archivado) · Explored by: el agente (orquestador), para Saúl Pérez (author)

## 1. Input validation

| Check | Result |
|---|---|
| As/I want/so that story with a concrete role | ✅ "Como paciente, quiero registrar mis enfermedades crónicas, para que el médico y la IA conozcan mi condición actual aunque no tenga el papel del diagnóstico." (proposal.md § User story) |
| Every AC in Given/When/Then with concrete data | 🟡 B-0…B-6 son observables y traen los datos concretos del prototipo v4 y del dominio (listas, estados, mensajes), pero aún no tienen forma GWT. Con `engine: openspec` se escriben como scenarios en `/epe-2-plan`, igual que la Story A. No bloquea |
| No imposed technical solution | ✅ Ninguno dicta tecnología. B-6 es el NFR-001 heredado |

## 2. Coverage matrix per criterion

| AC | Coverage | Where (file:line / dependency / URL + date) | Missing |
|---|---|---|---|
| B-0 la sección como las de la Story A | 🟡 Partial | Todo existe para 4 secciones: `HistorySection` (`backend/app/models.py:488`) y su orden `HISTORY_SECTIONS` (`:489`), "ninguna" con 409 si hay registros (`backend/app/api/routes/profile.py:543`), borrado del registro (`:532`), "registro vacío" con 422 (`models.py:700`). En el front: `HISTORY_SECTIONS` y slugs (`frontend/src/components/Profile/history.ts:10,32`), la tarjeta de crónicas existe pero no se abre (`frontend/src/routes/_layout/perfil.tsx:151,179`) | Agregar `chronic` a las listas de secciones del back y del front, con slug y tarjeta que abre; el resto se hereda |
| B-1 condición + salud mental sensible + otra | ❌ New (con patrón) | Mismo patrón de catálogo + "otra" que `PastHistoryContent` (`models.py:546`) y su requerido (`HISTORY_REQUIRED`, `models.py:656`) | Catálogo de 11 condiciones + otra; la marca de categoría "salud mental", derivada en el servidor de la condición elegida (no la manda el cliente); chip "sensible" en la lista |
| B-2 estado + desde/hasta + "hasta" no antes de "desde" | 🟡 Partial | "Cuándo" ya existe completo: `When` discriminado (`models.py:537`), `validate_when` contra la edad y el año de nacimiento con "hoy" de México (`models.py:679`, `profile.py:153-160`), el widget `WhenField` y `approxYears`/`STAGE_AGE_RANGES` en el front (`history.ts:65,98`) | Dos campos "cuándo" en lugar de uno (`validate_history_content` hoy valida solo `content.when`, `models.py:716`); la regla "hasta" ≥ "desde"; "hasta" solo con "Ya no la tengo" |
| B-3 tratamiento + nota | ✅ Exists (patrón) | Textos opcionales con `HISTORY_TEXT_MAX` = 2000 (`models.py:498`) y `<Textarea>` para ese tamaño (H2 de perfil-eventos) | Dos campos más en el esquema |
| B-4 enlace opcional a un diagnóstico | ❌ New | Los diagnósticos son `HealthRecord` con `record_type="diagnosis"` y `title` (`models.py:114,119,122`); lista solo del dueño en `GET /health-records` (`backend/app/api/routes/health_records.py:131`, sin filtro por tipo y `limit=100` por defecto); "dueño o 404" en `_get_owned_record` (`health_records.py:53`) | Guardar el id del diagnóstico dentro del JSON cifrado (no hay llave foránea posible: el contenido va cifrado, Decision 2 de perfil-eventos); validar al guardar que el id sea un diagnóstico del mismo paciente; selector de diagnósticos y "Respaldo: …" en la lista |
| B-5 aviso al borrar un diagnóstico enlazado | ❌ New | El borrado ya pide confirmación con texto fijo: `DeleteRecord` (`frontend/src/components/Records/DeleteRecord.tsx:28`), `records.json:98` ("¿Seguro que quieres eliminar este registro? Se eliminarán también sus adjuntos."); requirement "El expediente es del dueño: aislado, corregible y eliminable" (`openspec/specs/records/clinical-records/spec.md:65`) | El diálogo nombra las crónicas que el diagnóstico respalda; al borrar, el enlace se quita de esas crónicas |
| B-6 cifrado, aislado, tras consentimiento | ✅ Exists (infra) | `medical_history_entry.content` cifrado con `EncryptedString` (`models.py:504-512`, D13), aislamiento con 404 (`_get_owned_history_entry`, `profile.py:189`), `ConsentedUser` en todas las rutas del historial | Nada nuevo: la sección viaja en el mismo JSON cifrado |

## 3. What looked useful and was discarded (and why)

- **Una tabla `chronic_condition` propia, con llave foránea al diagnóstico:** daría la integridad del enlace en la
  base, pero pondría en claro una relación paciente-diagnóstico-crónica y rompería la Decision 2 de perfil-eventos
  (una tabla genérica con todo el contenido cifrado). El enlace vive en el JSON cifrado.
- **Resolver el enlace solo al leer y dejar el id colgando cuando se borra el diagnóstico:** es más barato, pero la
  crónica guardaría para siempre el id de un dato que el paciente borró (ARCO, FR-003). Mejor quitarlo al borrar
  (§5).
- **Que el cliente mande la categoría "salud mental":** se podría desincronizar de la condición. Se deriva en el
  servidor. *(Superado por §8: la marca es un interruptor del paciente, con valor por defecto según la condición.)*

## 4. Non-functional constraints detected

| Constraint | Source | Severity | How it is addressed |
|---|---|---|---|
| NFR-001 cifrado en reposo | `product/technical-brief.md:57` | 🟢 | El contenido completo, enlace incluido, va en el JSON cifrado de `medical_history_entry` |
| La longitud del ciphertext revela la sección | `memory/closed.md:36` (S3, diferido el 2026-10-20) | 🟡 | Aplica igual a `chronic`; el veredicto lo cubre y no se re-litiga |
| Formulario hecho a mano en vez de RHF+zod | `memory/closed.md:37` (H5, diferido) | 🟡 | El formulario de crónica suma campos a esa deuda; se declara, no se migra aquí |
| FR-014 (enlaces por categoría) | `product/prd.md:32` | 🟢 | Solo se guarda la marca de categoría; compartir es E3/E4 |
| Selector de diagnósticos con `limit=100` | `health_records.py:131` | 🟡 | Un paciente con más de 100 registros no vería todos sus diagnósticos; el plan pide el límite necesario o un filtro por tipo |
| Accesibilidad y es-MX | D15, a11y del apply de perfil-eventos | 🟢 | Mismos componentes (foco, errores junto al campo, nombres accesibles) |

## 5. Change classification

**Extension.** Una sección más sobre la infraestructura de la Story A, más dos piezas nuevas: el enlace al
diagnóstico (B-4) y el aviso al borrarlo (B-5). Toca dos specs: `records/patient-profile` (crónicas llenables) y
`records/clinical-records` (el borrado del diagnóstico avisa y quita el enlace).

Supuestos con valor por defecto (el plan los usa salvo que Saúl diga otra cosa):
- **Enlace inválido al guardar:** un id que no sea un diagnóstico del mismo paciente se rechaza con 422 es-MX
  ("Ese diagnóstico no está en tu expediente"). Esto resuelve el `MISSING` de la propuesta.
- **Al borrar el diagnóstico:** en la misma transacción, el servidor descifra las crónicas del paciente y les quita
  el enlace (decenas de filas, el mismo supuesto de tamaño que perfil-eventos). La crónica se queda, y su lista ya
  no muestra el respaldo.
- **El aviso de B-5** se arma en el front con los datos del historial que ya trae `GET /profile/history`, sin una
  ruta nueva.
- **"Hasta" con estado "Activa":** no se guarda (se limpia), como en el prototipo (`si: estado === "Ya no la
  tengo"`).
- **"Hasta" antes de "desde"** se rechaza cuando ambos se pueden comparar: edad con edad, etapa con edad por sus
  rangos, y año con edad solo si hay fecha de nacimiento.

Pistas para el plan:
- `validate_history_content` pasa a validar todos los campos `When` del contenido, no solo `when`.
- `chronic` va primero en `HISTORY_SECTIONS`, como la tarjeta.
- El borrado del diagnóstico llama a un helper del historial que quita el enlace, para no duplicar el descifrado.
- El prototipo v4 ya muestra B-1…B-4. B-5 no está en el prototipo: se agrega al mock antes del gate del plan.

## 6. Blocking questions (max 4)

1. **"Otra" condición y salud mental.** La marca "sensible" sale de la lista: depresión, ansiedad y trastorno
   bipolar. Si el paciente escribe en "otra" algo de salud mental (p. ej. "TOC"), no queda marcada y FR-014 no la
   podría ocultar al compartir. Opciones:
   - **(a, recomendada)** Junto a "otra", la pregunta opcional "¿Es de salud mental?", que la marca igual que las de
     la lista.
   - **(b)** Solo se marcan las de la lista, como en el prototipo. Más simple, pero puede filtrar algo sensible el
     día que exista el compartir.

## 7. Sources consulted

- Código del repo en `main` al 2026-10-20 (anclas en §2).
- `product/dominio.md` § Enfermedad crónica (Story B), § Procesos, § Open questions 2 (respondida el 2026-10-20).
- `product/prototipos/perfil-secciones.html` v4 (B-1…B-4).
- `openspec/specs/records/patient-profile/spec.md` y `openspec/specs/records/clinical-records/spec.md`.
- `memory/closed.md` (S3, H5), `memory/decisions.md` (D13, D15), `product/technical-brief.md` § 4.
- Archivo de perfil-eventos: `openspec/changes/archive/2026-10-20-perfil-eventos/design.md` (Decisions 2–4).

## 8. Respuestas del gate (Saúl Pérez, 2026-10-20)

- **§6 pregunta 1 → "Interruptor por crónica":** prefirió la opción (a) y la amplió: cada crónica lleva su propio
  interruptor "Sensible", prendido por defecto en salud mental y adicciones. Pidió primero un CRUD de enfermedades
  con su marca sensible. La objeción (entidad nueva con pantallas y reglas al editar o borrar del catálogo; cada
  crónica ya es "su" enfermedad) la aceptó al elegir el interruptor. Queda como B-1b en la propuesta.
- **Adicciones en el grupo sensible:** "Consumo de alcohol u otras sustancias" entra a la lista junto a salud mental,
  como las agrupa la LGS art. 72 (`memory/research.md#salud-mental-lgs`). El detalle del consumo sigue en Hábitos
  (Story C).
- **Matriz §2 y supuestos §5:** sin objeciones. Pasa a `/epe-2-plan`, cuyo gate es el "plan approved" sobre el
  prototipo actualizado (B-1b y B-5).
- **Fuera de foco:** compartir por secciones y por marca sensible (FR-014, E3/E4) queda en el inbox.

