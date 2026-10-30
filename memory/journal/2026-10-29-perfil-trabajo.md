---
date: 2026-10-29
---

# perfil-trabajo (C2b): «Trabajo» en el Perfil básico

**Quién e intención.** Saúl Pérez (autor), con la investigación de UX cerrada, pidió seguir con la C2b: el bloque
«Trabajo» (C-9) que quedó pendiente al partir la C2 el 2026-10-26.

**Exploración y plan.** Saúl Pérez eligió las cuatro recomendaciones:
- diálogo propio desde Datos básicos;
- una sola situación laboral, sumando «No puedo trabajar por mi salud»;
- a qué te dedicas, exposiciones y turno solo con «Trabajo»;
- sin «Cargar peso», que ya pregunta el movimiento del día.

El turno ganó respaldo: la IARC clasifica el trabajo nocturno en el Grupo 2A (`memory/research/ocupacion.md`). La
categoría de INEGI que respalda «No puedo trabajar por mi salud» quedó NOT VERIFIED en el original. Saúl Pérez navegó
el prototipo y escribió «plan approved».

**Ejecución.** Dos grupos test→impl.
- **Backend:** rojo 23 de 583, todos por 404. Verde 583 passed, cobertura 96 %, mypy y ruff limpios, migración que
  sube y baja.
- **Frontend:** el primer rojo del tester era inválido, porque la base de desarrollo no tenía la migración (reconstruir
  el contenedor no la aplica). El orquestador la aplicó y el rojo quedó en 14 fallas por lo que faltaba. Verde: 27
  passed en chromium y s26-ultra, con `tsc` y `biome` limpios.
- `make tdd-check` ✓ en los dos.
- **Suite completa como CI:** 366 passed y 1 failed (`reset-password.spec.ts:90`, el intermitente heredado, que pasa
  solo).
- **Pase en Chrome sin defectos:** emoji, espacios, doble clic, Escape, más de 200 caracteres, ventana angosta.

**Lo que se aprendió y quedó escrito.**
- La receta de e2e del bloque de contexto de `AGENTS.md` ahora incluye `prestart.sh`, como el CI.
- El implementer encontró que el hook `lint.py` compila con el Python del sistema (3.9) y marca como error la sintaxis
  3.14 de `profile.py:224`. La propuesta está en `memory/meta-improvements/2026-10-29-lint-hook-interprete-del-proyecto.md`
  y va upstream antes de la siguiente historia, si Saúl Pérez la aprueba.

**Deuda.**
- «Truly green» sin marcar por el intermitente heredado.
- Sin aviso al borrar lo del trabajo cuando cambia la situación (T-6, decidido así).
- La ocupación no se codifica.

## Revisión adversaria, ronda 1 (mismo día)

Saúl Pérez eligió revisar antes de archivar. Hubo dos finders y un validador distinto, que reprodujo los 9 hallazgos
con Playwright, mutantes en una copia del backend y la API. Los 9 se confirmaron y todos quedaron bajos. Saúl Pérez
aprobó «Todo lo recomendado». Un fixer aplicó V1, V2 y V5 a V9 sin rebotar ninguno, y el orquestador hizo V3 y V4.

- V1: la X del diálogo ya no se muestra mientras guarda (D20).
- V5: las filas de la tarjeta parten las palabras largas.
- V8 y V9: dos pruebas nuevas, y los mutantes que sobrevivían ahora mueren.
- V2, V6 y V7: el prototipo de producto normaliza, y se corrigieron citas.
- V3 y V4: las anclas de evidence, y se completó el pase en Chrome que la tarea 3.2 daba por hecho: modo claro, las
  tres situaciones que faltaban y «Nada de esto» contra cada exposición.

Verde, re-corrido por el orquestador:
- backend 588 passed;
- e2e 27 passed en chromium y s26-ultra;
- `tsc` y `biome` limpios;
- `make tdd-check` ✓.

**Corrección en línea a este journal:** la sección «Ejecución» decía que el pase en Chrome había cubierto «ventana
angosta». Fue a 500 px y solo en oscuro; el resto se completó en esta ronda.

**Sobre el índice de veredictos en los briefs:** los dos finders recibieron solo las filas pertinentes del índice
`make closed` y la ruta al índice completo, que se les pidió leer. El validador recibió el índice casi literal, con
algunos veredictos largos abreviados. Ni lo uno ni lo otro es la copia literal que pide el skill. El hook lo aceptó
porque encontró encabezados del índice en el prompt.

**Saúl Pérez, durante la revisión:** después de este PR la prioridad es Android, en app nativa, y más adelante iPhone
nativa (`memory/inbox/2026-10-29-prioridad-app-android.md`). Esto revisa D7 y toca D17.
