---
date: 2026-10-29
state: deferred
anchor: journal: 2026-10-29 · android-base: la app de Android entra y muestra el perfil
---
Fuera del alcance de android-base (PR #44), ronda 1: X2, X3, X5 y la edad de la web. X1, X4 y D7 van al inbox

**Verdict and why:** el validador transversal confirmó la clasificación contra `design.md` (Non-Goals; el backend no
cambia) y la spec. Saúl Pérez aprobó el 2026-10-29 aplicar los 26 confirmados; estos quedan como deuda.
- **X2:** «Cerrar sesión» solo borra el token del teléfono. El JWT sigue valiendo hasta 8 días en el servidor
  (`backend/app/core/config.py:25`), porque no hay revocación ni `jti`. La web hace lo mismo (`useAuth.ts:60-64`).
  Revocar es un cambio de backend.
- **X3:** la build debug exporta `PreviewActivity` y `ComponentActivity`, que vienen de `debugImplementation`
  `ui-tooling` y `ui-test-manifest`. No llegan a release; es la plantilla estándar de Android Studio.
- **X5:** `android/.gitignore` no ignora `*.jks` ni `keystore.properties`. Se hace al configurar la firma (Play
  Console, fuera de alcance de D24 v1).
- **La edad en la web:** `frontend/src/components/Profile/format.ts:38-48` calcula con la fecha local del aparato. La
  API y la app usan America/Mexico_City. Se paga en la tarea de deudas de la web.
- **Van al inbox:**
  - X1 `FLAG_SECURE` (`memory/inbox/2026-10-29-flag-secure-app-android.md`), por decisión de Saúl Pérez;
  - X4 `alls-green` sin `changes` y D7 pruebas saltadas (`memory/inbox/2026-10-29-ci-alls-green-y-pruebas-saltadas.md`).
