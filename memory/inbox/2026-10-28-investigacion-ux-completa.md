---
date: 2026-10-28
status: open
---

**Investigación de UX completa del producto, ahora** (Saúl Pérez, 2026-10-28, después de mergear el PR #34). Va
antes de la C2b y de las deudas. Abarca tres hilos:
1. **Formularios del perfil.** Hoy, en Ejercicio, cada actividad elegida agrega sus campos debajo de las
   anteriores, en el orden del catálogo (`ACTIVITIES.filter` en `frontend/src/components/Profile/HabitsForm.tsx`).
   Con todas elegidas, la pantalla las muestra todas a la vez. La propuesta de Saúl Pérez son pestañas como las
   `nav-tabs` de Bootstrap, que muestren solo la última elegida. La investigación compara pestañas, acordeón con
   una sola abierta y tarjetas de resumen editables, con estos criterios:
   - hasta 9 actividades a 400 px de ancho;
   - errores que quedan en una pestaña oculta ("Escribe cuál.", días o minutos faltantes);
   - si el chip sirve a la vez para elegir y para navegar, volver a tocarlo lo desmarca;
   - el total semanal a la vista;
   - lectores de pantalla (patrón tabs de la APG);
   - el mismo patrón en el resto del perfil.
2. **Identidad:** mascota "casi Duolingo" y paleta. La investigación está en `memory/research/mascota-color.md` y
   falta decidir (`memory/inbox/2026-10-20-experiencia-casi-como-duolingo-mascota-que.md`).
3. **Captura:** texto libre, catálogo o híbrido; es la ronda 2 del dominio. La investigación está en
   `memory/research/captura-catalogos.md` y el híbrido es la dirección adoptada
   (`memory/inbox/2026-10-20-ronda-2-del-dominio-medicina-diagnostico.md`).

**Why it matters:** La pantalla de hábitos real, con 9 actividades, mostró lo que el prototipo no hizo ver. Los
tres hilos mueven pantallas de varias épicas, así que conviene decidirlos juntos antes de construir la C2b o
pagar deuda en pantallas que van a cambiar.

**Status:** abierto · triage: PRD (varias épicas no deben divergir). **Hilo 1 hecho** (2026-10-28): investigación en `memory/research/formularios-ux.md`, Saúl Pérez eligió la variante E, D18 revisada, y el cambio está archivado en `openspec/changes/archive/2026-10-28-ejercicio-lista-casillas/` (PR #35). Siguen los hilos 2 (identidad: mascota y paleta) y 3 (captura), que hay que decidir con Saúl Pérez como prototipos navegables, y después actualizar `product/prd.md`. Deuda de estilo pendiente: tamaño de las casillas y peso de la etiqueta frente a la pregunta, para toda la app (`memory/closed/2026-10-28-ronda-2-de-ejercicio-lista-casillas.md`).

**Hilo 3 hecho (2026-10-29):** Saúl Pérez fijó el orden, primero la captura, después los colores y al final la mascota. La captura quedó decidida en D21 (`product/prototipos/captura-hibrida.html`, FR-029..031). Siguen la paleta y después la mascota (`memory/research/mascota-color.md`).
