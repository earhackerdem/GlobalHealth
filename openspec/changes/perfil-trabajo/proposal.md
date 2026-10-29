# Proposal

Origin: product/prd.md § E2 — US-18 (FR-028) · dominio: product/dominio.md § Trabajo y § Rebanada (Story C: C2b,
"Trabajo" en el Perfil básico, C-9) · prototipo de producto: `product/prototipos/perfil-secciones.html` (C-9,
`:274-297`) · investigación: `memory/research/ocupacion.md#ocupacion`
Triage: change — toca `code` (backend y frontend) y agrega un requisito a la spec `records/patient-profile`. Es la
segunda mitad de la C2, que Saúl Pérez partió el 2026-10-26; va antes de la mascota (D23) y de las deudas, por su
orden del 2026-10-29.

## Why

Las plantillas mexicanas de historia clínica preguntan la ocupación en la ficha de identificación, y NIOSH define el
mínimo para un expediente: situación laboral, trabajo actual y el de más años (`memory/research/ocupacion.md`). En la
ronda 7 del dominio Saúl Pérez lo pidió así: «también te preguntan por tu profesión… hay oficios que implican
movimiento diario». Hoy el Perfil básico solo tiene fecha de nacimiento, sexo, alergias, peso y estatura.

## User story

Como paciente, quiero contar a qué me dedico, a qué me expongo en mi trabajo y en qué turno, para que el médico lo
tome en cuenta sin tener que preguntármelo en cada consulta.

## Acceptance criteria (los Given/When/Then con datos concretos van en la spec delta)

- **C-9 Trabajo en el Perfil básico:** situación laboral, una sola (trabajo · busco trabajo · jubilado o pensionado ·
  hogar · estudio · no puedo trabajar por mi salud), y el trabajo de más años si es otro (texto libre). Solo con
  «Trabajo»: a qué te dedicas (texto libre), exposiciones (polvo · químicos o solventes · ruido fuerte, varias, o «Nada
  de esto») y turno (de día · de noche · rotativo). Se edita en su propio diálogo desde la tarjeta Datos básicos
  (respuestas de Saúl Pérez, 2026-10-29, `exploration.md` § 5).
  - **T-1:** guardo «Trabajo», «Chofer de transporte», exposiciones «Ruido fuerte» y turno «Rotativo»; la tarjeta
    Datos básicos muestra «Chofer de transporte · rotativo · expuesto a ruido fuerte».
  - **T-2:** todo es opcional: guardar el bloque vacío es válido y la tarjeta dice «Sin registrar».
  - **T-3:** «Nada de esto» y una exposición se excluyen: elegir una quita la otra.
  - **T-4:** jubilado con «Minero» como el trabajo de más años: la tarjeta muestra «Jubilado o pensionado · antes: Minero»; no se le
    pregunta a qué se dedica, exposiciones ni turno.
  - **T-6:** cambio de «Trabajo» a «Busco trabajo» y guardo: lo que solo aplica al trabajo (a qué se dedica,
    exposiciones, turno) se borra.
  - **T-5:** los datos van cifrados en reposo, solo los ve su dueño y piden consentimiento vigente.
- La app no califica nada de esto (no hay «riesgo laboral» calculado; C-6, NFR-008).

## What Changes

- El perfil suma un bloque «Trabajo» (cerrado y cifrado, como los hábitos) y su ruta.
- La tarjeta Datos básicos de «Mi perfil médico» lo muestra y abre su edición.

## Capabilities

### New Capabilities
Ninguna.

### Modified Capabilities
- `records/patient-profile`: requisito nuevo "Trabajo en el perfil básico".

## Impact

- **Backend:** `backend/app/models.py` (esquema cerrado del trabajo), `backend/app/api/routes/profile.py` (ruta),
  migración de una columna cifrada.
- **Frontend:** `frontend/src/routes/_layout/perfil.tsx` (tarjeta), un componente de edición, textos es-MX en
  `profile.json`, cliente regenerado.
- **Fuera:** codificar la ocupación con el catálogo de NIOSH; la mascota y sus «¿Por qué lo pedimos?» (D23, después);
  el trabajo en el asistente de bienvenida (FR-027 no lo incluye).
