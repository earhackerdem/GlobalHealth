# 2026-10-19 · onboarding-perfil (review adversarial + apply)

**Quién:** Saúl Pérez aprobó el gate con "todo" (y las 3 decisiones por el camino recomendado: cifrar condition,
TZ America/Mexico_City para measured_on, extender el veredicto K8/H5 a los 422 íntegros de pydantic). El harness
orquestó 5 finders + 4 validadores + 3 fixers.

**Review:** 33 hallazgos crudos → 30 únicos → **28 confirmados, 2 falsos positivos** (ambos con prueba: la
"fecha futura en silencio" — hallazgo del propio orquestador, el usuario SÍ ve el 422 es-MX — y la "bomba del
superusuario de auth.setup" — 222 ejecuciones verdes). Los 2 CRÍTICOS: sin UI para mediciones post-onboarding
(violaba el SHALL "completarse después") y family_history.condition EN CLARO (el spec manda sobre el design;
precedente ↩️ 2026-10-11). Comentarios finder/validator en el PR #16.

**Apply (3 fixers, prefijo NO-CLOSED, cero descartes por cuenta propia):**
- Backend: condition cifrada + migración re-cifrado f4b2c7d81e93 (idempotente, InvalidToken propaga), dedupe 409
  en POST (y PUT — hueco hermano cerrado por el orquestador con test), measured_on con TZ México, relatives
  acotado(8)+dedupe, GETs endurecidos (Literal + ge/le: adiós al 500 de skip=-1), y la suite endurecida
  (ciphertext determinista por descifrado, orden por fechas DISTINTAS vía retrodatado SQL, null-borra,
  other_text, es-MX exacto, consentimiento 9/9 rutas, 409/varios antecedentes).
- Frontend: **AddMeasurement en /perfil** (cierra el CRÍTICO G1), guardado del wizard idempotente (re-lee el
  servidor, 409 tolerado — reintento tras fallo parcial ya no duplica), "Mujer/Hombre" según el spec, foco al
  heading por paso + fieldset con aria-label (K5), ui/select de shadcn, EditBasicData a RHF+zod con fecha inline,
  getProfileQueryOptions, i18n page.* sin duplicar common, pageTitle sin branding del template, sidebar.perfil,
  regex del testMatch anclado.
- E2e: 6 escenarios (antes 4): registrar medición desde /perfil + validación inline, dos condiciones con PUT y
  DELETE del editor, omitir paso 2 no guarda lo marcado, relogin tras COMPLETAR, edad asertada en el Resumen,
  bucle muerto del Esc. 11 reemplazado por aserción directa.
- Documental (orquestador): Esc. 12 del spec reescrito a lo implementable, frontera de cifrado ratificada en
  spec+design (G19), evidence/validation corregidos (el FP era del orquestador), 4 filas nuevas en closed.md,
  deuda formatDateMx al inbox.

**Rebotado (1, parcial, para ratificación de Saúl):** migrar EditFamilyHistory a RHF+zod — el diálogo no tiene
campos escalares ni reglas que mostrar; queda ⏸️ en closed.md, se hace si lo reafirma.

**Verificación (re-corrida por el orquestador, desde limpio):** backend **168 passed / 0 failed / 0 skipped**,
cobertura **95%**, mypy limpio; tsc y lint limpios; Playwright **109 passed / 0 failed** (chromium + s26-ultra);
migración nueva aplicada también al contenedor dev. `openspec validate --strict` verde.

**Deuda viva:** formatDateMx duplicado (inbox) · PUT feliz de family-history sin test backend directo (lo cubre
el e2e del editor) · residuo usuario de prueba del fixer en BD dev (fixer-check-g1@example.com, local).
