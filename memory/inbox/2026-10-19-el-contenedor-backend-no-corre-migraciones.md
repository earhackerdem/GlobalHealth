---
date: 2026-10-19
status: done
---

[2026-10-19] El contenedor backend NO corre migraciones Alembic al (re)arrancar: tras crear d5f2a8c41e07 la BD
dev dio 500 ("relation patient_profile does not exist") hasta un `docker compose exec backend alembic upgrade
head` manual (visto por el implementer del grupo 2 de onboarding-perfil). Decidir: prestart que migre, o
documentar el paso en make up. **✅ Cerrado (fix/dev-migraciones-y-cliente, 2026-10-20):** `make up` migra al
final y `make migrate` lo hace a mano tras crear una migración (corre `scripts/prestart.sh`, idempotente).
