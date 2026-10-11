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
