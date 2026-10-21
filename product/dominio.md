# Dominio — GlobalHealth · rebanada "receta a la mexicana"

Date: 2026-10-18 · Interviewed: Saúl Pérez (author, haciendo de paciente-interesado; mensaje del 2026-10-12 tras
probar el expediente v1) · Evidencia: 74 fotos reales de documentos propios aportadas por Saúl el 2026-10-18
(§ Evidencia empírica; las fotos NO entran al repo, aquí solo su estructura) · Status: **agreed — gate cerrado el
2026-10-18: Saúl Pérez validó el prototipo y respondió las 4 preguntas (Q1-A con B diferida a inbox, Q2-A, Q3-A,
Q4-A dos stories)**
Prototipo: **`product/prototipos/receta-primero.html`** (fuente de verdad, se abre en cualquier navegador; la
publicación en claude.ai es solo conveniencia y está ligada a una cuenta). Incluye la historia de usuario borrador
y los AC-1…AC-9 con el toggle "Ver criterios".
Alcance: SOLO el dominio de la receta y su captura. El resto del producto ya está en product/prd.md; esta rebanada
corrige el modelo que la v1 del expediente asumió mal.

## Catálogos (en las palabras de Saúl)

### Receta
| Attribute | In their words | Sensitive? | Notes / [ASSUMPTION] |
|---|---|---|---|
| medicinas (varias) | "la receta dice las medicinas" | sí | una receta ⇢ N medicinas; en las fotos: 1–4 por receta [VERIFIED 2026-10-18 fotos] |
| fecha de expedición | "tiene la fecha en que se expide" | sí (metadato) | [VERIFIED fotos] — pero frágil: manuscrita junto a la firma o incluso ausente en recetas tradicionales |
| nombre del paciente | "y el nombre del paciente" | sí | presente en casi todo el corpus, PERO hay documentos de **familiares** (titular ≠ paciente) [VERIFIED fotos] |
| médico que la expide | implícito en "quién te la dio" | sí | [VERIFIED fotos: membrete con nombre + cédula profesional en el 100% de recetas; a veces un 2º prescriptor manuscrito] |
| diagnóstico | "no suele venir con diagnóstico… te lo dicen con la voz" | sí | **campo opcional de la receta**, no entidad aparte [VERIFIED fotos: escrito solo en ~⅓–½, casi siempre en formatos impresos de cadena] |
| foto original | "subir una foto de la receta… o usar la cámara" | sí | el documento fuente queda adjunto al registro [VERIFIED]; relación foto↔documento N:M (reversos, retomas, 2 docs en una foto) [VERIFIED fotos] |

- **Relations:** receta → medicinas (1→N) · receta → foto/adjunto (1→0..N) · receta → diagnóstico (campo, 0..1)
- **States / lifecycle:** [ASSUMPTION] emitida → (surtida) → vencida/histórica — la vigencia impresa es la excepción
  [VERIFIED fotos: 2 de ~33 recetas la traen ("UN AÑO"), más leyendas genéricas de farmacia]; cualquier vigencia es
  dato opcional, nunca obligatorio. Pregunta abierta Q1.
- **What they explicitly do NOT want:** vigencia inicio/fin obligatoria; diagnóstico como registro separado
  obligatorio; capturar a mano como ÚNICO camino.

### Medicina (dentro de una receta)
| Attribute | In their words | Sensitive? | Notes |
|---|---|---|---|
| nombre | "las medicinas" | sí | [VERIFIED fotos] — a veces sustancia activa, a veces marca, a veces ambas |
| dosis / indicación | cómo tomarla | sí | [VERIFIED fotos] — ojo: puede ser **escalonada/condicional** ("X dos semanas, luego Y"; "si sigue el dolor…"), no un valor único |
| frecuencia / horarios de toma | — no lo dijo | sí | [VERIFIED fotos: frecuencia y duración vienen escritas en casi todas las recetas] → refuerza Q2-A (capturar ya) |
| duración / "hasta terminarlas" | — no lo dijo | sí | [VERIFIED fotos] casi constante; es lo que haría derivable una vigencia (Q1-B) |
| vía de administración | — no lo dijo | sí | [VERIFIED fotos] frecuente en impresas (oral/IM/tópica), a veces implícita en manuscritas → opcional |

## Glosario
| Their word | Meaning here | Never call it |
|---|---|---|
| receta | el papel/documento del médico con las medicinas | prescription order, vigencia |
| medicina | cada renglón de la receta (nombre + dosis) | drug, fármaco |
| subir la receta | tomarle foto o elegir una imagen existente | escanear |

## Procesos observados (who / when / with whom → future FRs)
| Who (role) | Does what | When / trigger | With whom | Exceptional paths mentioned |
|---|---|---|---|---|
| paciente | sube foto de la receta (cámara o imagen existente) | al salir de la consulta | — | foto borrosa/ilegible; el OCR se equivoca → el paciente corrige antes de guardar |
| paciente | dicta la receta con el micrófono (por campo o libre) | cuando la receta es manuscrita o no está a la mano | reconocimiento de voz (ideal: en el dispositivo) | nombre de medicina mal reconocido → corrige en la revisión |
| sistema (OCR+IA) | lee la foto y prellena medicinas, fecha, médico | tras subir la foto | proveedor IA (NFR-005: cero retención) | lectura parcial → campos vacíos editables, nunca inventados |
| paciente | confirma/corrige y guarda; puede capturar a mano sin foto | tras la lectura | — | — |

## Escalera de captura (Saúl Pérez, 2026-10-18 — tras ver la evidencia de las fotos)

Tres entradas + la manual, ordenadas por costo, todas desembocando en **la misma pantalla de revisar/corregir antes
de guardar** (nunca se inserta sin confirmación del paciente): [VERIFIED 2026-10-18, en sus palabras]

| # | Entrada | Cuándo conviene | Costo/dependencia | Nota |
|---|---|---|---|---|
| 0 | teclado (manual) | siempre disponible, fallback universal | cero | ya en la rebanada |
| 1 | **dictado** ("botón de micrófono para dictar su receta") | recetas manuscritas o cuando no hay papel a la mano | reconocimiento de voz, puede ser **en el dispositivo** (mejor para NFR-005) | esquiva la caligrafía: el paciente la lee en voz alta. Variante barata: dictado por campo (cero parseo); dictado libre requiere un paso de estructuración |
| 2 | **foto + OCR** con revisión del usuario | recetas **impresas** (cadena/laboratorio: buena calidad OCR) | OCR clásico, barato | ⚠️ el OCR lee caracteres pero no separa campos: hace falta plantilla por formato o un paso ligero de estructuración; la revisión del usuario absorbe los errores |
| 3 | **foto + LLM/visión** | manuscritas, giradas, reversos, multi-documento | el más caro; proveedor pendiente (Q4 / NFR-005) | último recurso, no el camino default |

Regla transversal: lo que no se lee queda vacío y editable, nunca inventado; el corpus real de 74 fotos sirve de
banco de pruebas para medir (tech-brief) hasta dónde llega cada peldaño antes de pagar el siguiente.

## Evidencia empírica — 74 fotos reales (Saúl Pérez, 2026-10-18)

Corpus: 74 fotos propias (2015–2026) ≈ **~50 documentos únicos** (≈⅓ son retomas del mismo papel, reversos o dos
documentos en una foto). Las imágenes NO entran al repo; esto es solo su estructura. [VERIFIED 2026-10-18]

### Inventario por tipo
| Tipo | Docs únicos (aprox.) | Nota |
|---|---|---|
| Receta — consultorio de farmacia / cadena (impresa, estructurada) | ~12 | el tipo dominante; folio, QR, fecha nacimiento, a veces signos vitales y diagnóstico impresos; **campos obligatorios rellenos con basura ("ss")** |
| Receta — privada tradicional o de especialista (membrete + manuscrito) | ~13 | la mitad del corpus de recetas es **manuscrita**; las de especialista, la peor caligrafía |
| Receta — dental / recomendaciones de higiene sin posología | 2 | "producto recomendado" ≠ medicina con dosis |
| Orden/solicitud de estudios (lab, imagen; a veces sobre papel de receta) | ~5 | la receta también funciona como solicitud |
| Comprobante de pago de laboratorio/imagen | ~5 | folio/QR/clave para descargar el resultado en portal externo |
| Resultado de laboratorio (analitos + rangos; un antibiograma) | ~4 | estructura tabular propia: analito → valor → unidad → rango → bandera |
| Nota clínica institucional (urgencias IMSS) | 1 | motivo, antecedentes, exploración, DX, plan: más rica que una receta |
| Comprobante de vacunación (papeleta suelta) | 1 | biológico, refuerzo, fecha, unidad aplicadora |
| Indicaciones manuscritas sueltas / posología sobre el empaque | ~3 | tratamiento real sin paciente, médico ni fecha |
| No médico (tickets, horarios, listas) | ~6 | el pipeline necesita una clase "descartar" |

### Qué confirma y qué corrige del catálogo
- Confirma: receta ⇢ N medicinas (1–4); diagnóstico escrito es la excepción (~⅓–½, concentrado en formatos de
  cadena); vigencia casi nunca impresa (2 de ~33); médico con cédula profesional constante en el membrete;
  frecuencia y duración vienen escritas casi siempre (soporta Q2-A).
- Corrige/matiza: la fecha es frágil (manuscrita o ausente); el nombre del paciente no siempre es el titular
  (**documentos de familiares** en el corpus); la dosis puede ser escalonada/condicional, no un valor único;
  "campo impreso presente" ≠ "dato real" (basura "ss" en formatos de farmacia).

### Implicaciones para la captura foto-primero (insumo del tech-brief / Q4)
1. ~40–50% de los documentos son manuscritos → OCR genérico no basta: se necesita visión-IA/HTR o captura asistida.
2. Normalizar orientación (muchas fotos giradas 90°/180°, sombras, recortes) es prerrequisito.
3. Deduplicación por contenido (folio/fecha/medicinas): ~⅓ del corpus son retomas del mismo documento.
4. Relación foto↔documento N:M: reversos con medicinas extra, 2 documentos en una foto.
5. Clasificador de tipo de documento ANTES de extraer campos (receta / resultado / orden / comprobante / vacuna /
   descartar), con "lo que no leo queda vacío, nunca inventado".
6. Matching de identidad laxo: nombres con erratas e inconsistencias entre documentos del mismo paciente.

### Fuera del alcance de esta rebanada (catálogos futuros, no se modelan ahora)
Resultado de laboratorio (estudio → analitos), orden de estudios, comprobante de pago ligado a resultado externo,
vacunación, nota clínica, titular ≠ paciente (expediente familiar), referencias/derivaciones entre médicos. Se
registran aquí para que las próximas rebanadas no partan de cero.

## Diagnóstico suelto y su confirmación (Saúl Pérez, 2026-10-18 — responde Q3 y abre concepto nuevo)

El diagnóstico suelto es una entrada del expediente **capturada por el paciente** (lo que le dijeron de palabra),
sin documento que lo respalde. Para darle peso clínico sin quitarle facilidad, Saúl propone que un **médico pueda
confirmarlo** vía el enlace/QR que el paciente comparte (E3/E4): porque lo atendió antes, o porque tiene su propio
registro del paciente. [VERIFIED 2026-10-18, en sus palabras]

- **Estados del diagnóstico suelto:** registrado (solo palabra del paciente) → confirmado por «médico» el «fecha»
  (vía enlace activo). La confirmación no lo vuelve editable por el médico: sigue siendo del paciente; el médico
  solo atestigua. [ASSUMPTION: la confirmación es un sello, no una edición — validar en el siguiente prototipo]
- **Para qué sirve:** el paciente y sus médicos tienen contexto de salud "aunque no tengan toda la info a la
  mano"; un diagnóstico confirmado vale más para la IA (E5) y para otro médico que uno solo dicho.
- **Encaje regulatorio** (memory/research.md 2026-10-18): el paciente compartiendo es ejercicio de su titularidad
  (NOM-004 5.4/5.5.1); el médico que confirma queda identificado como en toda nota clínica (NOM-004 5.10: nombre,
  fecha, firma) → la confirmación debe registrar quién/cuándo/vía qué enlace, y caer en la bitácora de accesos
  (US-03).
- **Alcance:** el modelo (entrada suelta + campo `confirmación`) entra en la rebanada receta-mexicana solo como
  dato; el FLUJO de confirmación vive en E3/E4 (requiere enlaces), no en la primera story.

## Datos sensibles y retención
| Data | Who may see it | Kept for | Who can erase it | Regulation |
|---|---|---|---|---|
| foto de la receta + campos | el paciente; profesional solo vía enlace activo (E3/E4) | mientras viva la cuenta | el paciente (ARCO) | LFPDPPP; cifrado en reposo ya probado (D13/D16) |
| contenido enviado al OCR/IA | el proveedor NO lo retiene ni entrena | n/a | n/a | NFR-005, proveedor pendiente (Q4) |

Regulación verificada en texto vigente (memory/research.md, 2026-10-18): **nueva LFPDPPP** (DOF 2025-03-20, ref.
2025-11-14) — salud es dato sensible (art. 3-VI), consentimiento expreso y por escrito vía mecanismo de
autenticación (art. 8), notificación inmediata de vulneraciones (art. 19), cancelación con bloqueo (art. 24),
multas duplicadas en sensibles (art. 59); autoridad: Secretaría Anticorrupción y Buen Gobierno. NOM-004 5.4:
titularidad del paciente sobre su información (sustento del compartir por enlace). NOM-024 (SIRES): pendiente de
verificar si aplica cuando exista el portal del profesional (E4).

## Open questions (max 4) — el gate del discovery
1. ~~**Vigencia/eliminación**~~ **RESPONDIDA (Saúl Pérez, 2026-10-18): opción A** — el paciente archiva
   manualmente. **B queda como pendiente explícito** (vigencia derivada de la duración si la IA la infiere,
   editable) para cuando se resuelva el proveedor de IA (Q4); fila en memory/inbox.md.
2. ~~**Frecuencia de toma**~~ **RESPONDIDA (Saúl Pérez, 2026-10-18): opción A** — campo opcional por medicina
   desde ya (así está en el prototipo v4).
3. ~~**El tipo "diagnóstico" de la v1**~~ **RESPONDIDA (Saúl Pérez, 2026-10-18): opción A** — el diagnóstico
   suelto se conserva como entrada del expediente, sin receta ni resultado que lo respalde ("idealmente una
   persona debería ser capaz de guardar diagnósticos aunque no estén ligados a una receta o un resultado").
   Razón: facilidad de uso; no todo el mundo guarda sus papeles (su papá archiva todo en físico; "no es una
   práctica general"). Deriva un concepto nuevo → § Diagnóstico suelto y su confirmación.
4. ~~**Proveedor OCR/IA**~~ **RESPONDIDA (Saúl Pérez, 2026-10-18): opción A — dos stories.** La primera entrega
   modelo + captura manual/dictado + foto adjunta, sin IA; la segunda (lectura con IA) espera al tech-brief del
   proveedor. Contexto original de la pregunta: *Evidencia fotos: ~mitad del corpus es manuscrito, con
   giros y retomas → el pipeline de lectura es un proyecto en sí (visión-IA/HTR + clasificador + dedupe), no un
   añadido; separa stories con más razón.*
   Insumos para el tech-brief (Saúl Pérez, 2026-10-18 + verificación en memory/research.md): **Gemini API gratuito
   (AI Studio) queda descartado para datos de salud** — sus términos permiten a Google usar prompts/respuestas
   para mejorar productos con revisores humanos y piden no enviar información sensible [VERIFIED 2026-10-18];
   candidatos vivos: Gemini **de pago** (no entrena, pero loguea por abuso), API de Anthropic (no entrena por
   default), **Gemini Nano on-device** (spike D17, cero retención por construcción), y la idea de Saúl de **BYOK**
   (el usuario trae su propia API key) — con la salvedad de que la app deberá rechazar proveedores/modos cuyos
   términos entrenen con los datos.

---

# Dominio — GlobalHealth · rebanada "perfil del paciente y antecedentes familiares (onboarding)"

Date: 2026-10-19 · Interviewed: Saúl Pérez (pedido del 2026-10-18 al cerrar receta-mexicana, fila SIGUIENTE TAREA
en memory/inbox.md: "fecha de nacimiento, peso actual, estatura, y antecedentes médicos familiares — lo que
preguntan mucho los médicos: diabetes o cáncer en la familia — justo después de aceptar el consentimiento") ·
Evidencia: el mismo corpus de 74 fotos (2026-10-18) · Status: **agreed — gate cerrado el 2026-10-19: Saúl Pérez
respondió las 4 preguntas en dos rondas (Q2 especificidad de línea, Q3 todo omitible, y "sigo tu recomendación
para ambas" sobre Q1 medición con fecha y Q4 alcance de la primera story) con el prototipo v2 a la vista**
Prototipo: **`product/prototipos/onboarding-perfil.html`** (fuente de verdad; incluye historia borrador y los AC
con el toggle "Ver criterios"; v2 con línea materna/paterna y secciones del perfil médico).
Alcance: el feature es el **perfil médico por secciones** (la anamnesis estándar, § El perfil médico por
secciones); el **onboarding** post-consentimiento captura solo el mínimo (perfil básico + AHF) y al terminar
sugiere completar el resto. NO entra en la primera story: el llenado de las secciones APP/APNP (solo su
estructura visible), signos vitales como serie clínica, exploración física, cuestionarios por especialidad,
nada del compartir (E3/E4).

## Catálogos (en las palabras de Saúl)

### Perfil del paciente
| Attribute | In their words | Sensitive? | Notes / [ASSUMPTION] |
|---|---|---|---|
| fecha de nacimiento | "fecha de nacimiento" | sí | los formatos de farmacia del corpus la imprimen (junto con la edad) [VERIFIED 2026-10-18 fotos]; de ella se deriva la edad mostrada; se corrige, no "cambia" |
| peso actual | "peso actual" | sí | NOM-004 6.1.2 lo pide en la exploración física ("peso y talla") [VERIFIED 2026-10-19]; **cambia con el tiempo** → [ASSUMPTION] se guarda como medición con fecha y el perfil muestra la última (Q1) |
| estatura | "estatura" | sí | ídem 6.1.2; estable en adultos pero no inmutable → misma mecánica que peso (Q1) |
| sexo | — no lo pidió | sí | parte de la ficha de identificación (NOM-004 6.1.1) y de rangos clínicos; **propuesta del harness** con "prefiero no decir" (Q4) |
| alergias a medicamentos | — no lo pidió | sí | APP según NOM-004 6.1.1, pero es LA pregunta de toda consulta y de toda receta segura; **propuesta del harness** como campo simple (Q4) |

### Antecedente familiar (AHF)
| Attribute | In their words | Sensitive? | Notes / [ASSUMPTION] |
|---|---|---|---|
| condición | "diabetes o cáncer en la familia…" | sí | lista corta de condiciones frecuentes + "otra" libre (Q2); la nota IMSS del corpus trae sección AHF explícita [VERIFIED 2026-10-18 fotos] |
| parentesco(s) con línea | "los médicos suelen ser más específicos… si el cáncer fue en abuelo paterno o materno" (2026-10-19) | sí | madre/padre/abuela-o **materna o paterna**/hermana-o/otro; una condición puede tener varios parentescos. La práctica clínica registra 3 generaciones separando línea materna y paterna [VERIFIED 2026-10-19, memory/research.md § anamnesis] |
| edad al diagnóstico del familiar | — | sí | opcional; los cuestionarios oncológicos la piden junto con la línea [VERIFIED 2026-10-19 research.md] — en prototipo v2 como nota por condición |

- **Relations:** paciente → perfil (1→1) · perfil → medición de peso/estatura (1→0..N, con fecha; Q1) ·
  paciente → antecedente familiar (1→0..N, condición + parentescos[])
- **States / lifecycle:** onboarding `ofrecido → completado | omitido` (se ofrece **una sola vez**; omitido no se
  vuelve a forzar, el perfil queda editable desde su pantalla); perfil `vacío → parcial → completo` — parcial es
  un estado legítimo, no un error.
- **What they explicitly do NOT want:** (del encuadre) nada antes del consentimiento; nada que bloquee el primer
  uso — [ASSUMPTION a confirmar en Q3: todo omitible].

## Glosario
| Their word | Meaning here | Never call it |
|---|---|---|
| antecedentes familiares | condiciones de salud en la familia directa (AHF) | "heredo-familiares" en la UI (tecnicismo), historia clínica |
| perfil | los datos básicos del paciente (nacimiento, sexo, peso, estatura, alergias; y trabajo desde FR-028 Story C) | ficha de identificación, demographics |
| onboarding | la única vez que la app pregunta el perfil al entrar | wizard, setup |

## Procesos (who / when / with whom → future FRs)
| Who (role) | Does what | When / trigger | With whom | Exceptional paths |
|---|---|---|---|---|
| paciente | acepta el consentimiento (ya existe, PR #1) | al crear la cuenta | — | — |
| sistema | ofrece el onboarding de perfil, una sola vez | inmediatamente después del consentimiento | — | "Ahora no" → directo al expediente, sin castigo ni re-pregunta |
| paciente | llena u omite cada paso (datos básicos → AHF) y confirma en un resumen | durante el onboarding | — | fecha futura rechazada; valores fuera de rango plausible avisados |
| paciente | completa/corrige el perfil después | cuando quiera, desde "Mi perfil" | — | — |
| sistema (futuro, E5) | usa AHF para avisos proactivos con fuente | FR-021 ("AHF de diabetes sin tamizaje registrado") | — | fuera de esta rebanada |

## El perfil médico por secciones (Saúl Pérez, 2026-10-19 — segunda ronda del gate)

Saúl amplió el pedido con más datos valiosos de su experiencia real: **fracturas** ("en mi caso también luego me
preguntan si he tenido fracturas"), **enfermedades pasadas como hepatitis**, **enfermedad crónica que el paciente
reconoce directamente**, y pidió **más especificidad en AHF** ("si el cáncer fue en abuelo paterno o materno, lo
mismo con la diabetes"). Él mismo planteó la duda correcta: ¿es mucho para el onboarding? ¿mejor que al terminar
el perfil se le sugiera añadir datos adicionales? Y pidió investigar primero qué datos son relevantes para los
médicos, no solo los generales (urólogo, proctólogo, otorrino…). Conclusión: el feature es un **"perfil médico"
con secciones**, y el onboarding es solo su puerta de entrada mínima.

La estructura no hay que inventarla: es la **anamnesis estándar** que la NOM-004 (6.1.1) exige al médico y que
las guías de semiología detallan [VERIFIED 2026-10-19, memory/research.md § anamnesis]:

| Sección del perfil médico | Qué guarda (en términos del paciente) | ¿En el onboarding? |
|---|---|---|
| Perfil básico (ficha de identificación) | nacimiento, sexo, peso, estatura | **sí** |
| Antecedentes familiares (AHF) | condición + parentesco con línea materna/paterna, edad al diagnóstico opcional | **sí** |
| Alergias | a medicamentos, alimentos u otras sustancias | **sí** (propuesta Q4: es lo primero que preguntan) |
| Enfermedades crónicas (APP) | las que el paciente reconoce directamente (diabetes, hipertensión…) | no — sugerida al terminar |
| Enfermedades pasadas e infecciosas (APP) | hepatitis, varicela, COVID grave… con la edad que tenía o el año (rebanada FR-028, ronda 8) | no — sugerida |
| Cirugías y hospitalizaciones (APP) | qué, cuándo, complicaciones | no — sugerida |
| Fracturas y lesiones (APP traumáticos) | qué hueso/lesión, cuándo, secuelas | no — sugerida |
| Transfusiones y grupo sanguíneo (APP) | fecha, motivo, reacción; tipo de sangre | no — sugerida |
| Hábitos (APNP) | tabaco, alcohol, ejercicio, vacunación | no — sugerida |

- **Mecánica propuesta:** el onboarding termina (o se omite) → "Mi perfil médico" muestra TODAS las secciones con
  su estado (vacía/parcial) y una invitación no intrusiva a completarlas. El llenado es progresivo y siempre
  opcional (Q3 respondida: **todo omitible** — Saúl Pérez, 2026-10-19). A futuro, **FR-022 ya existe en el PRD**
  ("recibir preguntas de la IA para completar registros incompletos"): la IA es el mecanismo natural para sugerir
  la siguiente sección útil.
- **Especialidades (urólogo, proctólogo, otorrino…):** el tronco anterior es común a todas; lo específico por
  especialidad es el **"interrogatorio por aparatos y sistemas"** (también en NOM-004 6.1.1) — preguntas dirigidas
  por sistema (urinario, digestivo, ORL…). Los cuestionarios validados por especialidad son una capa futura: llegan
  mejor vía el médico por el enlace (E4, FR-017) o vía la IA (FR-022), no cargando el perfil inicial. Se registra
  como catálogo futuro, no se modela ahora.

## Encaje regulatorio y sensibilidad
- **NOM-004-SSA3-2012, 6.1.1** (interrogatorio mínimo de la historia clínica): ficha de identificación,
  antecedentes **heredo-familiares**, personales patológicos y no patológicos; **6.1.2** (exploración física):
  signos vitales, **peso y talla** [VERIFIED 2026-10-19, texto oficial DOF — memory/research.md]. GlobalHealth no
  es el expediente del prestador, pero capturar exactamente lo que el médico va a preguntar es el valor de O6.
- **LFPDPPP art. 3-VI**: todo esto es dato sensible; los AHF además son **datos de salud de terceros (familiares)
  aportados por el titular** — mismo cifrado en reposo y consentimiento ya resueltos (D13/D16, NFR-001/NFR-004);
  minimización: por eso todo es opcional y omitible.

## Encaje en el PRD (cerrado el 2026-10-19)
- **FR-008 ya existía** ("registrar historial familiar: parentesco + condición", M, O6) y US-05 es su story: esta
  rebanada la implementa con la especificidad de línea, no la duplica.
- **FR-027** (épica E2, US-17): onboarding de perfil básico post-consentimiento, omitible, editable después, con
  la pantalla de secciones visible. **FR-028** (épica E2, US-18): llenado progresivo de las secciones APP/APNP —
  story siguiente. La primera story con prototipo cubre FR-027 + FR-008.

## Open questions (max 4) — el gate del discovery
1. ~~**Peso/estatura: ¿valor único que se sobreescribe, o medición con fecha?**~~ **RESPONDIDA (Saúl Pérez,
   2026-10-19): medición con fecha** mostrando la última — un peso de hace 3 años presentado como "actual"
   desinforma al médico; el historial graficable queda para después.
2. ~~**AHF: ¿cómo se captura?**~~ **RESPONDIDA en dirección (Saúl Pérez, 2026-10-19):** estructurada y con MÁS
   especificidad que la propuesta inicial — la línea importa ("si el cáncer fue en abuelo paterno o materno").
   Prototipo v2: condición + parentescos con línea materna/paterna + nota opcional (edad al diagnóstico). Queda
   validar el v2 clickeando.
3. ~~**¿Todo omitible?**~~ **RESPONDIDA (Saúl Pérez, 2026-10-19): sí, todo omitible** — "Ahora no" por paso y
   global, perfil editable después, sin re-preguntar.
4. ~~**¿Qué entrega la primera story?**~~ **RESPONDIDA (Saúl Pérez, 2026-10-19): la recomendación** — onboarding
   mínimo (perfil básico + AHF + alergias) **+ la pantalla "Mi perfil médico" con todas las secciones visibles
   pero vacías** (FR-027); el llenado de APP/APNP (crónicas, hepatitis, fracturas, cirugías, transfusiones,
   hábitos) es la story siguiente (FR-028), y las preguntas por especialidad llegan vía E4/FR-022. Sexo y alergias
   quedaron dentro (no los recortó al validar el prototipo).

---

# Dominio — GlobalHealth · rebanada "perfil médico por secciones (llenado, FR-028)"

Date: 2026-10-19 · Interviewed: Saúl Pérez (author, con sombrero de stakeholder; pidió "procede con 028" tras
archivar onboarding-perfil) · Método: borrador 0 desde memory/research.md § anamnesis, corregido en 5 rondas (la
ronda 5 no añadió nada) + ronda 6 al clickear el prototipo v1: hábitos crece (research.md § hábitos) + ronda 7: ocupación,
movimiento del día y sueño (research.md § ocupación) · Status: **agreed para la Story A — gate cerrado el 2026-10-20: Saúl Pérez navegó el prototipo en 4
versiones (rondas 6–8 salieron de clickearlo) y respondió "procede con la story a"**. La pregunta 2 (borrar un
diagnóstico enlazado) solo toca la Story B y queda abierta hasta entonces
Prototipo: **`product/prototipos/perfil-secciones.html`** (se abre localmente en el navegador, sin copia hospedada;
toggle "Ver criterios" con AC A-n / B-n / C-n; v2 con hábitos ampliados; v3 con trabajo, movimiento del día y sueño; v4 con "cuándo" por edad o etapa).
Alcance: llenar las 6 secciones que el PR #16 dejó visibles y vacías. NO entra: vacunación (catálogo propio,
futuro), otras sustancias, alimentación, cuestionarios por especialidad (E4/FR-022), enlaces entre
registros de secciones distintas, enlace tratamiento↔medicinas de receta.

## Partición en stories (Saúl Pérez, ronda 3; rehecha en la ronda 6)
- **Story A — eventos:** enfermedades pasadas e infecciosas, cirugías y hospitalizaciones, fracturas y lesiones,
  transfusiones + grupo sanguíneo, y el mecanismo "ninguna" común a todas (4 de las 6 tarjetas cobran vida). **✅ Entregada en el PR #20 (2026-10-20); spec en `openspec/specs/records/patient-profile/spec.md`.**
- **Story B — crónicas:** con enlace opcional al diagnóstico del expediente. **✅ Entregada en el PR #26 (2026-10-20); spec en `openspec/specs/records/patient-profile/spec.md` (B-5 en `records/clinical-records`).**
- **Story C — hábitos + trabajo:** cuestionario con lista anidada (ejercicio), movimiento del día y sueño, más
  el bloque "Trabajo" del Perfil básico. Se separó de B en la ronda 6 al crecer: no comparte forma con crónicas.

## Catálogos (en las palabras de Saúl / del borrador que aceptó)

Mecánica común a las secciones de lista (todas salvo hábitos):
- **Estado de la sección** (ronda 2, "Sí, por sección"): `sin llenar → ninguna (negado) → con registros`. "Ninguna"
  solo se marca sin registros; agregar uno lo quita. Motivo: el médico y la IA deben distinguir "no ha pasado"
  de "no lo ha contado" (la historia clínica escribe "quirúrgicos: negados").
- **"Cuándo"** (ronda 1, corregida en la ronda 8): se pregunta **como el médico** — "¿cuántos años tenías?" o
  "¿ibas en la primaria o en la secundaria?" (Saúl Pérez: "el médico no pregunta en qué año crees que te dio…
  para calcular el año"). El paciente contesta con **edad**, **etapa** (antes de la primaria · primaria ·
  secundaria · prepa), **año** si lo sabe, o "No recuerdo". Se **guarda lo que dijo** (tipo + valor) y el año
  aproximado se **calcula al mostrarlo** con la fecha de nacimiento del perfil: si el paciente la corrige, el año
  se recalcula; si la omitió en el onboarding, solo se muestra la edad o la etapa. Las edades por etapa
  (primaria 6–11, secundaria 12–14, prepa 15–17) son [ASSUMPTION] y solo sirven para estimar. Validación: edad no
  mayor que la actual; año entre el nacimiento y hoy. NO fecha exacta — difiere a propósito de `occurred_on` de
  los registros del expediente.
- **Cruces entre secciones** (ronda 3, "Marca sí/no, sin enlace"): una fractura dice "¿requirió cirugía?" y una
  enfermedad pasada "¿requirió hospitalización?"; si el paciente quiere el detalle, lo registra en Cirugías. Sin
  modelo de enlaces entre registros.

### Enfermedad pasada e infecciosa (APP)
| Attribute | Notes |
|---|---|
| condición | lista frecuente (varicela, sarampión, paperas, rubéola, hepatitis A/B/C, COVID-19 grave, dengue, tuberculosis) + "otra"; **requerido** |
| cuándo | mecánica común |
| ¿requirió hospitalización? | sí / no / no sé |
| secuelas, nota | texto opcional |
(ronda 5: "nada más"; tratamiento recibido descartado)

### Cirugía u hospitalización (APP quirúrgicos)
| Attribute | Notes |
|---|---|
| tipo | cirugía / hospitalización sin cirugía |
| nombre ("qué fue") | **requerido** |
| cuándo, motivo, complicaciones | borrador aceptado |
| hospital o lugar | ronda 2 (sirve para pedir el expediente al hospital) |
| médico que operó o atendió | ronda 2 — dato de un tercero, opcional |
| ¿reacción a la anestesia? + qué pasó | ronda 2 |
| material implantado | ronda 4: "en fracturas y cirugías" (placa, prótesis, marcapasos; lo pregunta la resonancia) |

### Fractura o lesión (APP traumáticos)
| Attribute | Notes |
|---|---|
| qué hueso o lesión | **requerido** |
| lado | izquierdo / derecho / ambos / no aplica (ronda 3) |
| cuándo, ¿requirió cirugía?, secuelas | borrador aceptado |
| material implantado | ronda 3 |

### Transfusión y grupo sanguíneo (APP transfusionales)
| Attribute | Notes |
|---|---|
| cuándo, motivo, ¿hubo reacción? + qué pasó | borrador aceptado |
| qué se transfundió | sangre / plaquetas / plasma / no sé (ronda 3) |
| hospital o lugar | ronda 3 |
| **grupo sanguíneo** | **un solo dato del paciente**, no por transfusión: A/B/AB/O con Rh ±, o "no lo sé" (ronda 5: solo el valor; el estudio que lo respalde va como adjunto del expediente) |

### Enfermedad crónica (APP crónico-degenerativos) — Story B
| Attribute | Notes |
|---|---|
| condición | lista frecuente (diabetes tipo 2, hipertensión, asma, hipotiroidismo, colesterol alto, EPOC, artritis, epilepsia) + **salud mental** (depresión, ansiedad, trastorno bipolar) + "otra"; **requerido** |
| categoría sensible | ronda 4: las de salud mental se guardan **marcadas como "salud mental"** para que FR-014 (enlaces por categoría) las oculte sin migrar datos |
| desde cuándo | mecánica "cuándo" (edad, etapa o año) |
| estado | **Activa / Ya no la tengo** + hasta cuándo, con la mecánica "cuándo" (ronda 2; "controlada" es juicio clínico, no se pide al paciente) |
| tratamiento actual | texto libre opcional (ronda 2; el enlace a medicinas de receta, después) |
| diagnóstico que la respalda | **enlace opcional** a un diagnóstico del expediente (ronda 1: "aparte, enlazable") |
| nota | texto opcional |

### Hábitos (APNP + tabaquismo) — Story C, cuestionario (no lista; sin "ninguna": cada hábito tiene "Nunca")
Ronda 6 (Saúl Pérez al clickear el prototipo v1: "hábitos puede o debe crecer más… consumo de alcohol puede ser
fines de semana… me expongo a humo de cigarro dos veces por semana… varios ejercicios con su propia frecuencia",
y pidió investigar cómo se maneja). La evidencia (research.md § hábitos) dice que justo frecuencia, cantidad,
estado, fechas y humo ajeno son lo que los campos estructurados de los expedientes no capturan.

| Hábito | Respuesta |
|---|---|
| alcohol | **nunca / lo dejé (a qué edad; ronda 8) / actual**. Si actual, las 3 preguntas del **AUDIT-C** con su escala: frecuencia (una vez al mes o menos · 2–4 al mes · 2–3 por semana · 4+ por semana), bebidas en un día típico (1–2 · 3–4 · 5–6 · 7–9 · 10+), frecuencia de 6 o más en una ocasión (nunca · menos de una vez al mes · cada mes · cada semana · diario o casi) + marca "sobre todo fines de semana". **Sin puntaje** (C-6) |
| tabaco | nunca / antes / actual + cigarros al día + a qué edad empezó + a qué edad lo dejó (si "antes") — ronda 8: edad, no año |
| vapeador | nunca / antes / actual |
| humo de tabaco ajeno | **hábito propio** (ronda 6): dónde (casa · trabajo o escuela · otro lugar, varios) + días por semana, o "no me expongo" |
| humo de leña | nunca / antes / actual + años aprox.; riesgo [VERIFIED] (research.md § humo de leña), forma de captura [ASSUMPTION] |
| ejercicio | **lista de actividades** (caminar, correr, bicicleta, nadar, pesas o gimnasio, fútbol u otro deporte, yoga o pilates, baile, otra), cada una con días por semana + minutos por vez (forma del Exercise Vital Sign, por actividad); se muestra el total semanal **sin veredicto** contra la OMS. El tipo permite distinguir aeróbico de fuerza (OMS 2020) sin preguntar intensidad |

| movimiento del día | ronda 7, forma del GPAQ (OMS): en el trabajo o actividad principal (casi todo sentado · de pie o caminando · esfuerzo físico pesado), desplazamiento activo (caminar o bici para ir a algún lado: sí/no + días por semana) y horas sentado al día. **No se suma al total de ejercicio** (paradoja de la actividad física, research.md § ocupación) |
| sueño | ronda 7 (antes fuera): horas por noche + ¿te cuesta dormir o te despiertas? (nunca · a veces · casi siempre). Sin diagnóstico ni puntaje |

### Trabajo — se suma al Perfil básico (Story C)
Ronda 7 (Saúl Pérez: "también te preguntan por tu profesión… paso mucho tiempo sentado… hay oficios que implican
movimiento diario"). Las plantillas mexicanas de historia clínica ponen la ocupación en la ficha de
identificación; NIOSH (Occupational Data for Health) define el mínimo: situación laboral, trabajo actual y el de
más años (research.md § ocupación). Decisión: va en el **Perfil básico**, no en Hábitos.
| Attribute | Notes |
|---|---|
| situación laboral | trabajo · busco trabajo · jubilado o pensionado · hogar · estudio |
| a qué te dedicas | texto libre (NIOSH tiene catálogo con traducción al español; codificar queda fuera) |
| el trabajo de más años | texto libre, si es otro (explica exposiciones antiguas) |
| exposiciones | polvo · químicos o solventes · ruido fuerte · cargar peso (varias) o "nada de esto" |
| turno | de día · de noche · rotativo — [ASSUMPTION] su relevancia (sueño); no está en el estándar NIOSH consultado |

- **Regla C-6 (objeción del harness, aceptada por Saúl Pérez):** la app captura con la forma de los
  instrumentos, pero NO calcula puntajes (AUDIT-C), riesgos ni "cumples / no cumples": los cortes varían por fuente
  y es juicio clínico; cualquier interpretación futura es salida de la IA con fuente y leyenda (NFR-008).

- **Relations:** paciente → registro de sección (1→0..N, con tipo de sección) · paciente → estado por sección
  (ninguna sí/no) · paciente → grupo sanguíneo (1→0..1) · paciente → hábitos (1→0..1) → actividad física (1→0..N) · perfil → trabajo (1→0..1) · crónica → diagnóstico
  del expediente (N→0..1, opcional; el diagnóstico NO depende de la crónica).
- **States / lifecycle:** sección `sin llenar → ninguna → con registros` (ver arriba); crónica `activa → ya no la
  tengo` (reversible: el paciente corrige). Los registros de eventos no tienen estado: son pasado.
- **What they explicitly do NOT want (esta rebanada):** vacunación, otras sustancias, alimentación/sueño
  (ronda 1: "nada más por ahora"; el sueño y el sedentarismo entraron en la ronda 7); enlaces entre registros de secciones distintas (ronda 3); tratamiento
  enlazado a recetas (ronda 2).

## Glosario (se suma al de la rebanada onboarding)
| Their word | Meaning here | Never call it |
|---|---|---|
| secciones / historial | las 6 secciones de antecedentes personales del perfil médico | APP/APNP en la UI (tecnicismo), anamnesis |
| ninguna | el paciente declara que no ha tenido nada de esa sección | negados, N/A, vacío |
| crónica | enfermedad que el paciente tiene o tuvo de forma duradera, aunque no tenga el papel del diagnóstico | diagnóstico (eso es el registro con fecha del expediente) |
| ya no la tengo | crónica que se resolvió | remisión, inactiva, curada |

## Procesos (who / when / with whom → future FRs)
| Who | Does what | When / trigger | Exceptional paths |
|---|---|---|---|
| paciente | abre una sección desde "Mi perfil médico" y agrega, corrige o elimina registros | cuando quiera | edad mayor que la actual o año fuera de su vida rechazados; "hasta" antes de "desde" rechazado; registro vacío no se guarda |
| paciente | marca "No he tenido ninguna" | sección sin registros | agregar un registro después la quita |
| paciente | elige su grupo sanguíneo | en la sección de transfusiones | "No lo sé" es un valor válido |
| paciente | enlaza una crónica a un diagnóstico del expediente | al registrar o editar la crónica | si el diagnóstico se borra, la crónica queda sin enlace (no se borra) y la confirmación de borrado lo avisa (Saúl Pérez, 2026-10-20) |
| sistema (futuro E5) | usa crónicas, hábitos (tabaco, humo ajeno, leña, AUDIT-C) y "ninguna" para avisos con fuente | FR-021 | fuera de esta rebanada; cualquier puntaje o riesgo es salida de la IA con fuente (NFR-008) |

## Datos sensibles
Todo es dato sensible (LFPDPPP art. 3-VI), mismo cifrado en reposo (D13) y detrás del consentimiento (D16).
Salud mental lleva además su categoría para FR-014. Médico y hospital son datos de terceros aportados por el
titular, como los AHF: opcionales por minimización.

## Open questions (max 4) — el gate del discovery
1. ~~**¿El prototipo refleja lo que respondiste?**~~ **RESPONDIDA (Saúl Pérez, 2026-10-20):** el v1 produjo la
   ronda 6 (hábitos), el v2 la 7 (trabajo, movimiento del día, sueño) y el v3 la 8 ("cuándo" por edad); sobre el
   v4: "procede con la story a".
2. ~~**Borrar un diagnóstico enlazado**~~ **RESPONDIDA (Saúl Pérez, 2026-10-20: "Se queda y se avisa"):** la
   crónica conserva su registro y pierde el enlace, y la confirmación de borrado del diagnóstico avisa cuáles
   crónicas respalda (criterio B-5 de perfil-cronicas).
