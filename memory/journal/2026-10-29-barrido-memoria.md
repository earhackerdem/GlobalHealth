---
date: 2026-10-29
---

# Barrido de memoria tras dos compactaciones

**Quién e intención.** Saúl Pérez (autor) pidió el barrido («haz lo de la memoria») al cerrar la investigación de UX
y antes de empezar la C2b.

**Qué se hizo.**
- `make memory-check` sin pistas mecánicas. Las 6 memorias privadas se verificaron contra el repo: siguen siendo
  ciertas (harness 0.4.0 igual al template, `playwright.config.ts:4`, la exclusión de `.claude/hooks/` en
  `.pre-commit-config.yaml:46`, la ruta `/consent`).
- Al repo, en el bloque `harness:context` de `AGENTS.md`: cómo correr e2e como el CI, el `testMatch` de
  `s26-ultra` que deja fuera una prueba nueva sin avisar (pasó en la paleta), el comando de `tsc`, el gate de
  `typos` con palabras en español y los dos e2e intermitentes conocidos.
- Al inbox de e2e intermitentes, la evidencia del 2026-10-29 (PR #37).
- A la memoria privada: una regla nueva (al menos una variante que rompa el patrón de UI vigente, porque las casillas
  de Ejercicio las propuso Saúl Pérez y no el agente), y dos memorias recortadas para apuntar al repo.

**Cuenta.** Corregidas 2 (privadas, ahora apuntan al repo) · borradas 0 · nuevas 1 privada y 2 en el repo
(bloque de contexto e inbox).
