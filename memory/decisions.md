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

## D12 — Entorno de desarrollo: el que prescribe el template (Docker Compose + uv)
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner), al detectar el vacío antes de aprobar US-01
- **Decision:** el entorno local es el documentado por el propio template: **Docker Compose** para Postgres y el
  stack completo (con `watch` para hot reload) y **uv** como gestor de entorno virtual y dependencias de Python
  (el template migró de Poetry a uv en sept 2024 [VERIFIED: memory/research.md#stack]); Node para el frontend.
  Nada de Postgres instalado nativo ni venvs manuales. T1 de `cuenta-consentimiento` lo confirma empíricamente
  contra el development.md oficial y actualiza este ADR si difiere.
- **Why:** mantener el entorno que el template mantiene es cero fricción de upgrade y cero documentación propia;
  un entorno custom diverge en el primer update. Detectado por Saúl Pérez: ni el technical brief ni el harness
  tenían un paso explícito de entorno de desarrollo (→ meta-mejora propuesta).
- **Discarded:** Postgres nativo en la máquina (drift entre sesiones/máquinas); pip/poetry manual (el template ya
  no lo usa).

## D13 — Cifrado app-level: Fernet/MultiFernet vía EncryptedString, claves por propósito
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner), al aprobar la revisión adversaria de
  `cuenta-consentimiento` (/epe-4-review → /epe-5-apply)
- **Decision:** el cifrado de datos sensibles en reposo (NFR-001) es app-level con **Fernet** (simétrico,
  autenticado) a través del TypeDecorator `EncryptedString` (`backend/app/core/encrypted.py`), aplicado hoy a
  `OAuthIdentity.subject` y `HealthRecordStub.note`. Derivación de claves **por propósito** desde el mismo
  material: la clave de datos es `ENCRYPTION_KEY` tal cual (o, solo en dev, derivada determinista de `SECRET_KEY`)
  y la de la cookie PKCE se deriva con tag (`sha256(key material + b"pkce")`), de modo que comprometer una no
  expone la otra. **`ENCRYPTION_KEY` es obligatoria fuera de development** (el arranque falla sin ella; en dev solo
  advierte, mismo mecanismo que el enforcement de `SECRET_KEY` del template). Rotación: `ENCRYPTION_KEY_PREVIOUS`
  se añade como clave solo-descifrado (**MultiFernet**) mientras se re-cifra el dato existente; después se retira.
- **Why:** Fernet ya viene con `cryptography` (dependencia del template), es autenticado (tampering → token
  inválido, no plaintext corrupto) y MultiFernet da rotación sin migración big-bang. La separación por propósito y
  la obligatoriedad en prod salieron de los hallazgos aprobados de la revisión (clave única para cookie y datos +
  fallback silencioso a SECRET_KEY eran riesgo).
- **Discarded:** cifrado at-rest de Postgres/disco (no protege ante acceso SQL con credenciales); pgcrypto (ata el
  cifrado al motor y mete la clave en el SQL/logs); una sola Fernet para cookie y datos (el estado anterior).
- **Consequence:** columnas cifradas no se filtran por valor en SQL (comparar tras descifrar); E2+ usa
  `EncryptedString` para todo campo clínico; los deploys definen `ENCRYPTION_KEY` dedicada (urlsafe base64, 32
  bytes) y rotan con `ENCRYPTION_KEY_PREVIOUS`.

## D14 — BD de prueba efímera en Docker; pytest se niega a correr contra otra cosa
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner), a pedido directo. Extiende D12.
- **Decision:** servicio `db-test` en `compose.override.yml` (postgres:18, **tmpfs**, base `app_test`, host
  5433) solo para dev/CI: el stack de deploy (`compose.yml + compose.deploy.yml`) nunca lo levanta. La suite
  backend resuelve `TEST_DATABASE_URL` (entorno > `.env` raíz; vacía explícita = desactivada), **aborta** si
  falta o si el nombre de base no termina en `_test`, exporta `DATABASE_URL` antes de importar `app.*` y corre
  `alembic upgrade head` por sesión (la BD parte vacía en cada arranque del contenedor). Migraciones fuera del
  gate de cobertura (`omit = ["app/alembic/*"]`: DDL, no lógica).
- **Why:** el conftest del template corre contra la BD de desarrollo y su teardown borra User/Item: borró dos
  veces datos reales de Saúl (auth.setup 400 en Playwright; el usuario Google + consentimiento de la
  re-verificación manual). La guarda en conftest cubre también `uv run pytest` directo, que fue el camino real
  de los incidentes; un wrapper solo protege a quien lo usa.
- **Discarded:** segunda base `app_test` dentro del contenedor `db` (comparte ciclo de vida y volumen con datos
  reales; Saúl pidió contenedor aparte); redirección en scripts en vez de conftest (no cubre pytest directo);
  volumen persistente para db-test (la efimeridad ES la garantía de partir limpio).
- **Consequence:** correr pruebas exige `docker compose up -d --wait db-test` una vez por sesión de trabajo;
  dos corridas de pytest simultáneas siguen compartiendo db-test (paralelismo por-worker queda fuera, se decide
  si duele); Playwright sigue sobre el stack real de desarrollo.

## D15 — Localización: react-i18next con es-MX como único locale embarcado
- **Status:** Accepted · 2026-10-12 · decided by: Saúl Pérez (author/owner), a pedido directo ("prefiero el
  paquete de React"). Cubre NFR-012.
- **Decision:** react-i18next + i18next (pins exactos) con `es-MX` único, recursos estáticos en 7 namespaces por
  dominio (`frontend/src/locales/es-MX/`), sin selector de idioma ni detección de locale. El backend NO usa
  biblioteca i18n: `detail=`/`message=` visibles y asuntos de correo son strings es-MX directos; los correos
  transaccionales se redactan en las plantillas React Email y se regeneran con `bun run export`. Los códigos de
  máquina (p. ej. `CONSENT_REQUIRED`) no se traducen. El chrome de UI del gate de consentimiento se mueve a
  recursos byte a byte; el texto legal sigue sirviéndose desde el backend (consent_text.py) y no se toca.
- **Why:** un solo locale con infraestructura lista para el segundo (añadir JSON + selector, con recarga; el
  cambio de idioma en caliente exigiría mover los `i18n.t` de module scope a render-time) sin pagar hoy
  gettext/babel en el backend; la suite Playwright con textos es-MX queda como contrato del idioma (177+
  aserciones), que es donde se rompería una regresión.
- **Discarded:** traducción directa sin biblioteca (decisión explícita de Saúl en contra, inbox 2026-10-12);
  i18n también en backend (cero variación de locale no lo justifica); claves = texto inglés (ata los recursos a
  la redacción vieja).
- **Consequence:** todo string nuevo de UI nace en `locales/es-MX/<ns>.json` y se consume con `t()`; los tests
  E2E asiertan el texto es-MX exacto del recurso; `components/ui/` (shadcn) queda fuera del barrido por no tener
  texto propio.
