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
