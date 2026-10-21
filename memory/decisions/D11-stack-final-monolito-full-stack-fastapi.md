---
id: D11
date: 2026-10-11
status: accepted
---

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
