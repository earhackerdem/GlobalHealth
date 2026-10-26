---
date: 2026-10-22
state: deferred
anchor: journal: 2026-10-22 · perfil-habitos-completitud (C-15…C-17)
---
F de perfil-habitos-completitud (PR #33, ronda 1): las preguntas que una respuesta de hábitos vuelve obligatorias (C-15) no se marcan como tales: las cajas de número sin `aria-required` ni `*` (`HabitsForm.tsx` número `Input`), los grupos de chips sin requerido; un lector de pantalla las lee como opcionales hasta tocar "Guardar"

**Verdict and why:** Validado como instancia nueva de ⏸️ R8 (perfil-cronicas, aceptada por Saúl Pérez el 2026-10-20): la única otra pregunta que se vuelve obligatoria según una respuesta ("¿Cuál fue?" con "Otra", `HistoryEntryForm.tsx`) tampoco se marca, y la convención `*` + `aria-required` de la casa cubre solo campos siempre obligatorios. El contrato aprobado (`design.md` § Frontend) no pidió marcador: la regla va en la introducción y "Guardar" marca lo que falta con el foco al primero; los demás errores se leen al llegar con Tab (`aria-invalid` + descripción). Saúl Pérez aprobó la recomendación ("procede", 2026-10-22). Se paga con R8: `aria-required={required.has(key) || undefined}` en las cajas, `*` solo con una línea de leyenda, y el requerido de los chips en `ChipGroup` para todas las pantallas

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-22 · perfil-habitos-completitud (C-15…C-17)
