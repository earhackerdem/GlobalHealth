---
date: 2026-10-31
---

# validaciones-hoy-y-texto-invisible: la fecha de nacimiento con el «hoy» de México y el texto invisible del historial (B2, T3)

**Quién:** Saúl Pérez (author), con `/epe-autopilot` («toma las tareas que correspondan a fast api»). Segundo cambio del
lote: el grupo «validaciones» del inventario de deudas.

**Qué se hizo:**
- **API (`test→impl`):**
  - `validate_birth_date(birth_date, today)` recibe el «hoy» de Ciudad de México, como los demás validadores. Antes
    usaba `date.today()`, y el contenedor corre en UTC (medido).
  - `_is_filled` usa `_is_blank`, de hábitos.
- **Pantalla (`test→impl`):** `isBlank` se movió a `Profile/text.ts`, compartido por hábitos y el historial.
- **T3:** la prueba de la fecha futura usa «pasado mañana en México».

Los testers y los implementers de API y pantalla corrieron a la par, sobre archivos disjuntos.

**Por delegación:**
- Matriz aceptada y diseño aprobado.
- Rechazar, no vaciar, el texto invisible.
- `isBlank` compartido.
- Fecha relativa a +2 días.

**Verificación:**
- **Rojo:** 7 en la API y 2 en e2e (`82d7e46`).
- **Verde:** 596/0/0/0 en el backend, cobertura 96 %; e2e 243/0/0/0 en chromium y s26-ultra; tsc y biome limpios;
  `tdd-check` ✓.
- **Pase exploratorio en Chrome:** el texto invisible se rechaza en la caja; doble clic con «Zika» da un solo registro.

**Tropiezo:** `guard-review-brief.py` bloqueó el brief del implementer de backend por la palabra «validators»
(validadores de código). Se relanzó con `NO-CLOSED:`; la propuesta está en
`memory/meta-improvements/2026-10-31-guard-review-brief-validators-de-codigo.md`.

**Deuda:** otros formularios con `.trim()` (`memory/inbox/2026-10-31-trim-en-otros-formularios-del-perfil.md`).
