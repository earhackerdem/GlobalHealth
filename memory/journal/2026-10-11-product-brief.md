# 2026-10-11 — Product brief del expediente personal de salud

- Saúl Pérez (author/owner) trajo la idea: app Android (paciente) + web (personal de salud) para registrar
  recetas, diagnósticos y resultados, con IA que responde citando el expediente, y compartir vía QR/PDF/URL
  revocable. Motivación de primera mano: historial fragmentado → malos diagnósticos repetidos.
- Triage: rung **brief** (greenfield, muchas features, sin product/). Saúl aceptó y pidió explícitamente
  priorizar la privacidad para evitar reescrituras.
- Entrevista en una ronda (AskUserQuestion): alcance v1 = solo él con diseño multi-usuario; jurisdicción México
  (LFPDPPP + NOM-024); fuera de v1: wearables y telemedicina, con registro explícito e investigación de wearables
  con API abierta.
- Investigación de wearables → memory/research.md#wearables (Health Connect [VERIFIED], Fitbit en deprecación
  [VERIFIED], Garmin/Polar/Oura NOT VERIFIED, fallback PDF).
- Escrito product/brief.md (Status: draft — falta que Saúl lo acepte), ADRs D2–D4 en memory/decisions.md.
- Veredicto del brief: **PRD sí** (≥2 épicas sobre el mismo modelo de consentimiento). Siguiente:
  `/product-prd` → `/product-tech-brief`.
- Sin remoto git configurado: el trabajo queda en rama local `docs/product-brief`, sin PR posible aún.
- Nota: START-HERE.md aparece borrado en el árbol desde antes de esta sesión; no es de esta sesión y no se tocó.

## Segunda ronda (mismo día)
- Saúl Pérez respondió las 4 preguntas abiertas → ADR D5 (recordatorios mínimos en v1; enlace por profesional
  tipo+nombre revocable; IA proactiva también para el paciente; freemium con límite de consultas).
- Objeción de socio escéptico registrada: IA que sugiere estudios/médicos directo al paciente = recomendación
  clínica (riesgo COFEPRIS + alucinación). Alternativa adoptada en el brief: encuadre "preparación de consulta"
  (sugerencias con fuente, para discutir con el profesional). Saúl puede revertirlo.
- Investigación de comorbilidades pedida por Saúl → memory/research.md#comorbilidades (SII↔ansiedad [VERIFIED],
  ansiedad↔alcohol [VERIFIED], historial familiar→tamizaje [principio VERIFIED, umbrales 2026 por verificar],
  clústers de multimorbilidad [heurística, no regla]).
- Brief actualizado: O6 (detección proactiva de huecos con fuente obligatoria), preguntas abiertas → resueltas.

## Tercera ronda (mismo día): PRD
- Escrito product/prd.md (Status: draft): 25 FR, 14 NFR medibles (los números desconocidos como NEEDS
  CLARIFICATION, nunca inventados), 6 épicas (cuenta/privacidad, expediente, compartir, portal profesional, IA,
  recordatorios), trazabilidad outcome→épica→FR/NFR.
- 3 preguntas abiertas para Saúl Pérez: ¿FR-018 (aprobar aportes del profesional) y FR-014 (granularidad por
  categorías) suben a Must?; residencia de datos → technical brief.
- Split en change folders diferido hasta después del technical brief (ninguna story arranca aún).
- Pendiente: Saúl acepta el PRD → /product-tech-brief (stack, presupuesto NFR).

## Cuarta ronda (mismo día): technical brief
- Saúl Pérez subió FR-014 y FR-018 a Must (Q1/Q2 del PRD).
- Pregunta bloqueante respondida: PaaS (Railway/Fly/Render/Vercel) ya operado, sin techo estricto de gasto,
  20+ h/semana, abierto en cliente móvil.
- Escrito product/technical-brief.md: recomendación A = monolito Laravel + Postgres(pgvector) + Claude API tras
  AiGateway; cliente web responsive + Capacitor para Android; descartados template FastAPI (dos aprendizajes sobre
  el núcleo de privacidad) y sidecar desde v1 (evolución futura, no alternativa perdida). ADRs D6–D9.
- Budget NFR de 14 entradas con prueba por NFR; NEEDS CLARIFICATION honestos: texto vigente LFPDPPP (reforma 2025),
  retención exacta de Anthropic (7 vs 30 días, verificar en fuente oficial antes del primer dato real), residencia.
- harness.json: code += routes/, database/, resources/, config/; blocked_commands += migrate:fresh/reset, db:wipe.
- Verificaciones a memory/research.md#stack (no-training Anthropic, template fastapi, LFPDPPP art. 9/36-37).
- Pendiente: Saúl acepta el technical brief → split de la primera story (épica E1 cuenta/privacidad) con
  `make epe-new`.

## Sexta ronda (mismo día): vacío de entorno de desarrollo, detectado por Saúl Pérez
- Antes de aprobar US-01, Saúl Pérez preguntó si el harness define el entorno local (¿Docker para la BD? ¿venvs?).
  No lo define: se resolvió con ADR D12 (el entorno del template: Docker Compose + uv, verificado en commit log) y
  quedó propuesta la meta-mejora para el skill product-tech-brief en memory/meta-improvements.md.
- También abierta la story US-01 `cuenta-consentimiento` (openspec, 4/4 artefactos, design en DRAFT esperando
  "plan approved"); FR-026 (login con Google) añadido antes al PRD a pedido suyo.

## Quinta ronda (mismo día): el stack lo decide el dueño — sin Laravel
- Saúl Pérez corrigió la dirección dos veces: primero "la capa IA sí o sí en FastAPI por mercado" (quedó D10:
  Laravel core + FastAPI portal), y al ver esa variante aclaró su ideal: "prefiero no usar Laravel" — monolito con
  el template full-stack FastAPI para médicos, paciente y capa IA; microservicio IA solo como contingencia (sin
  template; evaluar config por variables en BD si llega).
- La objeción del agente (fluidez Laravel vs aprender Python+React sobre el núcleo de privacidad) fue oída y
  descartada por Saúl: decisión suya, registrada en D11 con el costo aceptado. D6 y D10 → Revised.
- technical-brief.md actualizado (opción B marcada ELEGIDA), harness.json: code backend//frontend/, tests
  anidados explícitos (el hook casa por prefijo: .claude/hooks/_config.py:112-125), blocked_commands de Alembic y
  docker volumes en lugar de artisan.
