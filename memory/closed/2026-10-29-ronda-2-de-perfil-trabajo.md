---
date: 2026-10-29
state: deferred
anchor: journal: 2026-10-29 · perfil-trabajo (C2b): «Trabajo» en el Perfil básico
---
Ronda 2 de perfil-trabajo (PR #40, diff 9788715..9d404cb): de cuatro hallazgos bajos, quedan como deuda dos (R2-2 y R2-4) y el resto de lo diferido en la ronda 1

**Verdict and why:** La ronda 2 la hizo un finder sobre el delta de la ronda 1. Comprobó que V1 a V9 se sostienen y
encontró cuatro hallazgos bajos. No pasaron por validador, por la regla de cierre que Saúl Pérez aprobó con el plan
(`design.md`, Decision 7): si una ronda después de la primera trae solo hallazgos bajos, quedan como deuda registrada
y se archiva. Ninguno pierde datos ni deja de cumplir T-1 a T-6.

- **R2-2:** mientras guarda, la X del diálogo «Tu trabajo» desaparece (`showCloseButton={!busy}`,
  `EditWork.tsx:143-146`). D20 pide `aria-disabled="true"` y que el botón siga en el recorrido del teclado, como
  «Cancelar». Ninguna sesión pierde el foco, porque guardar nunca empieza desde la X, pero las dos salidas se
  comportan distinto. Se paga con D20 en `components/ui/dialog.tsx`, para todos los diálogos, en la tarea de deudas.
- **R2-4:** en el prototipo de producto, `resumenTrabajo` (`perfil-secciones.html:277`) dice «Sin llenar» con solo
  «el trabajo de más años», donde la app muestra «antes: …». Se paga junto con la deuda de «Sin llenar» del
  prototipo.
- **Diferido en la ronda 1:**
  - «Sin llenar» como etiqueta vacía de todas las secciones del prototipo de producto;
  - los punteros a `research.md` de `product/dominio.md` anteriores a la partición en `memory/research/`.

R2-1 (las filas de la ronda 1 en la tabla del pase exploratorio quedaban fuera de la tabla por una línea en blanco)
y R2-3 (el ancla `:258` del párrafo del cambio de formato, hoy `:282`) se corrigieron al cerrar, porque la evidencia
debe ser fiel (AGENTS.md). Es el mismo precedente que R2-3 y R2-5 de ejercicio-lista-casillas.
