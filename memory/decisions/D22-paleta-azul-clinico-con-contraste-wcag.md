---
id: D22
date: 2026-10-29
status: accepted
---

## D22 — Paleta: azul clínico con contraste WCAG 2.2 AA medido

- **Status:** Accepted · 2026-10-29 · decided by: Saúl Pérez (autor), navegando `product/prototipos/paleta.html`.
- **Decision:** la app usa la paleta **B · Azul clínico**, basada en la del NHS. Valores en
  `product/prototipos/paleta.html`, en `P.B`.
  - **Claro:** fondo `#f0f4f5`, tarjetas `#ffffff`, texto `#212b32`, secundario `#4c6272`, principal `#005eb8`
    con texto blanco, borde de controles `#4c6272`, error `#d5281b`, éxito `#007f3b`, aviso `#5c4400` sobre
    `#fff4c2`, sensible `#330072`.
  - **Oscuro:** lo diseñamos nosotros, porque el NHS no tiene. Fondo `#0f1a22`, tarjetas `#172630`, texto
    `#e8eef1`, principal `#5aa9f0` con texto `#0b1a26`, borde `#7a92a1`.
  - **Regla:**
    - todo texto mide al menos 4.5:1 contra su fondo;
    - el borde de campos, casillas sin marcar y botones secundarios mide al menos 3:1 (WCAG 1.4.11);
    - el error y lo sensible llevan texto o ícono, nunca solo color.
  - **Mismo cambio, también decidido por Saúl Pérez:**
    - casillas de 20 px con borde de 3:1;
    - la etiqueta de cada opción en peso normal y la pregunta del grupo en negritas.

    Esto cierra la deuda R2-4 y la del tamaño de casilla (`memory/closed/2026-10-28-ronda-2-de-ejercicio-lista-casillas.md`).
    Se aplica ya, antes de la mascota.
- **Why:**
  - Los colores de hoy, que son los de shadcn/ui con el verde azulado `oklch(0.598 0.107 182)` en
    `frontend/src/index.css:52`, no pasan AA. El texto blanco del botón principal da 3.61:1 en claro y 2.95:1 en
    oscuro. El borde de los campos y de las casillas sin marcar da 1.26:1. Medido el 2026-10-29 con la fórmula de
    luminancia de WCAG.
  - El azul se percibe algo más confiable en sitios médicos, con efecto «limitado».
  - La paleta del NHS apunta a AAA y lleva años usándose con pacientes (`memory/research/mascota-color.md`).
- **Discarded alternatives:**
  - **A · Verde azulado corregido:** era la recomendación del agente, por costo y continuidad con los prototipos.
  - **C · Cálido:** el principal y el error se confunden con deuteranopía.
- **Risks the agent noted, accepted by Saúl Pérez:**
  - El modo oscuro no tiene respaldo del NHS.
  - Con la edad empeora la distinción azul-amarillo, así que el aviso amarillo depende de su texto.
  - [OPINION] Puede verse institucional; la mascota puede compensarlo.
- **Applies to:**
  - los tokens de `frontend/src/index.css`;
  - el `Checkbox` de `components/ui/checkbox.tsx`;
  - los prototipos que se hagan desde ahora.

  Los prototipos ya hechos no se repintan.
- **Applied:** 2026-10-29 en `openspec/changes/archive/2026-10-29-paleta-azul-clinico/` (PR #37). La prueba `frontend/tests/visual-accessibility.spec.ts` mide los contrastes y la casilla.
