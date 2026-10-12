# 2026-10-12 — ui-es-mx-i18next: toda la UI en es-MX con react-i18next

- Saúl Pérez decidió react-i18next sobre traducción directa y aprobó el plan el mismo día ("plan approved");
  Storybook/Atomic quedó en inbox con objeción anotada, sin reafirmar.
- Medido antes de planear: 177 aserciones de texto en Playwright = el costo dominante; acople transversal
  verificado (detail del backend asertado por Playwright; asuntos de correo leídos de Mailpit).
- 4 grupos: infra (agente autor produjo 203 claves/7 namespaces como CONTRATO antes del tester), pantallas
  (rojo estructural: auth.setup bloquea 61; verde 62/62 con 34 archivos cableados), backend+correos (rojo 28+6;
  verde 104/0/0, 93.69%, 62/62 leyendo el correo real de Mailpit), cierre.
- El tester del grupo 3 encontró un hueco real del contrato (message= de éxito): se extendió el contrato antes
  de migrar, no se improvisó traducción en el test.
- El implementer del grupo 2 agotó sus 40 turnos a la mitad; se continuó con SendMessage sin relanzar (contexto
  intacto). ADR D15. Grep de remanentes: 1 console.warn no visible, 0 strings de UI.
- Deuda: "Test email sent" en routes/utils.py (sin test), span de énfasis perdido en paginación del DataTable,
  baseURL default de playwright.config apunta al dev server; fila es-MX del inbox se cierra tras el merge (hay
  ediciones del inbox en vuelo en el PR #3).
