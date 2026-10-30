---
date: 2026-10-29
---

# android-base: la app de Android entra y muestra el perfil

**Quién e intención.** Saúl Pérez (autor) instaló Android Studio y pidió arrancar la app nativa (D24). Es la primera
historia de la v1 «hardware primero».

**Exploración y plan.**
- Investigación con fuentes primarias (`memory/research/android.md`): minSdk 29 cubre al menos el 93.1 % en México;
  `security-crypto` quedó obsoleta (se usa DataStore con Tink); AGP 9.5; Play pide target 36.
- Saúl Pérez eligió las cuatro recomendaciones: Google después, el consentimiento en la app, básicos más el estado de
  las secciones, y minSdk 29. Navegó el prototipo y escribió «plan approved».

**Ejecución.**
- **Andamio:** Gradle 9.6.0 descargado de la fuente oficial con su checksum verificado, Compose con la paleta D22, CI
  `test-android` filtrado por `android/**` y `android/` agregado a `harness.json`.
- **Dos grupos test→impl:**
  - Grupo 1 (sesión, entrada, consentimiento): rojo de 12 referencias sin resolver; verde con 13 pruebas.
  - Grupo 2 (perfil): rojo de 30 referencias a `ProfileFormat`; verde con 39 pruebas.
  - Ninguna falla, error ni prueba saltada; lint sin errores; `tdd-check` ✓.
- **Lo que aparecieron en el camino:**
  - Robolectric con el SDK 36 no arranca sobre el JDK 25: se fijó el SDK 35 de pruebas.
  - Las librerías actuales exigen `compileSdk` 37.
  - Una prueba prohibía la palabra «editar» y chocaba con la nota aprobada: volvió al tester y ahora busca solo
    controles.
  - El tester también reforzó la prueba de D20 de «Entrar», que pasaba aunque el botón siguiera disponible.

**Verificación.** Pase en el emulador contra la API real:
- un solo pedido con doble toque;
- el perfil con datos reales;
- **cero coincidencias** del JWT o de datos del perfil en los archivos de la app;
- reabrir, girar, modo oscuro, sin API con «Reintentar», cerrar sesión, y el consentimiento registrado (201).

**No hecho.** El S26 Ultra no aparece por USB en la Mac (ni en `adb` ni en el sistema). Su recorrido queda en
`validation.md`. TalkBack no se activó.

**Deuda.**
- El texto del consentimiento es el provisional del backend («pendiente de revisión legal»).
- No hay backend en línea para la versión release.
- El ícono es provisional.
- Gradle 9.8.2 está disponible y el plan fijó 9.6.0.

## Revisión, ronda 1 (PR #44)

**Quién y qué:** Saúl Pérez (author) eligió la revisión adversaria y aprobó aplicar los 26 hallazgos confirmados.
`FLAG_SECURE` lo mandó al inbox. Revisaron cinco agentes, uno por lente: seguridad, criterios, pruebas, plataforma y
convenciones. Validaron cuatro agentes distintos, por reproducción contra la API real, con mutantes en una copia, en
el emulador y con `javap` de Tink. Aplicó un fixer, que no rebotó ninguno.

**Lo que se encontró:**
- **Alto, B1:** la API responde **403** a un token vencido, no 401. La app se quedaba en «Algo salió mal» con el
  token muerto. Las pruebas usaban un 401 que la API no da, y `evidence.md` afirmaba que estaba cubierto. La spec se
  enmendó, con la aprobación de Saúl Pérez: «un 401, o un 403 que no sea `CONSENT_REQUIRED`».
- **Medios:**
  - A2: un keyset ilegible cerraba la app en cada arranque;
  - A4: las pruebas de AB-6 pasaban sin cifrado;
  - D1: `validation.md` no se podía seguir (`JAVA_HOME`, depuración USB, qué cuenta usar).
- **22 bajos**, entre ellos «1 registrados», D20 en el consentimiento, el consentimiento ilegible en horizontal con
  letra grande, el destello blanco en oscuro y varias pruebas que dejaban pasar mutantes.

**Verificación:**
- Rojo de 69 pruebas con 18 fallas (`c3c46cf`) y verde de 69/0/0/0 (`369af78`), los dos re-corridos por el
  orquestador. Lint con 0 errores y `tdd-check` ✓.
- El S26 Ultra se conectó durante la revisión y se recorrió con el código de antes de los arreglos (`evidence.md`).
  Su keyset es un `EncryptedKeyset`, cifrado por el Keystore.

**Sobre el índice de cerrados:** los revisores lo recibieron con una línea por veredicto en el prompt, y el texto
completo en el archivo del brief. Ninguna de sus 60 filas trataba de Android.

**Que no estaba en el brief:**
- El fixer escribió algunos archivos con `sed` o Python por Bash, así que los hooks `lint.py` y `gate-plan` no los
  vieron (el límite declarado en CLAUDE.md). Sí pasaron por el compilador y por `lintDebug`.
- Durante el trabajo llegó un mensaje sobre «la RAM en uso en un sidebar» que no corresponde a esta sesión. No se
  actuó; se le pidió a Saúl Pérez que lo reenvíe a la sesión correcta.
