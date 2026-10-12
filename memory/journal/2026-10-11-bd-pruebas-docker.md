# 2026-10-11 — bd-pruebas-docker: BD de prueba efímera y guarda en la suite

- Contexto inmediato: Saúl Pérez re-verificó el flujo Google real (botón → Google → /google-callback → sesión,
  consentimiento aceptado) y mergeó el PR #1. Pidió una BD de prueba "también en docker"; plan aprobado
  ("plan approved") el mismo día.
- El CI del PR #1 se cerró en verde total: el único rojo (merge-playwright-reports) era un artefacto
  `blob-report-1` corrupto en el storage de GitHub (falló 2× con digest OK en los otros 3); se borraron los 4
  blobs efímeros y el re-run completo pasó. Nada de código.
- Ejecución en 3 grupos: infra compose (single) → guarda+automigración (test→impl) → CI+evidencia (single).
  Rojo 2 failed/1 passed (658da3f); verde final **103/0/0, cobertura 93.69%**, tdd-check ✓.
- Asimetría asumida y documentada: el verde del grupo 2 vive en `backend/tests/conftest.py` (ruta de tests), el
  guard-tests bloquea ahí al implementer → lo implementó el orquestador y entró como commit `test:` (133f056)
  para que tdd-check siga verificando por git.
- Ajuste de contrato en caliente: `TEST_DATABASE_URL=""` explícita = desactivada sin fallback (si no, el
  escenario "sin configuración" era intesteable en máquinas cuyo `.env` ya define la variable). design.md
  actualizado, no recortado.
- Incidente honesto: la corrida ROJA aún usó el conftest viejo y barrió la BD dev una última vez — se llevó el
  usuario Google y el consentimiento recién creados por Saúl. Re-sembrada con prestart; el snapshot md5
  antes/después de DOS suites completas salió idéntico (aislamiento probado). Desde 133f056 es imposible por
  construcción.
- Cobertura: al migrar en-proceso, coverage contó `app/alembic/versions/*` → 85.70% espurio; `omit` en
  pyproject y la cifra real quedó en 93.69% (= cierre anterior). ADR D14 registrado (extiende D12).
- Deuda/no-goals: paralelismo de dos pytest simultáneos sobre db-test (fuera de alcance, se decide si duele);
  inbox: la fila de cobertura-al-umbral quedó obsoleta (93.69% desde el apply).

## Ronda review→apply (misma fecha)
- /epe-4-review: 5 finders → 21 únicos → 4 validadores por reproducción → rondas 2 y 3 NO secas (3 nuevos + 3
  bajas); parado por calibración y reportado como límite. 3 falsos positivos documentados (md5 "de PII" era el
  placeholder de .env.example — verificación aritmética; target movido; puerto hardcodeado). Hallazgo estrella de
  ronda 2: los 3 workflows disparaban push a master con default main → sin CI post-merge (herencia del template).
- Saúl Pérez aprobó los grupos A/B/C completos. Fixer 15/15 sin rebotes. El validador me atrapó afirmando en
  evidence que el design reflejaba la versión final cuando git probaba lo contrario — corregido y confesado en el
  propio evidence.
- Re-evidencia de aislamiento con GIVEN real sembrado (5 tablas, cifrado verificado en crudo): counts idénticos,
  dumps normalizados idénticos (pg_dump 18 mete token \restrict aleatorio — gotcha nuevo), y prueba xmin: ninguna
  transacción escribió en la BD dev durante dos suites (104 passed c/u).
- Corrección inline a la entrada de arriba: "design.md actualizado, no recortado" era cierto solo para la semántica
  de vacía-explícita; los pasos 1 y 4 del contrato quedaron viejos hasta este apply (hallazgo G2/H2-1).
- closed.md +4 filas; meta-improvements: brecha tdd-check/conftest; inbox: despersonalizar artefactos (decisión de
  Saúl).
