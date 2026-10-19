# Dominio — GlobalHealth · rebanada "receta a la mexicana"

Date: 2026-10-18 · Interviewed: Saúl Pérez (author, haciendo de paciente-interesado; mensaje del 2026-10-12 tras
probar el expediente v1) · Status: **draft — gate pendiente: validar el prototipo y las 4 preguntas abiertas**
Alcance: SOLO el dominio de la receta y su captura. El resto del producto ya está en product/prd.md; esta rebanada
corrige el modelo que la v1 del expediente asumió mal.

## Catálogos (en las palabras de Saúl)

### Receta
| Attribute | In their words | Sensitive? | Notes / [ASSUMPTION] |
|---|---|---|---|
| medicinas (varias) | "la receta dice las medicinas" | sí | una receta ⇢ N medicinas [VERIFIED 2026-10-12] |
| fecha de expedición | "tiene la fecha en que se expide" | sí (metadato) | [VERIFIED] |
| nombre del paciente | "y el nombre del paciente" | sí | en la app es el dueño de la cuenta; se guarda si la foto lo trae [ASSUMPTION] |
| médico que la expide | implícito en "quién te la dio" | sí | [ASSUMPTION: la receta impresa lo trae casi siempre] |
| diagnóstico | "no suele venir con diagnóstico… te lo dicen con la voz" | sí | **campo opcional de la receta**, no entidad aparte [VERIFIED] |
| foto original | "subir una foto de la receta… o usar la cámara" | sí | el documento fuente queda adjunto al registro [VERIFIED] |

- **Relations:** receta → medicinas (1→N) · receta → foto/adjunto (1→0..N) · receta → diagnóstico (campo, 0..1)
- **States / lifecycle:** [ASSUMPTION] emitida → (surtida) → vencida/histórica — la receta mexicana NO trae vigencia
  impresa [VERIFIED]; cualquier vigencia es dato derivado o capturado aparte, nunca obligatorio. Pregunta abierta Q1.
- **What they explicitly do NOT want:** vigencia inicio/fin obligatoria; diagnóstico como registro separado
  obligatorio; capturar a mano como ÚNICO camino.

### Medicina (dentro de una receta)
| Attribute | In their words | Sensitive? | Notes |
|---|---|---|---|
| nombre | "las medicinas" | sí | [VERIFIED] |
| dosis / indicación | cómo tomarla | sí | [VERIFIED, prototipo validado a medias 2026-10-12] |
| frecuencia / horarios de toma | — no lo dijo | sí | [ASSUMPTION] la necesitará FR-025 (recordatorios); pregunta abierta Q2 |

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
| sistema (OCR+IA) | lee la foto y prellena medicinas, fecha, médico | tras subir la foto | proveedor IA (NFR-005: cero retención) | lectura parcial → campos vacíos editables, nunca inventados |
| paciente | confirma/corrige y guarda; puede capturar a mano sin foto | tras la lectura | — | — |

## Datos sensibles y retención
| Data | Who may see it | Kept for | Who can erase it | Regulation |
|---|---|---|---|---|
| foto de la receta + campos | el paciente; profesional solo vía enlace activo (E3/E4) | mientras viva la cuenta | el paciente (ARCO) | LFPDPPP; cifrado en reposo ya probado (D13/D16) |
| contenido enviado al OCR/IA | el proveedor NO lo retiene ni entrena | n/a | n/a | NFR-005, proveedor pendiente (Q4) |

## Open questions (max 4) — el gate del discovery
1. **Vigencia/eliminación:** sin vigencia impresa, ¿cómo deja de estar "activa" una receta para los futuros
   recordatorios? A (recomendada): el paciente la archiva manualmente / B: vigencia opcional derivada de la
   duración del tratamiento si la IA la infiere, editable.
2. **Frecuencia de toma:** ¿se captura desde ya por medicina (campo opcional) para que FR-025 no exija otra
   migración, o se pospone? A (recomendada): campo opcional ahora.
3. **El tipo "diagnóstico" de la v1:** ¿desaparece como tipo de registro (y FR-005 pasa a "nota/diagnóstico opcional
   en la receta"), o se conserva además como entrada suelta del expediente? A: se conserva como entrada opcional
   suelta (hay diagnósticos sin receta) / B: solo campo de la receta.
4. **Proveedor OCR/IA:** la captura foto-primero depende de decidir NFR-005 (cero retención). ¿Se decide en el
   tech-brief antes de la story de OCR, dejando receta-mexicana (modelo + captura manual + foto adjunta) como
   primera story sin IA? A (recomendada): sí, dos stories.
