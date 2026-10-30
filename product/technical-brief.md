# Technical brief — Expediente personal de salud

Date: 2026-10-11 · Author: Saúl Pérez (author/owner) · Status: draft · Source: product/prd.md

## 1. Team and existing stack (answered first, verbatim)
| Question | Answer |
|---|---|
| Team (size, seniority, maintainer) | Saúl Pérez en solitario; programador fullstack; 20+ h/semana, v1 en semanas |
| Languages / frameworks in use today | Fluido: fullstack Laravel (PHP). Java hace tiempo. Python reciente. Sin experiencia Android (tocó Android Studio) |
| Databases / hosting / CI in use today | Opera PaaS hoy (Railway/Fly.io/Render/Vercel). CI no declarado |
| Fluency and preferences | Propuso FastAPI (template full-stack de tiangolo) para la capa IA; abierto a alternativas en el cliente móvil |
| Budget, deadline, licensing, compliance | Sin techo estricto de gasto; sin licencias restrictivas; compliance: México LFPDPPP + NOM-024 (ADR D3) |
| Existing codebase to live in or integrate with | none (greenfield) |

**Verdict:** no hay stack de producto existente, pero la fluidez del equipo (una persona) ES la restricción:
candidatos abajo, sesgo a tecnología aburrida que Saúl ya domina.

## 2. Where the requirements strain the existing stack
No aplica (greenfield); las tensiones aparecen por candidato en §3.

## 3. Candidate stacks
| Option | Buys | Costs | Maturity / hiring | Hosting fit | NFRs met / at risk | Sources |
|---|---|---|---|---|---|---|
| **A (recomendación del agente, descartada por Saúl → D11): monolito Laravel 12 + PostgreSQL (pgvector) + Claude API directa; web responsive para paciente y profesional; app Android = shell Capacitor sobre la misma web** | Máxima fluidez (el núcleo privacidad/consentimiento se construye en el framework que domina); un solo deploy; cifrado, authn/z, colas y notificaciones resueltos por el ecosistema Laravel [OPINION fundada en fluidez declarada] | La capa IA se orquesta en PHP (llamadas HTTP al proveedor + pgvector): ecosistema de tooling IA más delgado que Python; OCR/procesado pesado de documentos quedaría para un sidecar futuro | Laravel y Postgres: aburridos y masivos; Capacitor: maduro, comunidad grande [OPINION] | Railway/Render corren Laravel+Postgres administrado (PaaS que ya opera) | Cumple NFR-013 (una persona), NFR-001/002 (revocación server-side trivial en monolito). Riesgo: NFR-009 si el procesado de PDFs crece → sidecar | fluidez: §1; template no requerido |
| **B (ELEGIDA, ADR D11)**: fastapi/full-stack-fastapi-template (FastAPI + SQLModel + Postgres + React/TS + Docker + Traefik + GH Actions) | Un solo backend en el lenguaje del ecosistema IA; cliente OpenAPI autogenerado; template oficial mantenido (snapshot feb 2026) [VERIFIED: github.com/fastapi/full-stack-fastapi-template · 2026-10-11] | Python «reciente» + React probablemente nuevo: aprender dos capas mientras se construye el núcleo de privacidad; Traefik/Compose = más ops que un PaaS git-push | FastAPI: maduro, enorme adopción [VERIFIED mismo repo] | Dockerizado corre en Railway/Fly | Riesgo NFR-013 (curva + ops) en las semanas objetivo | ídem |
| C: Laravel núcleo + sidecar FastAPI para IA (idea original de Saúl) | Cada herramienta en lo suyo; Python disponible para RAG/OCR desde el día 1 | Dos servicios: dos deploys, dos superficies de secretos, contrato interno que mantener — el costo operativo más alto para una persona | ambos maduros | PaaS corre ambos (más caro) | Riesgo NFR-013; NFR-005 igual en los tres (el proveedor es el mismo) | — |

**Recommendation and what would change it:** el brief recomendó **A** (monolito Laravel). Saúl Pérez, tras oír la
objeción (dos aprendizajes sobre el núcleo de privacidad), decidió lo contrario y es su decisión registrada
(ADR D11; D6 y D10 → Revised): **prefiere no usar Laravel; todo en FastAPI por razones de mercado**. Decisión final:
- **Monolito = template oficial full-stack FastAPI** (`backend/` FastAPI + SQLModel + Postgres + Alembic;
  `frontend/` React/TS + Vite [VERIFIED: github.com/fastapi/full-stack-fastapi-template · 2026-10-11]). Un solo
  proyecto sirve: la web del personal médico (vistas de enlace compartido, Q&A, devolución de aportes), la gestión
  del paciente (subir recetas/estudios, ver lo que ven sus médicos, activar/desactivar sus URLs) y la **capa IA**
  (async nativo de FastAPI para llamadas al proveedor). Dueño único de datos, revocación y bitácora: el mismo backend.
- **Microservicio de IA: contingencia, no punto de partida.** Si una razón concreta lo exige (aislar consumo/latencia,
  dependencias pesadas de procesado de documentos), se extrae a un FastAPI aparte SIN template (no necesita front);
  valdría añadirle gestión por variables en BD (no env/secrets) si se quiere operar sin redeploy — lo decide el plan
  de ese cambio. Mientras tanto, la capa IA vive detrás de una interfaz interna (`AiGateway`) para que la extracción
  no sea rediseño.
- **Cliente Android (D24, 2026-10-29; revisa D7):** app nativa en Kotlin + Jetpack Compose en `android/`, contra la misma
  API; v1 «hardware primero» (cuenta, cámara para FR-007, recordatorios de FR-025, ver el perfil). iPhone nativo en
  Swift después.
- Costo aceptado conscientemente: Python reciente + React probablemente nuevo mientras se construye el núcleo de
  consentimiento/privacidad; mitigación: 20+ h/semana, el template trae authn, CI, pytest y Playwright resueltos.
**Cliente móvil (texto de 2026-10-11, revisado por D24 el 2026-10-29: app nativa en Kotlin + Compose, no Capacitor):** web responsive primero y la app Android como shell Capacitor (notificaciones locales nativas
para FR-025, cámara para FR-007, y vía futura a Health Connect por plugin/módulo nativo cuando los wearables entren;
memory/research.md#wearables). Kotlin nativo descartado para v1: meses de curva sin beneficio en los FR de v1
[OPINION]; se revisita si Health Connect lo exige.
**Proveedor IA:** Claude API (Anthropic): no entrena con contenido de clientes API por defecto [VERIFIED, fuentes
secundarias coincidentes · 2026-10-11 — confirmar en Commercial Terms oficiales]; retención por defecto reportada
entre 7 y 30 días (fuentes en conflicto) y ZDR existe pero se solicita → **verificar en docs oficiales antes del
primer dato real** (NFR-005). Modelos: claude-sonnet-5-5 para Q&A/preparación de consulta, claude-haiku-5-5 para
tareas baratas; precios → verificar al implementar, no de memoria.

## 4. NFR budget (every change inherits this)
| ID | Attribute | Stimulus → response → measure | Proof (test) | Status |
|---|---|---|---|---|
| NFR-001 | security (cifrado) | acceso al almacenamiento sin credenciales de la app → datos de salud ilegibles → 100% de campos sensibles cifrados en reposo (app-level) y TLS en tránsito | test automatizado: lectura directa a DB muestra ciphertext en campos sensibles; scan de endpoints sin TLS = 0 | agreed |
| NFR-002 | security (revocación) | paciente desactiva enlace → siguiente request rechazado → 100%, < 5 s | test E2E: desactivar y golpear el enlace; asserts en suite | agreed |
| NFR-003 | security (bitácora) | todo acceso vía enlace → fila en bitácora (enlace, timestamp, recurso) → 100% | test: N accesos ⇒ N filas; revisión en cada PR que toque el portal | agreed |
| NFR-004 | compliance/privacy | alta de cuenta → consentimiento expreso registrado (con evidencia conservada, LFPDPPP art. 9: expreso y por escrito/equivalente para datos sensibles [VERIFIED 2026-10-11, verificar texto vigente en DOF: reforma 2025 cambió la autoridad]) antes del primer dato → 100%; ARCO: export (FR-002) y borrado (FR-003) ejecutables, borrado alcanza respaldos | checklist de cumplimiento en el primer cambio que capture datos; drill de borrado+restore | NEEDS CLARIFICATION (texto vigente + abogado antes de usuarios ≠ Saúl) |
| NFR-005 | compliance/privacy (IA) | consulta a IA → proveedor no entrena con el contenido y retención conocida y documentada → política verificada en fuente oficial con fecha | captura fechada de Commercial Terms/DPA en memory/research.md antes del primer dato real | NEEDS CLARIFICATION (retención 7 vs 30 días; ¿aplicar a ZDR?) |
| NFR-006 | data residency | datos en reposo en región US del PaaS → transferencia internacional declarada en aviso de privacidad con consentimiento (excepción médica LFPDPPP art. 36/37 existe pero numeración/alcance por verificar) → aviso publicado antes de v1 | revisión legal del aviso; item del checklist NFR-004 | NEEDS CLARIFICATION (default: US + aviso; región MX si la verificación legal lo exige) |
| NFR-007 | performance efficiency | pregunta a la IA → primer token < 2 s (streaming), respuesta completa p95 < 15 s | medición en staging con 20 preguntas reales del expediente | agreed (default propuesto) |
| NFR-008 | reliability | pérdida total del entorno → expediente restaurado íntegro → RPO ≤ 24 h (backup diario), restore verificado | drill mensual de restore documentado en journal | agreed (default propuesto) |
| NFR-009 | maintainability | cada FR Must → su test (regla del plan EPE); lint y suite verdes en CI → 100% de PRs | `make tdd-check` + CI en GitHub Actions | agreed |
| NFR-010 | usability | profesional abre QR/URL → resumen legible → < 1 min, cero instalación/registro | test E2E Playwright/Dusk con cronómetro | agreed |
| NFR-011 | functional suitability (safety) | salida de IA → fuente verificable + leyenda "no es consejo médico" → 0 sin fuente, 0 sin leyenda | test de contrato sobre AiGateway: respuesta sin cita ⇒ se descarta y responde "no hay información" | agreed |
| NFR-012 | language | UI y contenidos → es-MX → 100% | revisión en cada PR de UI | agreed |
| NFR-013 | hosting/operations + cost ceiling | operación mensual → ≤ 2 h de ops y ≤ $50 USD/mes en v1 (hay holgura, pero medible) → factura y bitácora | revisión mensual en journal | agreed (default propuesto) |
| NFR-014 | observability | error en producción → visible sin ssh (logs del PaaS + alerta de errores) → 100% de excepciones registradas | provocar excepción de prueba y verla llegar | agreed |

## 5. Decisions recorded
| ADR | Decision | File |
|---|---|---|
| D6 | (Revised por D11) recomendación original: monolito Laravel | memory/decisions.md |
| D10 | (Revised por D11) variante intermedia Laravel core + FastAPI portal | memory/decisions.md |
| D11 | Stack final: monolito con el template full-stack FastAPI (backend+frontend) para médicos, paciente y capa IA; microservicio IA solo como contingencia; sin Laravel. Decidido por Saúl Pérez (mercado) | memory/decisions.md |
| D7 | (Revised por D24) Cliente: web responsive + app Android por Capacitor; Kotlin nativo descartado en v1 | memory/decisions.md |
| D24 | App de Android nativa (Kotlin + Jetpack Compose) en `android/`, misma API; v1 hardware primero; iPhone nativo en Swift después. Decidido por Saúl Pérez | memory/decisions/D24-app-android-nativa-kotlin-compose.md |
| D8 | Hosting: PaaS que Saúl ya opera (Railway o Render, elegir en el primer cambio), región US + aviso de transferencia; revisar si la verificación legal exige región MX | memory/decisions.md |
| D9 | Proveedor IA: Claude API (no-training por defecto); retención/ZDR por verificar en fuente oficial antes del primer dato real | memory/decisions.md |

## 6. Consequences for the harness
- Layout del template: `backend/` y `frontend/`. `harness.json` → `code`: `backend/`, `frontend/` ·
  `tests`: `backend/app/tests/`, `frontend/tests/` además de los genéricos (el hook casa por prefijo exacto,
  verificado en .claude/hooks/_config.py:112-125, así que las rutas anidadas se declaran explícitas) ·
  `blocked_commands`: `alembic downgrade`, `docker compose down -v` (tiran esquema/volúmenes de la BD).
- **Entorno de desarrollo (ADR D12):** el que prescribe el template — Docker Compose (Postgres y stack, `watch`
  para hot reload) + uv para venv/dependencias Python + Node para el frontend. Sin Postgres nativo ni venvs manuales.
- Cada `/epe-1-explore` arranca del budget §4; cada `/epe-2-plan` dice cómo cumple los NFR afectados; romper el
  budget = cambiar este brief y su ADR en el mismo PR.
