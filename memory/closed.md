# Closed — review verdicts already triaged

Injected verbatim into the finders and validators of /epe-4-review so they don't re-litigate what was decided.

States: 🔒 frozen (not reported; human decision or reproduced false positive) · ↩️ reopenable (only with new
evidence, citing the row) · ⏸️ deferred (goes to debt, not to findings) · 🧩 partial (only the missing instances)

| Date | Finding | Verdict and why | State | Anchor (journal: date · title) |
|---|---|---|---|---|
| 2026-10-11 | "SyntaxError en deps.py/tests (except A, B sin paréntesis): la API no arranca" | Falso positivo reproducido: es PEP 758, legal en el Python 3.14 del proyecto (pyproject, .python-version, Dockerfile, CI); 73/73 verdes en ese head. Residual real ya aplicado: paréntesis restaurados para el hook lint.py (python del sistema) | 🔒 frozen | journal: 2026-10-11 · cuenta-consentimiento (review) |
| 2026-10-11 | Barrera tester/implementer rota por fd073ea (tests tocados sin prefijo test: tras el rojo) | Confirmado y remediado: diff verificado 3× sin aserciones debilitadas (solo narrowing/formato); sanado con los commits test: del apply (c91eb7f, 39dc3d6) — tdd-check ✓. No re-litigar el commit histórico: la historia pusheada no se reescribe (guard de force-push) | 🔒 frozen | journal: 2026-10-11 · cuenta-consentimiento (review) |
| 2026-10-11 | HealthRecordStub.note en claro pese a design APPROVED que acotaba NFR-001 a subject | Confirmado y aplicado (cifrado, migración a7f3c9e2). Veredicto de criterio para E2+: TODO campo con contenido de salud se cifra desde su primera migración, el acotamiento por story no exime campos nuevos | ↩️ reopenable | journal: 2026-10-11 · cuenta-consentimiento (review) |
| 2026-10-11 | "md5 de PII real commiteado en evidence" | Falso positivo reproducido: el hash corresponde al email placeholder de .env.example (verificación aritmética del validador); criterio residual: snapshots futuros con datos reales usan sal no commiteada | 🔒 frozen | journal: 2026-10-11 · bd-pruebas-docker (review) |
| 2026-10-11 | "Mover el target del hijo rompe 3 tests sin describir la causa" | Falso positivo: AC1/AC2 sobreviven y el fallo de AC3 imprime la causa literal | 🔒 frozen | journal: 2026-10-11 · bd-pruebas-docker (review) |
| 2026-10-11 | "Puerto 5433 hardcodeado" | Falso positivo como defecto: convención heredada del template (db:5432 idéntico); parametrizar sería mejora opcional | 🔒 frozen | journal: 2026-10-11 · bd-pruebas-docker (review) |
| 2026-10-11 | "Healthcheck de db-test por socket: ventana del server temporal" | Riesgo teórico medido (ventana ≈160 ms, cierra ~4.4 s antes del primer probe; 0/5 reproducciones); fix opcional `pg_isready -h 127.0.0.1` si algún día flakea | ⏸️ deferred | journal: 2026-10-11 · bd-pruebas-docker (review) |
