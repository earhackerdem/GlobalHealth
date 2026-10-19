# 2026-10-19 · receta-mexicana: apply del review (PR #13)

**Quién:** Saúl Pérez (author) aprobó el alcance tras la entrega en dos tiempos del /epe-4-review: todos los
confirmados + dos dudosos promovidos (confirmación también al editar desde el menú ⋯, C7; cobertura móvil con el
viewport de su S26 Ultra, K9) y un dudoso congelado (lenidad del null en campos retirados — fila en closed.md).

**Qué:** dos fixers (backend/frontend, archivos disjuntos, prefijo NO-CLOSED) aplicaron los ~25 hallazgos
aprobados; **cero rebotados**. Lo mayor: la migración c91f3b7a52e8 ya no destruye datos ante llave equivocada
(descifra con el MultiFernet del ORM y deja abortar InvalidToken — era el CRÍTICO), el PATCH rechaza null
explícito en `archived`/`occurred_on` con 422 es-MX, tope de 20 medicinas, campo "Vía" con round-trip (route ya
no se pierde al editar), confirmaciones en eliminar-adjunto y editar-por-menú, fila sin nombre avisa, Próximamente
visible, a11y (aria-labels distinguibles, HTML válido, foco de regreso, grupo por fila), botón de adjuntar es-MX,
chip "sin confirmar" en el detalle, y la suite e2e recuperó el test de eliminar, renombró el delta a D1–D4 y corre
también en el proyecto `s26-ultra` (384×832). El helper del tab-switch ahora aserta el refetch real (la mutación
que pasaba en verde ya falla). El orquestador actualizó validation/evidence/design, corrigió el journal del 18
(H1) y asentó 9 filas en closed.md (decisión del null, falsos positivos, diferidos menores).

**Verificación (re-corrida por el orquestador desde limpio):** backend **146 passed/0 failed/0 skipped** + mypy
Success; `tsc --noEmit` limpio; Playwright **33 passed** (setup + 16×2 proyectos); test nuevo de migración con BD
efímera en ambas llaves. Números y anchors en evidence.md § Apply.

**Deuda:** el detalle de solo lectura aún no muestra la "Vía" de cada medicina (el hallazgo pedía round-trip, no
exhibición; señalado por el fixer). Diferidos del review en closed.md (duplicaciones, claves muertas, tdd-check
baseline).

**Siguiente:** CI del PR #13 en verde → merge de Saúl → /epe-6-archive.
