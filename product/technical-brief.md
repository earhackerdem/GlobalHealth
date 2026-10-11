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
| **A (recomendada): monolito Laravel 12 + PostgreSQL (pgvector) + Claude API directa; web responsive para paciente y profesional; app Android = shell Capacitor sobre la misma web** | Máxima fluidez (el núcleo privacidad/consentimiento se construye en el framework que domina); un solo deploy; cifrado, authn/z, colas y notificaciones resueltos por el ecosistema Laravel [OPINION fundada en fluidez declarada] | La capa IA se orquesta en PHP (llamadas HTTP al proveedor + pgvector): ecosistema de tooling IA más delgado que Python; OCR/procesado pesado de documentos quedaría para un sidecar futuro | Laravel y Postgres: aburridos y masivos; Capacitor: maduro, comunidad grande [OPINION] | Railway/Render corren Laravel+Postgres administrado (PaaS que ya opera) | Cumple NFR-013 (una persona), NFR-001/002 (revocación server-side trivial en monolito). Riesgo: NFR-009 si el procesado de PDFs crece → sidecar | fluidez: §1; template no requerido |
| B: fastapi/full-stack-fastapi-template (FastAPI + SQLModel + Postgres + React/TS + Docker + Traefik + GH Actions) | Un solo backend en el lenguaje del ecosistema IA; cliente OpenAPI autogenerado; template oficial mantenido (snapshot feb 2026) [VERIFIED: github.com/fastapi/full-stack-fastapi-template · 2026-10-11] | Python «reciente» + React probablemente nuevo: aprender dos capas mientras se construye el núcleo de privacidad; Traefik/Compose = más ops que un PaaS git-push | FastAPI: maduro, enorme adopción [VERIFIED mismo repo] | Dockerizado corre en Railway/Fly | Riesgo NFR-013 (curva + ops) en las semanas objetivo | ídem |
| C: Laravel núcleo + sidecar FastAPI para IA (idea original de Saúl) | Cada herramienta en lo suyo; Python disponible para RAG/OCR desde el día 1 | Dos servicios: dos deploys, dos superficies de secretos, contrato interno que mantener — el costo operativo más alto para una persona | ambos maduros | PaaS corre ambos (más caro) | Riesgo NFR-013; NFR-005 igual en los tres (el proveedor es el mismo) | — |

**Recommendation and what would change it:** **A**, con la capa IA detrás de UNA interfaz interna (un servicio
`AiGateway` propio): si el procesado de documentos u OCR lo exige, el sidecar FastAPI (C) se añade después sin
rediseño — C es la segunda mejor y el camino de evolución, no una alternativa perdida. B se descarta porque apila
dos aprendizajes sobre el código más delicado (consentimiento/privacidad); cambiaría la decisión que Saúl quiera
explícitamente invertir estas semanas en aprender el stack Python/React más que en lanzar v1.
**Cliente móvil:** web responsive primero y la app Android como shell Capacitor (notificaciones locales nativas
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
| D6 | Stack v1: monolito Laravel 12 + Postgres(pgvector) + Claude API tras interfaz AiGateway; descartados template FastAPI (B) y sidecar ahora (C → evolución futura) | memory/decisions.md |
| D7 | Cliente: web responsive + app Android por Capacitor; Kotlin nativo descartado en v1 | memory/decisions.md |
| D8 | Hosting: PaaS que Saúl ya opera (Railway o Render, elegir en el primer cambio), región US + aviso de transferencia; revisar si la verificación legal exige región MX | memory/decisions.md |
| D9 | Proveedor IA: Claude API (no-training por defecto); retención/ZDR por verificar en fuente oficial antes del primer dato real | memory/decisions.md |

## 6. Consequences for the harness
- `harness.json` → `code`: `app/`, `src/`, `routes/`, `database/`, `resources/`, `config/`, `lib/`, `packages/` ·
  `tests` sin cambio · `blocked_commands`: `php artisan migrate:fresh`, `php artisan db:wipe`, `php artisan migrate:reset`.
- Cada `/epe-1-explore` arranca del budget §4; cada `/epe-2-plan` dice cómo cumple los NFR afectados; romper el
  budget = cambiar este brief y su ADR en el mismo PR.
