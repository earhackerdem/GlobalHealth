# 2026-10-19 · onboarding-perfil (discovery)

**Quién:** Saúl Pérez (author) pidió arrancar la SIGUIENTE TAREA que dejó encargada al cerrar receta-mexicana
("procede con el onboarding"); el harness ejecutó la rebanada de discovery.

**Intención:** onboarding de perfil del paciente justo después de aceptar el consentimiento — fecha de nacimiento,
peso actual, estatura y antecedentes médicos familiares ("lo que preguntan mucho los médicos: diabetes o cáncer en
la familia"). Encaje acordado: rebanada de discovery → FR nuevo en el PRD → story con prototipo.

**Qué se hizo:**
- Verificado en el texto oficial (PDF DOF) que NOM-004-SSA3-2012 **6.1.1** exige en el interrogatorio la ficha de
  identificación y los antecedentes heredo-familiares/APP/APNP, y **6.1.2** peso y talla en la exploración física
  → memory/research.md (los campos pedidos son el mínimo que la norma obliga al médico a preguntar).
- Nueva rebanada en `product/dominio.md`: catálogos Perfil del paciente y Antecedente familiar (AHF), glosario,
  procesos, estados del onboarding (ofrecido → completado | omitido, una sola vez), encaje LFPDPPP art. 3-VI
  (AHF = datos de salud de terceros aportados por el titular), encaje en el PRD (FR-008/US-05 ya existen; FR-027
  borrador para el perfil post-consentimiento) y **4 preguntas abiertas** como gate.
- Prototipo navegable `product/prototipos/onboarding-perfil.html` (patrón de receta-primero.html): wizard de 3
  pasos omitible, edad calculada, peso/estatura con fecha de medición, AHF por condición + parentescos, propuestas
  del harness visibles (sexo con "prefiero no decir", alergias a medicamentos), historia borrador y AC-1…AC-8 con
  el toggle "Ver criterios".
- Propuestas del harness más allá del pedido literal (regla del discovery: no aceptar la primera simplificación):
  peso/estatura como **medición con fecha** (no valor que se sobreescribe), AHF estructurado (checklist +
  parentescos, no texto libre — FR-021 lo necesita), sexo y alergias como candidatos a recortar.

**Verificación:** prototipo abierto localmente (flujo completo: llenar, omitir, guardar, editar); dominio.md y
research.md citan fuente y fecha; PR de discovery creado (precedente de rama: docs/discovery-* como PRs #11/#12).

**Gate abierto:** Saúl valida el prototipo clickeando y responde las 4 preguntas (peso como medición, forma de
capturar AHF, todo omitible, ¿entran sexo y alergias?). Con el gate cerrado: FR-027 al PRD y
`make epe-new SLUG=onboarding-perfil`.

**Deuda:** ninguna nueva; la captura foto/OCR y el resto del inbox siguen donde estaban.
