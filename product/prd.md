# PRD — Expediente personal de salud (nombre de trabajo)

Date: 2026-10-11 · Author: Saúl Pérez (author/owner) · Status: draft · Brief: product/brief.md

## 1. Context and goals
Un paciente que rota entre profesionales de salud no relacionados llega a cada consulta sin su historial completo;
cada profesional diagnostica sobre un fragmento (evidencia de primera mano: caso de Saúl Pérez, brief §Problem). El
producto es un expediente de salud propiedad del paciente: captura diagnósticos, recetas, resultados e historial
familiar; lo comparte con cada profesional mediante un enlace revocable, QR o PDF; y una capa de IA responde citando
el expediente y prepara la consulta proactivamente. v1 la usa un solo paciente real, con diseño multi-usuario y
privacidad primero (ADR D2), marco México LFPDPPP + NOM-024 (ADR D3).

Outcomes del brief: O1 historial completo recuperable · O2 profesional accede en <1 min · O3 revocación verificable ·
O4 IA cita o calla · O5 el profesional devuelve sin transcripción · O6 detección proactiva de huecos con fuente.

## 2. Functional requirements
| ID | As a … | The system shall … (observable) | Priority (M/S/C/W) | Outcome |
|---|---|---|---|---|
| FR-001 | paciente | crear una cuenta cuyos datos quedan aislados de cualquier otra cuenta | M | O1 |
| FR-002 | paciente | exportar el expediente completo en un formato portable y legible | M | O1 |
| FR-003 | paciente | eliminar la cuenta con borrado efectivo de todos sus datos | M | — |
| FR-004 | paciente | consultar la bitácora de accesos: qué enlace, cuándo y qué se consultó | M | O3 |
| FR-005 | paciente | registrar un diagnóstico con fecha, profesional y notas | M | O1 |
| FR-006 | paciente | registrar una receta/medicación con dosis y vigencia | M | O1 |
| FR-007 | paciente | adjuntar un documento (imagen o PDF: resultado, estudio, reporte) a un registro | M | O1 |
| FR-008 | paciente | registrar historial familiar (parentesco + condición) | M | O6 |
| FR-009 | paciente | buscar y recorrer el expediente por fecha, tipo o profesional | M | O1 |
| FR-010 | paciente | generar un enlace de acceso eligiendo tipo de profesional y nombre (un enlace por profesional) | M | O2 |
| FR-011 | paciente | mostrar el QR de un enlace para escaneo en consulta | M | O2 |
| FR-012 | paciente | activar/desactivar cada enlace individualmente, con efecto inmediato | M | O3 |
| FR-013 | paciente | generar un PDF de resumen del expediente para entrega directa | M | O2 |
| FR-014 | paciente | elegir qué categorías del expediente expone cada enlace (p.ej. salud mental solo a psiquiatra) | M | O3 |
| FR-015 | profesional | abrir un enlace activo y ver el resumen sin instalar nada ni registrarse | M | O2 |
| FR-016 | profesional | enviar un diagnóstico o nota por el enlace, que queda en el expediente marcado como aportado por él | M | O5 |
| FR-017 | profesional | enviar una petición de estudios o un anexo por el enlace | M | O5 |
| FR-018 | paciente | revisar y aceptar cada aporte de un profesional antes de integrarse al expediente | M | O5 |
| FR-019 | profesional | hacer preguntas en lenguaje natural sobre el expediente desde el enlace | M | O4 |
| FR-020 | paciente o profesional | recibir de la IA solo respuestas con cita a documentos del expediente; sin fuente, responde que no hay información | M | O4 |
| FR-021 | paciente | recibir avisos proactivos de huecos (p.ej. historial familiar de diabetes sin tamizaje registrado) con estudios y preguntas sugeridas para discutir con el profesional, cada una con fuente | M | O6 |
| FR-022 | paciente | recibir preguntas de la IA para completar registros incompletos | S | O6 |
| FR-023 | paciente | recibir sugerencia del tipo de especialista pertinente para discutir un hallazgo | S | O6 |
| FR-024 | paciente | ver su consumo de consultas de IA del periodo contra su límite | M | — |
| FR-025 | paciente | recibir un recordatorio en el horario de una toma registrada en una receta | M | — |
| FR-026 | paciente | registrarse e iniciar sesión con su cuenta de Google, además del alta con correo/contraseña | M | O1 |

## 3. Non-functional requirements (measurable; unknown → NEEDS CLARIFICATION)
| ID | Attribute | Stimulus → response → measure | Priority | Source |
|---|---|---|---|---|
| NFR-001 | security | acceso al almacenamiento sin credenciales de la app → datos de salud ilegibles → 100% de campos sensibles cifrados en reposo y en tránsito | M | ADR D2 |
| NFR-002 | security | paciente desactiva un enlace → siguiente intento de acceso rechazado → 100% de intentos, propagación < 5 s | M | O3 |
| NFR-003 | security | todo acceso vía enlace → registro en bitácora (enlace, timestamp, recurso) → 100%, sin excepción | M | ADR D2 |
| NFR-004 | compliance/privacy | alta de cuenta → consentimiento expreso para tratar datos sensibles registrado antes de capturar el primer dato → 100% (LFPDPPP); derechos ARCO ejecutables vía FR-002/FR-003; obligaciones NOM-024 aplicables a software personal no institucional: NEEDS CLARIFICATION (verificar fuente primaria) | M | ADR D3 |
| NFR-005 | compliance/privacy | consulta a la IA → ningún dato del expediente queda retenido ni se usa para entrenar modelos del proveedor → garantía contractual verificada; proveedor: NEEDS CLARIFICATION | M | ADR D2 |
| NFR-006 | data residency | ubicación de datos en reposo → NEEDS CLARIFICATION (¿México/EE.UU.? decide el technical brief con costo) | S | ADR D3 |
| NFR-007 | usability | profesional escanea QR o abre URL → resumen legible en pantalla → < 1 min, cero instalación, cero registro | M | O2 |
| NFR-008 | functional suitability (safety) | cualquier salida de la IA → lleva fuente verificable y leyenda de que no constituye consejo médico → 0 salidas sin fuente, 0 sin leyenda | M | ADR D5 |
| NFR-009 | performance efficiency | pregunta a la IA sobre el expediente → respuesta completa → p95 NEEDS CLARIFICATION (fijar en technical brief) | S | — |
| NFR-010 | reliability | pérdida del dispositivo del paciente → expediente recuperable íntegro en dispositivo nuevo → RPO NEEDS CLARIFICATION | M | O1 |
| NFR-011 | portability | paciente en móvil Android; profesional vía web en móvil y escritorio → ambas superficies funcionales | M | brief |
| NFR-012 | language/accessibility | toda UI y contenido → es-MX | M | brief |
| NFR-013 | hosting/operations | operación y costo sostenibles por una persona a tiempo parcial → presupuesto mensual y horas: NEEDS CLARIFICATION (technical brief) | M | brief |
| NFR-014 | maintainability | consumo de IA por usuario/periodo medible y consultable → 100% de consultas contadas (base del freemium) | M | ADR D5 |

## 4. Epics
### E1 — Cuenta y privacidad: el paciente es dueño verificable de sus datos
Covers: FR-001..004, FR-026, NFR-001, NFR-003, NFR-004, NFR-006, NFR-010 · Stories:
- US-01 As a paciente, I want crear mi cuenta (con Google o con correo) con consentimiento expreso, so that mis datos sensibles quedan aislados y bajo mi control.
- US-02 As a paciente, I want exportar y eliminar todo mi expediente, so that ejerzo mis derechos ARCO sin pedir permiso.
- US-03 As a paciente, I want ver la bitácora de accesos, so that sé quién vio qué y cuándo.

### E2 — Expediente: todo el historial en un lugar recuperable
Covers: FR-005..009, NFR-010, NFR-012 · Stories:
- US-04 As a paciente, I want registrar diagnósticos, recetas y adjuntar resultados, so that nada queda en papeles sueltos.
- US-05 As a paciente, I want registrar mi historial familiar, so that el riesgo hereditario (cáncer, diabetes) sea visible.
- US-06 As a paciente, I want buscar y recorrer mi historial, so that encuentro cualquier dato en consulta.

### E3 — Compartir con consentimiento: un enlace revocable por profesional
Covers: FR-010..014, NFR-002, NFR-007 · Stories:
- US-07 As a paciente, I want generar un enlace con tipo y nombre del profesional, so that cada médico tiene su acceso propio.
- US-08 As a paciente, I want QR y PDF de resumen, so that comparto en consulta en menos de un minuto.
- US-09 As a paciente, I want apagar un enlace al instante, so that nadie conserva acceso que ya no autorizo.

### E4 — Portal del profesional: ver, preguntar, devolver
Covers: FR-015..019, NFR-007 · Stories:
- US-10 As a profesional, I want abrir el enlace y ver el resumen sin registrarme, so that la consulta no pierde tiempo.
- US-11 As a profesional, I want devolver diagnóstico, órdenes y anexos, so that quedan en el expediente sin transcripción.
- US-12 As a profesional, I want preguntarle a la IA sobre el expediente, so that encuentro antecedentes sin leerlo todo.

### E5 — Capa IA: cita o calla, y prepara la consulta
Covers: FR-019..024, NFR-005, NFR-008, NFR-009, NFR-014 · Stories:
- US-13 As a paciente o profesional, I want respuestas solo con cita al expediente, so that ninguna alucinación entra al circuito clínico.
- US-14 As a paciente, I want avisos proactivos de huecos con estudios y preguntas sugeridas (con fuente), so that llego a la consulta adelantado y no espero a que el médico lo pida.
- US-15 As a paciente, I want ver mi consumo de consultas contra el límite, so that el freemium es transparente.

### E6 — Recordatorios mínimos de medicación
Covers: FR-025 · Stories:
- US-16 As a paciente, I want un recordatorio por cada toma de mis recetas activas, so that no pierdo adherencia al tratamiento.

## 5. Traceability
| Outcome | Epic | FR | NFR |
|---|---|---|---|
| O1 historial recuperable | E1, E2 | FR-001..002, FR-005..009, FR-026 | NFR-001, NFR-010, NFR-012 |
| O2 acceso < 1 min | E3, E4 | FR-010..011, FR-013, FR-015 | NFR-007 |
| O3 revocación verificable | E1, E3 | FR-004, FR-012, FR-014 | NFR-002, NFR-003 |
| O4 IA cita o calla | E4, E5 | FR-019..020 | NFR-005, NFR-008, NFR-009 |
| O5 devolución sin transcripción | E4 | FR-016..018 | NFR-007 |
| O6 detección proactiva | E2, E5 | FR-008, FR-021..023 | NFR-008 |
| (freemium) | E5 | FR-024 | NFR-014 |
| (adherencia) | E6 | FR-025 | — |

## 6. Out of scope and open questions
- Out (brief + ADR D4/D5): telemedicina/chat, ingesta de wearables (camino futuro: memory/research.md#wearables),
  citas/agenda, venta institucional, idiomas distintos de es-MX.
- Q1 RESUELTA (Saúl Pérez, 2026-10-11): FR-018 es **Must** — ningún aporte externo entra al expediente sin
  aprobación del dueño.
- Q2 RESUELTA (Saúl Pérez, 2026-10-11): FR-014 es **Must** — cada enlace expone solo las categorías que el
  paciente eligió.
- Q3 Residencia de datos (NFR-006) — la decide el technical brief con costo sobre la mesa.

## 7. Technology notes for the technical brief (not decisions)
- FR-019..023 implican recuperación sobre los documentos del expediente (RAG o contexto completo) + un corpus de
  guías clínicas con fecha para FR-021; la evidencia de partida vive en memory/research.md#comorbilidades y cada
  regla exige verificar la guía vigente antes de implementarse (ADR D5).
- NFR-005 restringe el proveedor de IA a uno con cero retención / no-training contractual.
- FR-010..012 implican URLs con token revocable server-side (la revocación <5 s descarta enlaces autocontenidos).
- FR-024/NFR-014 implican medición de uso por usuario desde v1 (el cobro llega después; la contabilidad, ahora).
- NFR-011 implica dos clientes (móvil Android + web) sobre una misma superficie de servicios.
- FR-002/FR-003 implican export e-borrado reales también en respaldos → condiciona la estrategia de backups (NFR-010).
- FR-026 implica OAuth/OIDC con Google como proveedor de identidad (solo identidad: ningún dato de salud se comparte
  con Google); el template trae auth JWT correo/contraseña, la integración del flujo social la decide el plan de E1.
  Nota: el consentimiento expreso (NFR-004) se recaba igual en ambos flujos de alta, el login social no lo sustituye.
