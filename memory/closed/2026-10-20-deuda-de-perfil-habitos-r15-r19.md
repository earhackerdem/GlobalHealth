---
date: 2026-10-20
state: deferred
anchor: journal: 2026-10-20 · perfil-habitos (Story C1: sustancias y humo)
---

Deuda de perfil-habitos: R15 (el grupo "¿Dónde?" y el número "Días por semana" se nombran sin el contexto de su bloque, que solo está en el h2; clasificado dudoso) · R19 (la regla de edad duplicada y divergente: "Debe estar entre {{min}} y {{max}}" vs "La edad debe estar entre 0 y {{max}} años" en `profile.json`, `max: 130` literal 4× en `HabitsForm.tsx` pese a `MAX_AGE`, el mensaje del backend repetido en `models.py`) · R20 (`ChipMultiGroup` copia el botón y las clases de `ChipGroup` en vez de compartir un renderer) · R21 (la tarjeta de hábitos en `perfil.tsx` duplica el marcado título+chevron; el comentario de `CARD_LINK_CLASS` dice "(chevron included)" y la clase no lo incluye) · R23 (`NUMBER_FIELDS.label` guarda un sufijo de clave i18n; `draft: keyof Draft` más ancho que los campos de texto, obliga a casts)

**Verdict and why:** Confirmados (R15 dudoso) por los validadores, sin efecto visible; la misma clase de duplicación se difirió en las revisiones anteriores (precedentes ⏸️ H6-H10 y la deuda de perfil-cronicas). Aceptados como deuda por Saúl Pérez

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-habitos (Story C1: sustancias y humo)
