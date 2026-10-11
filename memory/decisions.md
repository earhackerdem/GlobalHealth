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
  pregunta abierta Q1 del brief, no excluidos de forma permanente.
