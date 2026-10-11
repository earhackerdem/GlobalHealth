# Project decisions (lightweight ADR)

States: Accepted · Revised · Proposed · Discarded. Never deleted; when they change, mark them Revised with a date and
link the new one. Order: from most structural to most tactical.

## D1 — Origin, owner and identity of the project
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez
- **Decision:** "sandbox" is born from the mother template `harness` (flavor **development**). Owner: **Saúl Pérez**. Author:
  Saúl Pérez (earhackerdem@gmail.com), which is this repo's local git identity.
- **Why:** the harness brings memory in the repo, an EPE cycle with a human gate, profiles and deterministic hooks
  already measured in two projects; what is specific to this project is decided here, not in the template.
- **Consequence:** `harness.json` → `code` marks which paths require an approved plan; adjust it in the first change.

## D2 — Privacidad primero y diseño multi-usuario desde v1
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** la v1 del expediente personal de salud la usa solo Saúl, pero el modelo de datos, el aislamiento
  por usuario, el consentimiento y la revocación de accesos compartidos se diseñan multi-usuario y con los datos de
  salud tratados como sensibles desde el primer commit.
- **Why:** el objetivo declarado es una app pública freemium; añadir privacidad después de hacerla pública implica
  reescritura. Saúl lo pidió explícitamente: "demos prioridad a la privacidad para evitar reescrituras".
- **Consequence:** toda exploración de cambio hereda esta restricción; el technical brief la convierte en
  presupuesto NFR medible (cifrado, revocación, auditoría de accesos).

## D3 — Marco de privacidad de referencia: México (LFPDPPP + NOM-024-SSA3)
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** el diseño toma como referencia la ley mexicana: datos de salud = datos personales sensibles
  (consentimiento expreso, derechos ARCO) y la NOM-024-SSA3 como referencia de registros electrónicos de salud.
- **Why:** Saúl y sus profesionales de salud están en México; es el marco exigible en v1. GDPR/HIPAA se evaluará
  si el freemium sale de México (quedó como opción descartada por ahora, no para siempre).
- **Consequence:** los requisitos concretos (qué exige cada norma al software) se verifican con fuente primaria en
  la exploración del primer cambio que toque datos; nada se afirma de memoria.

## D4 — Fuera de v1: telemedicina y wearables; PRD sí
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** v1 excluye telemedicina/chat y la ingesta de wearables (camino futuro documentado en
  memory/research.md#wearables; fallback: importar reportes PDF del fabricante). Se escribirá PRD porque hay más de
  una épica que no debe divergir sobre el mismo modelo de consentimiento.
- **Why:** equipo de una persona a tiempo parcial; el núcleo es expediente + compartir con revocación + IA citante.
- **Consequence:** siguiente paso `/product-prd`, luego `/product-tech-brief`. Citas y recordatorios quedan como
  pregunta abierta Q1 del brief, no excluidos de forma permanente. *(Q1 resuelta en D5.)*

## D5 — Respuestas a las preguntas abiertas del brief
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** (1) recordatorios de medicación mínimos entran en v1, citas/agenda no; (2) acceso del profesional
  solo por control de enlace: un enlace por profesional (tipo + nombre), revocable individualmente, sin verificación
  por teléfono/correo; (3) la IA también atiende al paciente de forma proactiva — pregunta para completar el
  expediente y sugiere estudios/especialista a partir de huecos (incl. historial familiar de cáncer y diabetes) —
  con encuadre "preparación de consulta": toda sugerencia lleva fuente y se formula para discutir con el
  profesional, nunca como prescripción; (4) freemium = gratis con límite de consultas de IA.
- **Why:** motivación directa de Saúl: historial familiar de cáncer y diabetes; quiere que el paciente llegue con
  los estudios conversados proactivamente y no espere a que el médico los pida. El encuadre no-prescriptivo fue la
  objeción del agente (riesgo de recomendación clínica / COFEPRIS y daño por alucinación); Saúl puede revertirlo y
  quedaría registrado aquí como Revised.
- **Consequence:** la evidencia de comorbilidades que alimenta las sugerencias vive en
  memory/research.md#comorbilidades con su nivel de confianza; cada regla de sugerencia exige verificar la guía
  clínica vigente antes de implementarse (nunca desde memoria del modelo).

## D6 — Stack v1: monolito Laravel + Postgres(pgvector) + Claude API tras AiGateway
- **Status:** Revised · 2026-10-11 → ver D11 · decided by: Saúl Pérez (author/owner), recomendación del technical brief
- **Decision:** v1 es un monolito Laravel 12 con PostgreSQL (pgvector para recuperación) y la capa IA como
  llamadas directas a Claude API encapsuladas en una interfaz interna propia (`AiGateway`).
- **Why:** el equipo es una persona fluida en Laravel; el código más delicado (consentimiento, revocación,
  cifrado) se escribe en el framework que domina. Tecnología aburrida gana.
- **Discarded:** (B) template full-stack FastAPI — apila dos aprendizajes (Python reciente + React) sobre el núcleo
  de privacidad; (C) sidecar FastAPI desde v1 — dos deploys para una persona. C queda como evolución: si el
  procesado de documentos/OCR lo exige, el sidecar se añade detrás de AiGateway sin rediseño.

## D7 — Cliente: web responsive + Android por Capacitor
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** paciente y profesional usan la misma web responsive; la app Android de v1 es un shell Capacitor
  (notificaciones locales para FR-025, cámara para FR-007, vía futura a Health Connect por plugin/módulo nativo).
- **Why:** Saúl no tiene experiencia Android y está abierto a alternativas; Kotlin nativo son meses de curva sin
  beneficio en los FR de v1.
- **Discarded:** Kotlin nativo en v1 (se revisita si Health Connect lo exige al integrar wearables); PWA pura
  (recordatorios de medicación menos fiables que notificaciones locales nativas).

## D8 — Hosting: PaaS conocido, región US + aviso de transferencia
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** v1 corre en un PaaS que Saúl ya opera (Railway o Render; se fija en el primer cambio) con Postgres
  administrado, región US, declarando la transferencia internacional en el aviso de privacidad.
- **Why:** NFR-013 (≤2 h ops/mes para una persona); la LFPDPPP permite transferencia con consentimiento (art. 9,
  36/37 — texto vigente por verificar: NFR-006).
- **Discarded:** VPS propio (más ops); región MX obligatoria (solo si la verificación legal de NFR-006 lo exige).

## D9 — Proveedor IA: Claude API
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** la capa IA usa Claude API (claude-sonnet-5-5 para Q&A y preparación de consulta; claude-haiku-5-5
  para tareas baratas), detrás de AiGateway.
- **Why:** no entrena con contenido de clientes API por defecto [fuentes secundarias coincidentes, 2026-10-11];
  calidad en cita/grounding requerida por NFR-011.
- **Consequence:** NFR-005 obliga a verificar retención (7 vs 30 días en fuentes) y ZDR en Commercial Terms/DPA
  oficiales, con captura fechada en memory/research.md, ANTES del primer dato real en el sistema.

## D10 — (Revised el mismo día → D11) variante Laravel core + FastAPI portal/IA
- **Status:** Revised · 2026-10-11 → ver D11 · decided by: Saúl Pérez (author/owner)
- **Decision:** variante intermedia donde Laravel era dueño de datos y FastAPI servía portal médico + IA vía API
  interna. Vivió una ronda de conversación: Saúl aclaró que su preferencia es no usar Laravel en absoluto.

## D11 — Stack final: monolito full-stack FastAPI, sin Laravel
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner), reafirmado tras objeción del agente
- **Decision:** el producto es UN monolito sobre el template oficial full-stack FastAPI
  (github.com/fastapi/full-stack-fastapi-template: backend/ FastAPI+SQLModel+Postgres+Alembic, frontend/ React/TS).
  Ese mismo proyecto sirve la web del personal médico, la gestión del paciente (subir recetas/estudios, ver lo que
  ven sus médicos, activar/desactivar URLs) y la capa IA (async nativo). La app Android es un shell Capacitor sobre
  el frontend del template (ajuste a D7). Microservicio de IA = contingencia: FastAPI sin template, solo si una
  razón concreta lo exige; en ese caso evaluar gestión por variables en BD en lugar de env/secrets. La capa IA vive
  tras una interfaz interna (AiGateway) para que la extracción, si llega, no sea rediseño.
- **Why:** preferencia explícita de Saúl Pérez por razones de mercado (empleabilidad Python/FastAPI): "prefiero no
  usar Laravel". La objeción del agente (aprender Python+React sobre el núcleo de privacidad; recomendaba Laravel
  por fluidez) fue oída y descartada por él — costo aceptado conscientemente, mitigado por 20+ h/semana y por lo que
  el template ya trae resuelto (authn, CI, pytest, Playwright).
- **Discarded:** monolito Laravel (D6); Laravel core + FastAPI portal (D10); Kotlin nativo (sigue descartado, D7).
- **Consequence:** harness.json → code: backend/, frontend/; tests: backend/app/tests/, frontend/tests/;
  blocked_commands: alembic downgrade, docker compose down -v. Todo plan debe decir cómo el monolito cumple los NFR
  que toca (budget §4 del technical brief).
