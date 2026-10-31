---
date: 2026-10-29
state: deferred
anchor: journal: 2026-10-29 · android-base: la app de Android entra y muestra el perfil
---
Ronda 2 de android-base (PR #44, diff 913fc86..6c3c186): seis hallazgos bajos. R2-4, R2-5 y R2-6 se corrigieron al cerrar; R2-1, R2-2 y R2-3 quedan como deuda

**Verdict and why:** la ronda 2 la hizo un finder sobre el delta de la ronda 1. Comprobó, con mutantes, que se
sostienen B1, B2, B5, B7, A1, A2, A4 y A6:
- ningún 403 legítimo de las rutas que usa la app cierra la sesión;
- el cuerpo de la respuesta no se lee dos veces;
- con el autollenado, «Entrar» se habilita;
- un arranque normal no descarta la sesión.

Encontró seis hallazgos bajos. Por la regla de cierre que Saúl Pérez aprobó con el plan (`design.md`, Decision 8),
si una ronda después de la primera trae solo bajos, quedan como deuda registrada y se archiva. Los tres de
documentos se corrigieron de todos modos, porque la evidencia debe ser fiel (AGENTS.md). Es el mismo precedente que
la ronda 2 de perfil-trabajo.

**Deuda:**
- **R2-1:** la prueba de B4 cubre `SessionStore.clearIfCurrent`, pero no el sitio de la llamada en
  `SessionInterceptor.kt:26`. Cambiarla por `clear()` deja la suite verde. El riesgo es que un 401/403 tardío de un
  token viejo borre una sesión nueva. Se paga con una prueba del interceptor con dos tokens.
- **R2-2:** `KeystoreAead.kt:35-48` trata cualquier error del Keystore como «keyset ilegible».
  - Una falla pasajera que sobrevive al reintento de Tink borra una sesión válida, y el paciente vuelve a entrar.
  - Una llave maestra que existe pero no sirve nunca se borra (`AndroidKeystoreKmsClient.deleteKey` existe), así
    que la sesión queda en memoria en cada arranque.
  - La rama `getOrElse` de `rebuild` no tiene prueba, porque Robolectric no tiene Keystore.
  - Se vio leyendo el bytecode, no en un dispositivo.
- **R2-3:** ningún pase en un dispositivo usó el código arreglado. El emulador se colgó y el S26 se desconectó: la
  rama con Keystore usable de `KeystoreAead` y el tema DayNight de la ventana solo se han visto en pruebas. Lo
  cubre la validación de Saúl Pérez en el S26 (`validation.md`, AB-5 y la parte opcional).

**Corregidos al cerrar:**
- **R2-4:** las anclas de la tabla criterio → prueba de `evidence.md` se movieron con el delta, y faltaban las
  pruebas del 403. Se reescribió la tabla con las líneas de `c6f0c44`.
- **R2-5:** `validation.md` dejaba a la persona en la cuenta B después de AB-3, y ninguna cuenta tenía datos. Ahora
  AB-4 vuelve a la cuenta A, que se llena en la web con un antecedente familiar y «Ninguna» en transfusiones.
- **R2-6:** el resto de B1 sin registrar. Con un token válido, la API responde 404 «Usuario no encontrado» (cuenta
  borrada) o 400 «Usuario inactivo» (`backend/app/api/deps.py:50-53`), y la app muestra «Algo salió mal» con
  «Reintentar» para siempre; «Cerrar sesión» sí funciona. La web tampoco lo maneja. **Queda como deuda aquí**: se
  paga junto con el manejo de sesión de la web, o al tratar esas dos respuestas como fin de sesión en
  `core/net/ApiResult.kt`.
