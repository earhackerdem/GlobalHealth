# Exploration — bd-candados-indices-y-log

**Matriz aceptada por delegación de Saúl Pérez (author), 2026-10-31 (`/epe-autopilot`).**

## 1. Entrada
Siete escenarios con datos concretos y THEN observable (código, mensaje de la excepción, catálogo, estado final).

## 2. Cobertura por escenario
| Escenario | Estado | Evidencia (2026-10-31) |
|---|---|---|
| Error de BD sin el valor | ❌ | `backend/app/core/db.py:7` crea el engine sin `hide_parameters`; el validador del PR #46 vio `[parameters: {...}]` en `docker compose logs` y en `exception.values[].value`, y midió que `hide_parameters=True` lo quita de los dos (SQLAlchemy 2.0.51) |
| NUL en el alta / al editar | ❌ | `UserRegister.full_name`, `UserUpdateMe.full_name` (`models.py:31-48`) sin validación de NUL; Postgres no admite NUL en `varchar` → 500. El correo ya está cubierto: `EmailStr` rechaza `a\x00b@example.com` (medido) |
| NUL en el login | ❌ | `crud.authenticate` → `get_user_by_email` (`crud.py:43-62`) consulta con el `username` tal cual → 500 |
| NUL en un elemento | ❌ | `ItemBase.title/description` (`models.py:1420-1422`), del template, en claro |
| Llaves con índice | ❌ | consulta a `pg_constraint`/`pg_index` en la base de desarrollo: 9 llaves sin índice (lista en proposal.md) |
| Enlace a diagnóstico | 🟡 | `delete_health_record` (`routes/health_records.py:227-233`) toma `crud.lock_profile` (cero filas si no hay perfil) y desenlaza; `_check_diagnosis_link` (`routes/profile.py:175-195`) solo lee. La ventana es entre la lectura de `unlink_diagnosis` y el commit del DELETE |
| (R2) fila ilegible | 🟡 | `crud.py:107-108` hace `continue` sin log; la lista del historial sí registra el id (`routes/profile.py:224-226`) |

## 3. Lo que parecía útil y no lo fue
- Un handler de `DataError` que convierta cualquier error de la base en 422: oculta errores de verdad y depende del
  texto del driver. Validar el NUL en la entrada es local y explícito.
- Validar el NUL en los campos cifrados: no hace falta, porque el texto cifrado no lleva NUL (el validador del PR #46
  guardó un NUL en `allergies` y en `other_text` con 201).
- ⏸️ El interbloqueo DELETE de diagnóstico ↔ borrado de cuenta (`memory/closed/2026-10-20-ronda-2-de-perfil-cronicas-el.md`):
  su condición de entrada («si el borrado de cuenta se vuelve asíncrono o masivo») no se cumple. No se toca.

## 4. Restricciones no funcionales
NFR-001 y la privacidad: los valores salen del log. Rendimiento: los índices bajan los listados y la cascada de un
recorrido completo a una búsqueda por índice. NFR-009: una prueba por escenario.

## 5. Clasificación
**Extensión** con una migración. Sin preguntas abiertas.
