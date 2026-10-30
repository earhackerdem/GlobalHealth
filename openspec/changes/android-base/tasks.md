# Tasks

Each group carries its Execution:
- **`single`:** one agent writes the red, commits it as `test:`, then the green.
- **`test→impl`:** a `tester` agent writes the red from the scenarios and the interface contract; the orchestrator
  commits it as `test:`; an `implementer` agent makes it green without touching tests.
- **`parallel`:** only with the interface contract filled and disjoint files.

Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation files is `test→impl`; smaller groups
are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Base · single

- [x] 0.1 **Prototipo** `openspec/changes/android-base/prototipo.html`, local y navegable, en un marco de teléfono con
  la paleta D22 (claro y oscuro):
  - la entrada, con error y «Entrar» no disponible;
  - el consentimiento;
  - «Mi perfil médico», con datos y vacío;
  - sin conexión;
  - insignias AB-n que se prenden y apagan.

  El agente lo recorre primero en Chrome. «plan approved» significa «navegué el prototipo y esto es lo que quiero».
- [ ] 0.2 **Andamio** (orquestador; es infraestructura de pruebas y de compilación, se declara en evidence.md):
  - `android/` con el wrapper de Gradle 9.6.0 (con checksum), `libs.versions.toml`, el módulo `app` con minSdk 29,
    target 36, Compose, Material 3 con los colores de D22 y una `MainActivity` vacía;
  - las dependencias de prueba (JUnit, Robolectric, MockWebServer, ui-test de Compose);
  - `network_security_config.xml` de debug y las reglas de respaldo;
  - `harness.json` (`code` y `tests`), `.gitignore`, y `.github/workflows/test-android.yml`.

  Verificación: `./gradlew assembleDebug testDebugUnitTest` verde con 0 pruebas, y la app vacía instalada en el
  emulador.

## 1. Sesión, entrada y consentimiento · test→impl

- [ ] 1.1 **Tester.** Pruebas en `android/app/src/test/` a partir del test plan (filas 1, 2, 3, 4, 6, 7, 8 y 9) y del
  Interface contract, con MockWebServer y Robolectric. Verificación: rojo porque falta la app, no porque la prueba esté
  rota. Commit `test:` solo.
- [ ] 1.2 **Implementer.** `core/net` (Retrofit, el interceptor de token y de 401), `core/session` (DataStore con
  Tink), `auth`, `consent` y la navegación. Verificación: las pruebas de 1.1 en verde sin tocarlas; `lintDebug`
  limpio.
- [ ] 1.3 **Orquestador.** Rojo y verde de nuevo, `make tdd-check`, números en evidence.md.

## 2. Mi perfil médico · test→impl

- [ ] 2.1 **Tester.** Pruebas de `ProfileFormat` y de la pantalla del perfil (fila 5, y la 9 sobre el perfil). Commit
  `test:` solo.
- [ ] 2.2 **Implementer.** `profile/` (ViewModel, `ProfileFormat`, pantalla) con `strings.xml` en español.
  Verificación: verde sin tocar las pruebas; `lintDebug` limpio.
- [ ] 2.3 **Orquestador.** Rojo, verde y `tdd-check`; `assembleDebug`; números en evidence.md.

## 3. Verificación final y entrega · single

- [ ] 3.1 **Exploración del agente por `adb`** en el emulador (y en el S26 si está conectado): los casos del test
  plan, más girar la pantalla, el modo oscuro, TalkBack en la entrada y doble toque. Verificación: tabla en
  evidence.md con capturas en el scratchpad (no en el repo).
- [ ] 3.2 **CI.** `test-android.yml` en verde en el PR.
- [ ] 3.3 **Entregables.** `evidence.md`, `validation.md` (no técnico, para que Saúl Pérez lo recorra en su S26 con
  `adb reverse`), el journal y el PR.
- [ ] 3.4 **Revisión y archivo** (`/epe-4-review` → `/epe-5-apply` → `/epe-6-archive` como último commit del PR), con la
  regla de la Decision 8, o el archivo sin revisión si Saúl Pérez lo elige.
