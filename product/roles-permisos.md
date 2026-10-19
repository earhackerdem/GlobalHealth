# Roles y permisos — GlobalHealth

Date: 2026-10-18 · Interviewed: Saúl Pérez (author) · Status: **draft — gate pendiente junto con dominio.md**
Every change inherits this matrix like it inherits the NFR budget: a story that contradicts a cell fixes the story
or this file **in the same PR** — never silently.
Fuente: product/prd.md (épicas E1–E6) + entrevista 2026-10-12/18. Las celdas "—" no se han entrevistado: preguntar
antes de asumir (la mayoría llegan con E3/E4).

## Roles
| Role | Who they are | How they arrive |
|---|---|---|
| paciente | dueño del expediente y de la cuenta | signup correo/contraseña o Google, con consentimiento expreso |
| profesional | médico/especialista que atiende al paciente | enlace revocable generado por el paciente (E3); sin registro |
| sistema (IA/OCR) | automatizaciones que leen el expediente | siempre a nombre de una sesión del paciente; cero retención del proveedor |

## Matriz roles × operaciones
✔ allowed · ✖ forbidden (dicho explícito) · — never came up (ask before assuming)

| Entity · operation | paciente | profesional | sistema (IA/OCR) | Notes |
|---|---|---|---|---|
| receta · crear (foto o a mano) | ✔ | — (E4: FR-016/17 son aportes, no recetas propias) | ✖ (solo prellena; el paciente confirma) | nada se guarda sin confirmación del paciente |
| receta · ver | ✔ (las propias) | ✔ vía enlace activo, según categorías del enlace (FR-014) | ✔ para leer/citar (E5) | |
| receta · corregir | ✔ (las propias) | ✖ | ✖ | rectificación ARCO |
| receta · eliminar/archivar | ✔ (las propias) | ✖ | ✖ | cancelación ARCO; arrastra foto/adjuntos |
| foto de receta · descargar | ✔ | — | ✖ | |
| expediente · exportar/borrar todo | ✔ (US-02) | ✖ | ✖ | |
| bitácora de accesos · ver | ✔ (US-03) | ✖ | ✖ | |
| enlace · crear/revocar | ✔ (E3) | ✖ | ✖ | revocación < 5 s (NFR-002) |

## Lo que cada rol explícitamente NO puede (sus palabras / PRD)
- El profesional no conserva acceso tras revocarse el enlace (O3) ni ve categorías no expuestas (FR-014).
- La IA no responde sin cita al expediente (FR-020) y su proveedor no retiene datos (NFR-005).
- Nadie más que el paciente captura, corrige o borra su expediente en v1.

## Pantallas / superficies por rol (feeds the prototype)
| Role | Sees | Main actions |
|---|---|---|
| paciente | Expediente (recetas), captura por foto, adjuntos, (futuro: enlaces, bitácora) | subir foto, confirmar lectura, corregir, archivar |
| profesional | resumen vía enlace, sin registro (E4) | ver, aportar (FR-016/17), preguntar a la IA |
