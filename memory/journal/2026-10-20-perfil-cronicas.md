# 2026-10-20 · perfil-cronicas (Story B de FR-028/US-18)

**Quién:** Saúl Pérez (author) aprobó el plan tras navegar el prototipo ("plan approved"); el agente orquestó
`/epe-3-execute` con un tester y un implementer por grupo.

**Intención:** que "Enfermedades crónicas" se llene como una sección más del historial: condición (lista frecuente,
salud mental y adicciones, "otra"), marca "Sensible" que decide el paciente, Activa / Ya no la tengo con desde y
hasta, tratamiento, nota y un diagnóstico del expediente que la respalda; al borrar ese diagnóstico, la crónica se
queda sin respaldo y el diálogo lo avisa (B-5, decisión de Saúl Pérez: "Se queda y se avisa").

**Qué se hizo:**
- **Base:** rebase sobre main tras #24 y #25; `openspec validate --strict` limpio.
- **Grupo 1, backend (test→impl):**
  - rojo b39f5d5: 45 fallos por comportamiento ausente;
  - verde 001f808: sección `chronic` en la tabla cifrada de la Story A, `sensitive` con valor por defecto del
    servidor, comparación desde/hasta por rango de edad, enlace solo a diagnósticos propios y
    `crud.unlink_diagnosis` en el DELETE del expediente;
  - cliente regenerado.
- **Grupo 2, frontend (test→impl):**
  - rojo 5a0664f: 13 fallos;
  - verde a8aecd8: formulario de crónica, etiqueta "sensible", "Respaldo", tarjeta enlazada y aviso en
    `DeleteRecord`.
- **Exploración en Chrome:** encontró un defecto (el error de "¿Cuál?" quedaba fuera de pantalla a 500 px). Se
  arregló en 64333d0 y se re-exploró.

**Verificación:**
- **Backend:** 240 passed, cobertura 96 %, mypy y ruff limpios.
- **e2e del cambio:** 103 passed en chromium y s26-ultra.
- **tsc y biome:** limpios.
- **`make tdd-check`:** ✓ en los dos grupos.
- **Suite e2e completa:** 3 corridas. Una limpia (167 passed); las otras dos tuvieron un fallo intermitente cada
  una, en `reset-password` y en `admin`, pruebas heredadas que no tocan este cambio.

**Deuda:**
- La inestabilidad heredada del e2e.
- H5: el formulario sigue sin RHF+zod.
- Un error de edad imposible con desde y hasta enviados va como alerta del formulario: la API no dice cuál campo
  falló.
- El aviso con varias crónicas («A», «B») no tiene prueba automática.
- El archivo (3.3) queda para el final del PR, después de la review o de que Saúl Pérez diga que no habrá.
