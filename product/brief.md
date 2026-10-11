# Product brief — Expediente personal de salud (nombre de trabajo)

Date: 2026-10-11 · Author: Saúl Pérez (author/owner) · Status: draft

## Problem
Un paciente que rota entre profesionales de salud no relacionados entre sí (médico general, urólogo, psicólogo,
psiquiatra, fisioterapeuta) llega a cada consulta sin su historial completo: cada profesional ve un fragmento y
diagnostica sobre él. Evidencia de primera mano [caso de Saúl Pérez, relatado 2026-10-11]: ansiedad diagnosticada en
enero 2026 con síntomas reconocibles desde ~los 12 años; colitis aguda cuyos efectos sobre órganos vecinos se trató
repetidamente como infección de vías urinarias (ampicilina en varias ocasiones), con un médico asumiendo causa de
transmisión sexual por falta de contexto. Con el historial a la vista, la ansiedad, la colitis y el inicio del
alcoholismo se habrían conectado antes. Que esto generalice a otros pacientes es **[ASSUMPTION]** (sin verificar aún).

## Audience
- **Paciente dueño del expediente** (en v1: solo Saúl; el diseño es multi-usuario desde el día uno).
- **Personal de salud invitado por el paciente**: recibe el resumen, consulta/pregunta, devuelve diagnóstico,
  órdenes de estudios y anexos. No instala nada.
- Fuera: instituciones (clínicas/hospitales) como cliente; cuidadores/familiares.

## Outcomes (medibles, v1)
- O1 — El 100% del historial descrito (diagnósticos, recetas, resultados, tratamientos: ansiedad, colitis,
  litiasis, prostatitis, hígado graso, cursos de ampicilina, asistencia a AA) está cargado y recuperable por búsqueda.
- O2 — En consulta real, el profesional accede al resumen relevante (QR, PDF o URL) en <1 minuto, sin que el
  paciente relate de memoria.
- O3 — Todo acceso compartido es revocable: un URL desactivado por el paciente queda inaccesible, verificado en el
  100% de los intentos posteriores.
- O4 — La IA responde preguntas del profesional citando únicamente documentos del expediente, con la fuente
  adjunta; cero respuestas sin cita.
- O5 — Un profesional puede devolver diagnóstico/órdenes/anexos por el enlace compartido y quedan en el expediente
  sin transcripción manual del paciente.
- O6 — La IA detecta huecos proactivamente (p.ej. historial familiar de diabetes/cáncer sin tamizaje registrado) y
  propone al paciente preguntas y estudios **para plantear al profesional**, cada sugerencia con su fuente
  (guía clínica vigente o documento del expediente); cero sugerencias sin fuente. Nunca prescribe ni diagnostica.

## Constraints
- **Privacidad primero** (decisión de Saúl Pérez, 2026-10-11 → ADR D2): datos de salud tratados como sensibles
  desde v1 — aislamiento por usuario, consentimiento y revocación se diseñan ahora, aunque v1 tenga un solo usuario.
- **Marco de referencia:** México — LFPDPPP (datos de salud = sensibles, consentimiento expreso, derechos ARCO) +
  NOM-024-SSA3 como referencia de registros electrónicos (→ ADR D3).
- Plataforma: paciente en Android; personal de salud vía web, sin instalación.
- Equipo: Saúl Pérez en solitario, tiempo parcial → alcance implacable (ver technical brief).
- Idioma: es-MX. Futuro freemium: nada en v1 puede impedir multi-tenant ni cobro.

## Out of scope (v1, explícito a pedido de Saúl Pérez 2026-10-11)
- **Telemedicina / chat en tiempo real** con el profesional.
- **Ingesta de wearables/sensores.** Camino futuro investigado (memory/research.md#wearables): Health Connect en
  Android es la vía abierta (Galaxy Watch → Samsung Health → Health Connect); API legacy de Fitbit en deprecación
  desde sept 2026 hacia Google Health APIs; Garmin requiere aprobación de partner [NOT VERIFIED]. Fallback siempre
  disponible: importar los reportes PDF del fabricante como documentos del expediente.
- Venta institucional (clínicas/hospitales).

## Resolved questions (Saúl Pérez, 2026-10-11 → ADR D5)
1. Recordatorios de medicación **mínimos sí** en v1; citas/agenda fuera.
2. Identidad del profesional: **solo control del enlace** — un enlace por profesional (se genera eligiendo tipo de
   profesional + nombre), activable/desactivable individualmente. Sin verificación por teléfono/correo.
3. La IA **también atiende al paciente**, con encuadre "preparación de consulta": detecta huecos (historial
   familiar de cáncer y diabetes incluido), hace preguntas para completar el expediente y sugiere estudios y tipo de
   especialista *para discutir con el profesional* — nunca prescribe (objeción registrada: sugerencia directa =
   recomendación clínica/COFEPRIS; Saúl puede revertir el encuadre y quedaría registrado).
4. Freemium: **gratis con límites de consulta a la IA**; el pago quita límites. v1 solo debe dejar contable el uso.

## Next step
PRD needed? **Sí**: aunque decide una sola persona, hay más de una épica que no debe divergir (expediente,
compartir/consentimiento, portal del profesional, capa IA) y las cuatro cuelgan del mismo modelo de datos y
consentimiento. → `/product-prd`, luego `/product-tech-brief` (stack y presupuesto NFR de privacidad).
