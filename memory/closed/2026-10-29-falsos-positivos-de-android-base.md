---
date: 2026-10-29
state: frozen
anchor: journal: 2026-10-29 · android-base: la app de Android entra y muestra el perfil
---
Falsos positivos de la revisión de android-base (PR #44), ronda 1: B6, C3 (para la app) y C5

**Verdict and why:** los validadores los tumbaron por reproducción, y Saúl Pérez aprobó el resto el 2026-10-29.
- **B6** («la aserción "ningún dato del perfil antes de aceptar" no puede fallar porque el fake responde 403»): con una
  cuenta nueva sin consentimiento, la API real responde 403 en las cinco rutas `profile*` (`ConsentedUser`,
  `backend/app/api/routes/profile.py`). El fake copia ese contrato. Que no lleguen datos lo garantiza el servidor
  (NFR-004), y que no aparezca la pantalla del perfil lo comprueba `SessionLoginConsentTest.kt:174`.
- **C3** («la edad de la app no es igual a la de la web»): la app sigue `design.md`, que fija «hoy» en
  America/Mexico_City, igual que la API (`backend/app/api/routes/profile.py:76`). La que se aparta es la web
  (`frontend/src/components/Profile/format.ts:38-48`, fecha local del aparato). Eso es deuda de la web: está en el
  veredicto diferido de este mismo cambio.
- **C5** («los campos de entrada no ofrecen autollenado»): en el S26 Ultra, Samsung Pass ofreció guardar usuario y
  contraseña. En el emulador, la sesión de `AutofillManager` lista los dos campos como autollenables. Ningún criterio
  lo pide. Si algún día hace falta, `contentType` en `LoginScreen.kt` es opcional.
