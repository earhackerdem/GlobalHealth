---
date: 2026-10-31
state: frozen
anchor: journal: 2026-10-31 · validaciones-hoy-y-texto-invisible: la fecha de nacimiento con el «hoy» de México y el texto invisible del historial (B2, T3)
---
Ronda 1 de validaciones-hoy-y-texto-invisible (PR #47): diez hallazgos; nueve corregidos en el PR (C1 pagado con B2), y la mitad de I es un falso positivo

**Verdict and why:** gate por delegación de Saúl Pérez (author), con la reproducción del validador del 2026-10-31.
- **Falso positivo:** «la segunda pasada de S04b hereda `aria-invalid` de la primera».
  - Es cierto que los errores no se limpian al editar.
  - Pero si el segundo valor se aceptara, el formulario se cerraría y guardaría. Eso hace fallar `toHaveCount(0)` y el
    conteo por API, y el rojo lo mostró.
- **Visto y no tomado (nota del validador, no hallazgo):** `_is_blank` trata como blanco todo Cf, incluidos signos
  árabes visibles (U+0600–0605). Ya era así antes del cambio y nadie los teclea en un campo de antecedentes.

**State:** 🔒 frozen

**Anchor (journal: date · title):** journal: 2026-10-31 · validaciones-hoy-y-texto-invisible: la fecha de nacimiento con el «hoy» de México y el texto invisible del historial (B2, T3)
