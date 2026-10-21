# 2026-10-20 · perfil-cronicas (review y apply, PR #26)

**Quién:** el agente corrió `/epe-4-review` sobre el PR #26. Saúl Pérez (author) decidió el gate:
- **Aplicar lo recomendado:** R1, R5, R6+R9b, R12, R14, R15, R16, R17, R19 y R24.
- **Contrato:** R11 y R13, que cambian el contrato del design, también se aplican.
- **R18:** opción b. Se desmarcó la casilla "truly green" del PR y el arreglo de las pruebas intermitentes heredadas
  va en un PR aparte (inbox).
- **R25:** chips, y además la regla de la casa de usar chips cuando se eligen opciones. Quedó como ADR D18, con la
  excepción de listas largas o dinámicas, que es una objeción del agente pendiente de que Saúl Pérez la confirme o
  la retire.

Su mensaje decía "R23"; el agente lo leyó como R13 (era el que pedía decisión junto con R11) y lo dijo en el chat.
R23 quedó en deuda, como se había recomendado.

**Qué se hizo:**
- **Ronda 1:** 5 lentes y 4 validadores. Ningún hallazgo crítico ni alto; solo R5 quedó en medio.
- **Apply 1** (6242e3d test, e59ba83 fix):
  - candado de perfil en PUT y en el DELETE de diagnóstico;
  - los años se comparan como rango de dos edades, y año contra año sin fecha de nacimiento;
  - validación de "desde" y "hasta" en el cliente;
  - aviso de borrado robusto;
  - chips en "¿Cuál?";
  - las pruebas que no podían fallar.
- **Ronda 2:** no salió seca. El apply había dejado arreglos sin prueba y dos regresiones de R5: la hora del
  navegador y el orden de los errores.
- **Apply 2** (6539264 test, 903124e fix): `crud.lock_profile` sin crear perfil, candado también en el borrado de
  crónicas, `retry: false` en el aviso, «hoy» de CDMX en el cliente y orden de errores.
- **Ronda 3:** dos hallazgos bajos, a deuda. Convergencia: 24 → 12 → 2.

**Verificación:**
- backend 250 passed, cobertura 96 %;
- e2e del cambio 117 passed (chromium y s26-ultra);
- e2e nuevos 80/80 con `--repeat-each=5`;
- `make tdd-check` ✓;
- 13 mutaciones, cada una tumba su prueba.

**Lecciones:**
- **Una ronda no basta.** La ronda 2 encontró defectos que introdujo el propio apply. Correrla sobre el diff del
  apply es lo que los atrapó.
- **El fixer escribe pruebas junto con el arreglo, no antes.** El rojo se demostró por mutación y quedó declarado
  en `evidence.md`.
- **Un mismo puerto, dos procesos.** Hay un `fastapi dev` ajeno a la sesión escuchando en `127.0.0.1:8000` junto al
  contenedor. Hoy los dos servían el mismo código, pero un "probé contra la imagen" en ese puerto no está
  garantizado.

**Deuda:** está en `memory/closed.md` (filas 2026-10-20 de perfil-cronicas) y en el inbox (las pruebas e2e
intermitentes heredadas).
