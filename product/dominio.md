# Dominio — GlobalHealth · rebanada "receta a la mexicana"

Date: 2026-10-18 · Interviewed: Saúl Pérez (author, haciendo de paciente-interesado; mensaje del 2026-10-12 tras
probar el expediente v1) · Evidencia: 74 fotos reales de documentos propios aportadas por Saúl el 2026-10-18
(§ Evidencia empírica; las fotos NO entran al repo, aquí solo su estructura) · Status: **draft — gate pendiente:
validar el prototipo y las 4 preguntas abiertas**
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

## Datos sensibles y retención
| Data | Who may see it | Kept for | Who can erase it | Regulation |
|---|---|---|---|---|
| foto de la receta + campos | el paciente; profesional solo vía enlace activo (E3/E4) | mientras viva la cuenta | el paciente (ARCO) | LFPDPPP; cifrado en reposo ya probado (D13/D16) |
| contenido enviado al OCR/IA | el proveedor NO lo retiene ni entrena | n/a | n/a | NFR-005, proveedor pendiente (Q4) |

## Open questions (max 4) — el gate del discovery
1. **Vigencia/eliminación:** sin vigencia impresa, ¿cómo deja de estar "activa" una receta para los futuros
   recordatorios? A (recomendada): el paciente la archiva manualmente / B: vigencia opcional derivada de la
   duración del tratamiento si la IA la infiere, editable. *Evidencia fotos: la duración por medicina casi siempre
   está escrita → B es viable como derivado, A sigue siendo el default simple.*
2. **Frecuencia de toma:** ¿se captura desde ya por medicina (campo opcional) para que FR-025 no exija otra
   migración, o se pospone? A (recomendada): campo opcional ahora. *Evidencia fotos: la frecuencia viene escrita en
   casi todas las recetas — capturarla no añade fricción.*
3. **El tipo "diagnóstico" de la v1:** ¿desaparece como tipo de registro (y FR-005 pasa a "nota/diagnóstico opcional
   en la receta"), o se conserva además como entrada suelta del expediente? A: se conserva como entrada opcional
   suelta (hay diagnósticos sin receta) / B: solo campo de la receta. *Evidencia fotos: existen notas clínicas y
   diagnósticos fuera de recetas → refuerza A.*
4. **Proveedor OCR/IA:** la captura foto-primero depende de decidir NFR-005 (cero retención). ¿Se decide en el
   tech-brief antes de la story de OCR, dejando receta-mexicana (modelo + captura manual + foto adjunta) como
   primera story sin IA? A (recomendada): sí, dos stories. *Evidencia fotos: ~mitad del corpus es manuscrito, con
   giros y retomas → el pipeline de lectura es un proyecto en sí (visión-IA/HTR + clasificador + dedupe), no un
   añadido; separa stories con más razón.*
