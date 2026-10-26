## Hábitos: cómo se capturan y dónde fallan los expedientes (verificado 2026-10-19) <a id="habitos"></a>
- **Fact (fallas de captura estructurada):** en el módulo de historia social de un expediente electrónico, de 500
  registros de alcohol el texto libre se usó porque los campos estructurados no permitían describir frecuencia
  (75 %), cantidad (22 %) ni estado (18 %); la frecuencia escrita era sobre todo "ocasional" (61 %). De 525 registros
  de tabaco, el texto libre cubría cantidad (23.2 %), frecuencia (26.9 %), fechas de inicio o de dejarlo (28.2 %)
  y exposición al humo ajeno (17.9 %). Un estudio posterior concluye que los campos estructurados solos no dan el
  historial de tabaco completo, sobre todo en lo temporal.
- **Source:** Chen & Garcia-Webb, Appl Clin Inform 2014;5(2):402-415, https://pmc.ncbi.nlm.nih.gov/articles/PMC4081744
  · estudio de 525 registros de tabaco, https://pmc.ncbi.nlm.nih.gov/articles/PMC4419995 · Wang et al. (con
  Melton), AMIA 2016, https://experts.umn.edu/en/publications/investigating-longitudinal-tobacco-use-information-from-social-hi/
  · consulted 2026-10-19
- **Confidence:** [VERIFIED] (estudios de una sola institución, 2014–2017; los porcentajes no se generalizan, la
  dirección sí).

- **Fact (alcohol, AUDIT-C):** el tamizaje breve estándar son las 3 primeras preguntas del AUDIT (OMS): frecuencia
  de consumo, bebidas en un día típico y frecuencia de 6 o más bebidas en una ocasión, cada una de 0 a 4 puntos
  (total 0–12). Existe en español y en LOINC con traducción es-MX. Los puntos de corte VARÍAN por fuente (≥3
  mujeres / ≥4 hombres; ≥5; >4) → no se fija ninguno en la app. No se encontró validación específica en México.
- **Source:** AUDIT-C en español, California DHCS https://www.dhcs.ca.gov/Documents/AUDIT-C%20Spanish.pdf · LOINC
  68520-6 https://loinc.org/68520-6 · El Centro, U. Miami https://elcentro.sonhs.miami.edu/research/measures-library/audit-c/index.html
  · consulted 2026-10-19
- **Confidence:** [VERIFIED] las preguntas y escalas; [NO VERIFICADO] la "bebida estándar" mexicana (13 g solo
  en fuente secundaria, FISAC vía Publimetro 2023) → la UI describe la bebida por ejemplos, no por gramos.

- **Fact (humo ajeno):** las encuestas lo miden por lugar (casa, trabajo, lugares públicos) y frecuencia; LOINC
  tiene la pregunta en español de México por lugar y horas al día. La ONC reporta que al menos dos proveedores
  grandes de expedientes la incluyen, pero con uso limitado en producción.
- **Source:** EMTA Argentina https://www.entrerios.gov.ar/dgec/wp-content/uploads/2017/05/emta_preliminar.pdf ·
  LOINC 63956-7 https://loinc.org/63956-7 · ONC USCDI https://isp.healthit.gov/uscdi-data/secondhand-smoke-exposure
  · consulted 2026-10-19
- **Confidence:** [VERIFIED]; no se encontró el cuestionario textual de la ENCODAT (México).

- **Fact (actividad física):** el Exercise Vital Sign de Kaiser Permanente hace 2 preguntas en la consulta (días
  por semana de actividad moderada a intensa × minutos esos días = minutos por semana), con validez aparente y
  discriminante en ~1.8 millones de adultos. La OMS (nov 2020) recomienda 150–300 min/semana de actividad
  moderada (o 75–150 vigorosa) MÁS fortalecimiento muscular al menos 2 días, y limitar el sedentarismo.
- **Source:** Coleman et al., Med Sci Sports Exerc 2012, https://meps.ipums.org/meps/resources/Coleman_et_al_2012.pdf
  · CDC Prev Chronic Dis 2014, https://cdc.gov/pcd/issues/2014/14_0196.htm · OPS/OMS 2020-11-26,
  https://www.paho.org/es/noticias/26-11-2020-cada-movimiento-cuenta-para-mejorar-salud-dice-oms · consulted 2026-10-19
- **Confidence:** [VERIFIED]. La comparación del EVS contra acelerómetro (Kuntz 2021, PMC8154650) no se leyó.
- **Re-check if:** se diseña un aviso FR-021 sobre hábitos (ahí fijar fuentes y cortes) o se agrega sedentarismo.

## Vapeador y edad de inicio del alcohol (verificado 2026-10-21) <a id="vapeo-inicio"></a>
- **Fact (vapeador):** no hay una medida validada de "vapeadores o pods por semana" (los dispositivos varían:
  desechables, pods, recargables). El estudio poblacional PATH (EE. UU.) clasifica el uso actual por "todos los días /
  algunos días" y, en quien usa algunos días, por **días usados de los últimos 30** (infrecuente 0–2, moderado >2 sin
  ser diario, diario). El autorreporte "veces al día" (una vez ≈ 15
  caladas o ~10 min) predice las caladas de un contador automático con r = .58, y los usuarios tienen dificultad para
  reportarlo. En México, la ENCODAT 2025 mide el uso de cigarro electrónico en el último mes (2.6 % de 12 a 65 años).
- **Source:** Yingst J et al., Nicotine Tob Res 2020;22(5):699-704, PMID 30365024 (Europe PMC) · PATH Wave 1,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC6693501 (no se pudo abrir: captcha; categorías tomadas del resultado del
  buscador) · ENCODAT 2025, resumen ejecutivo,
  https://encuestas.insp.mx/repositorio/encuestas/ENCODAT2025/doctos/informes/251223_ENCODAT__ResumenEjecutivo.pdf
  (PDF no leído; cifra tomada del resultado del buscador) · consulted 2026-10-21
- **Confidence:** [VERIFIED] Yingst (resumen en Europe PMC); [NOT VERIFIED] las categorías de PATH y la cifra de
  ENCODAT (solo el resultado del buscador, sin abrir la fuente).
- **Fact (alcohol, edad de inicio):** el ítem estándar es la edad del **primer** consumo, sin contar probaditas: LOINC
  63634-0 (PhenX) "About how old were you when you first started drinking, not counting small tastes or sips of
  alcohol", en años; el protocolo vigente PhenX 30202 viene de la NSDUH 2015, se pregunta solo a quien ha bebido, y
  PhenX lo marca como información sensible. No se encontró pregunta estándar de "edad en que empezó a beber con
  regularidad" ni validación mexicana.
- **Source:** https://www.findacode.com/loinc/63634-0--alc-first-use-age-phenx.html (agregador, leído) ·
  https://phenxtoolkit.org/protocols/view/30202 (no leído; datos del resultado del buscador) · consulted 2026-10-21
- **Confidence:** [NOT VERIFIED en loinc.org] el texto LOINC (leído completo en un agregador, findacode, no en la
  fuente primaria); [NOT VERIFIED] el origen NSDUH de PhenX 30202 (solo el resultado del buscador).
- **Re-check if:** se diseña un aviso FR-021 sobre vapeo o alcohol, o aparece un instrumento mexicano validado.

## "No recuerdo" en preguntas de hábitos (verificado 2026-10-22) <a id="no-recuerdo"></a>
- **Fact (encuestas):** las encuestas de referencia separan "no sabe" de "rechazó", "sin respuesta" y "no aplica", con
  códigos fuera del rango de la respuesta. NHIS 2024: edad de inicio del tabaco (`SMKAGE_A`) 99 = Don't Know, 1.03 %
  de los casos; cigarros al día (`CIGNOW_A`) 0.40 %; años desde que dejó 0.64 %. NSDUH 2023: 994 = DON'T KNOW, 997 =
  REFUSED, 998 = BLANK, 999 = LEGITIMATE SKIP; edad del primer cigarro DK 0.14 %. NHIS y BRFSS los codifica el
  entrevistador ("DO NOT READ"); en la versión web de NCHS RSS-8 el "Don't know" solo aparece en los ítems que lo
  incluyen, por ejemplo uno de recuerdo, seguido de "What is your best guess…?".
- **Fact (AUDIT):** el manual de la OMS (Babor et al. 2001) no tiene opción "no sé" en ningún ítem; la puntuación suma
  todas las respuestas, y el formato autoadministrado "allowing only specific choices" reduce la incertidumbre. La guía
  VA (2004) deja pendiente un AUDIT-C sin completar; no lo calcula con faltantes.
- **Fact (estándares):** HL7 FHIR CodeSystem data-absent-reason: `asked-unknown` "The source was asked but does not know
  the value", `asked-declined`, `not-applicable`, `unknown`. Questionnaire R5: con `enableWhen`, `required` solo aplica
  si la condición se cumple. LOINC 2.82: `LA12688-0` "Don't know", `LA4489-6` "Unknown".
- **Fact (metodología):** en preguntas de actitud ("no tengo opinión") y de voto en un referéndum, no de hechos ni de
  recuerdo, ofrecer esa opción atrae más a quien contesta por escrito o con poco esfuerzo y no mejora la calidad de los
  datos; ofrecerla explícitamente sube por sí solo la abstención (identificación partidista: 12.5 % frente a 1.0 %,
  p. 384) (Krosnick et al. 2002, POQ 66:371-403). Aplicarlo a "No recuerdo" es por analogía [INFERENCE]. Lo que menos
  faltantes dejó en línea fue no ofrecerlo y repreguntar con amabilidad (de Leeuw, Hox y Boevé 2016, resumen).
- **Fact (México):** la NOM-004-SSA3-2012 (6.1.1) pide en el interrogatorio el uso de tabaco, alcohol y otras
  sustancias, pero no dice cómo registrar un dato desconocido.
- **Source:** NHIS 2024 adult codebook https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHIS/2024/adult-codebook.pdf
  · NSDUH 2023 codebook https://www.samhsa.gov/data/system/files/media-puf-file/nsduh-2023-ds0001-info-codebook_v2.pdf
  · BRFSS 2024 https://www.cdc.gov/brfss/questionnaires/pdf-ques/2024-BRFSS-Questionnaire-508.pdf · NCHS RSS-8
  https://www.cdc.gov/nchs/data/rss/round8/questionnaire.pdf · AUDIT (OMS 2001) https://www.paho.org/sites/default/files/Auditmanual_ENG.pdf
  · VA https://www.va.gov/vdl/documents/Clinical/CPRS-Clinical_Reminders/pxrm_1_5_21_setup.pdf · FHIR
  https://terminology.hl7.org/CodeSystem-data-absent-reason.html y https://hl7.org/fhir/R5/questionnaire-definitions.html
  · LOINC vía tx.fhir.org `$lookup` https://tx.fhir.org/r4/CodeSystem/$lookup?system=http://loinc.org&code=LA12688-0 y
  https://tx.fhir.org/r4/CodeSystem/$lookup?system=http://loinc.org&code=LA4489-6 · Krosnick 2002 https://web.stanford.edu/dept/communication/faculty/krosnick/docs/2002/2002%20The%20impact%20of%20no%20opinion%20response%20options%20on%20data%20quality-%20N.pdf
  · de Leeuw 2016 https://research-portal.uu.nl/en/publications/handling-do-not-know-answers-exploring-new-approaches-in-online-a/
  · NOM-004 https://dof.gob.mx/nota_detalle_popup.php?codigo=5272787 · consulted 2026-10-22
- **Confidence:** [VERIFIED] todo lo anterior en la fuente primaria, salvo: de Leeuw 2016 (solo el resumen), Poe et al.
  1988 (citado por Krosnick, no leído), el AUDIT-C de Bush 1998 y el umbral VA ≥5 (fuentes secundarias, no se usan aquí).
  Lo marcado [INFERENCE] no está en ninguna fuente: es la lectura de este proyecto.
- **Consecuencia para la captura (perfil-habitos-completitud) [INFERENCE]:** "No recuerdo" solo en preguntas sobre el
  pasado (edades de inicio y fin; cantidades de "Antes"); nunca en las tres preguntas de frecuencia del alcohol ni en lo
  que describe el presente, que se puede estimar (en NHIS 2024 el "no sabe" de `CIGNOW_A`, cigarros al día de quien
  fuma a diario, es 0.40 %, frente a 1.03 % en `SMKAGE_A`, edad de inicio); guardado como un valor propio, no como un
  número especial, para que "no recuerda" no se confunda con "sin respuesta" ni contamine un promedio.
- **Re-check if:** se mide en uso real que un ítem de la pantalla tiene claramente más "No recuerdo" que los demás que
  lo admiten (señal de que se usa como salida rápida), o se exporta a FHIR (mapear a `asked-unknown`). El ~1 % de NHIS
  no sirve de umbral: allí el "no sabe" no se lee y lo dice el entrevistado por su cuenta, y ofrecer la opción a la
  vista sube la tasa por sí solo (Krosnick 2002, p. 384).

## Ejercicio por actividad, movimiento del día y sueño: preguntas estándar y rangos (verificado 2026-10-26) <a id="actividad-sueno"></a>
- **Fact (duración del sueño):** las encuestas de referencia preguntan **una sola cifra promedio**. NHIS 2024
  `SLPHOURS_A` y BRFSS 2022 `SLEPTIM1`: "On average, how many hours of sleep do you get in a 24-hour period?"; en
  español (NHIS 2024): "En promedio, ¿cuántas horas duerme en un período de 24 horas?" (BRFSS 2020: "…en un periodo
  de 24 horas?"). Ambas en **horas enteras de 1 a 24**: 30 minutos o más suben a la hora siguiente, 29 o menos se
  descartan, y menos de 1 hora se anota como 1. Códigos aparte: NHIS 97 Refused · 98 Not Ascertained · 99 Don't Know (DK
  0.29 %, 94 de 32 629); BRFSS 77 No sabe · 99 Se negó. NHIS tiene un **aviso de verificación, no un bloqueo**, si la
  respuesta es de 1 a 5 horas ("Please verify"). PSQI ítem 4: "During the past month, how many hours of actual sleep did
  you get at night? (This may be different than the number of hours you spent in bed.)", respuesta abierta "HOURS OF
  SLEEP PER NIGHT"; su puntuación admite fracciones (cortes >7, 6–7, 5–6, <5). ENSANUT Continua 2022 (cuestionario de
  actividad física en adultos, "Hábitos de sueño"): "4. Cuántas HORAS en promedio duerme en un día?".
- **Fact (día laboral y día libre):** el MCTQ pregunta los horarios de sueño **por separado en días de trabajo y días
  libres**, porque difieren mucho salvo en los cronotipos más tempranos (Roenneberg 2003). NHANES 2017-2018 lo adoptó
  (`SLD012` días entre semana o de trabajo, `SLD013` fines de semana o días libres), calculado a partir de las horas de
  dormirse y de despertar, **en medias horas de 3 a 13.5**, con "menos de 3 horas" (código 2) y "14 horas o más"
  (código 14) aparte.
- **Fact (sesgo del autorreporte):** en el estudio CARDIA (n = 669, con actígrafo), el sueño medido promedió 6 h y el
  reportado 6.8 h; quien dormía 5 h reportaba ~1.2 h de más, y la correlación fue 0.47 (Lauderdale 2008).
- **Fact (síntoma de insomnio):** NHIS 2024 usa **dos ítems separados**, con recuerdo de 30 días y escala de 4 puntos.
  `SLPFLL_A`: "Durante los últimos 30 días, ¿con qué frecuencia tuvo dificultades para dormirse? ¿Diría que nunca,
  algunos días, casi todos los días o todos los días?". `SLPSTY_A`: "…¿con qué frecuencia tuvo dificultades para
  mantenerse dormido(a)?", con la nota al entrevistador "Include waking up too early". Respuestas: 1 Nunca · 2 Algunos
  días · 3 Casi todos los días · 4 Todos los días, más 7/8/9 aparte. Distribución en 2024: dormirse 43.2 / 38.6 / 9.1 /
  5.9 %; mantenerse dormido 42.4 / 35.1 / 10.8 / 8.4 %; DK ≤0.09 %.
- **Fact (escalas validadas):** todas son **escalas de varios ítems con puntuación**. La ISI está validada en español
  (España, n = 500, α = 0.82; Fernandez-Mendoza 2012). La **Escala Atenas de Insomnio está validada en México**
  (Nenclares Portocarrero y Jiménez-Genchi, Salud Mental 2005;28(5):34-39): 8 reactivos de 0 a 3, α = 0.90, con
  reactivos separados para "Inducción del dormir" y "Despertares durante la noche", y recuerdo de una semana en esa
  validación. PROMIS Sleep Disturbance: últimos 7 días, frecuencia de 5 puntos (never · rarely · sometimes · often ·
  always), ítems separados "I had difficulty falling asleep" y "I had trouble staying asleep" (Yu 2011). El PSQI no
  admite cambios sin permiso escrito de la Universidad de Pittsburgh, y su uso comercial requiere solicitud.
- **Fact (Exercise Vital Sign):** Kaiser hace exactamente dos preguntas: "On average, how many days per week do you
  engage in moderate to strenuous exercise (like a brisk walk)?" y "On average, how many minutes do you engage in
  exercise at this level?". Días de **0 a 7**; minutos en categorías **0, 10, 20, 30, 40, 50, 60, 90, 120 y "150 o
  más"**, para evitar errores de captura. El expediente multiplica ambos y muestra los minutos por semana. **No pregunta
  por fuerza muscular.** Su capacitación pide repreguntar si la respuesta parece irrazonable ("I exercise five hours
  every day"). Es una versión modificada del BRFSS.
- **Fact (BRFSS: precedente de dos actividades):** sección básica de ejercicio (años impares; 2023, y 2019 en español).
  `EXERANY2` pregunta si hizo alguna actividad el mes pasado. Para la actividad principal: `EXRACT12` "¿A qué tipo de
  actividad o ejercicio dedicó más tiempo durante el mes pasado?" (lista de 11 códigos: caminar, correr, jardinería,
  bicicleta, aeróbics, calistenia, elíptica, quehaceres del hogar, pesas, yoga/pilates/tai chi, otra), `EXEROFT1`
  "¿Cuántas veces a la semana o al mes realizó esta actividad durante el pasado mes?" (**veces**, no días: 1–99 por
  semana o 1–99 por mes, con "this is not asking for days" como nota al entrevistador) y `EXERHMM1` "Cuando realizó esta
  actividad, ¿cuántos minutos u horas le dedicó habitualmente?" (H:MM; en el codebook 2023 los valores van de 0:01 a
  9:59). Las mismas tres preguntas se repiten para "el segundo tipo de actividad", con "88 Ninguna otra actividad". La
  fuerza va en una pregunta aparte: `STRENGTH` "¿cuántas veces a la semana o al mes realizó actividad física o
  ejercicio para fortalecer sus músculos?" (888 Nunca), que no cuenta lo aeróbico. Al calcular los minutos aeróbicos,
  el CDC convierte las veces por mes a veces por semana (÷ 30/7), **cuenta como 0 las sesiones de menos de 10 minutos y
  también las pesas y el yoga**.
- **Fact (NHANES: precedente de N actividades):** NHANES 2005-2006 (`PAQIAF_D`) guarda **un registro por actividad de
  tiempo libre, sin límite de actividades**: cada una con veces en los últimos 30 días (`PADTIMES`, 1–300; se reporta por
  día, semana o mes y se convierte) y duración promedio por vez (`PADDURAT`, 10–600 min). Edición de datos: se excluyeron
  las actividades de menos de 10 minutos, y veces y duración se dejaron vacías si el total del día era de 12 horas o más.
- **Fact (GPAQ en español, OPS/OMS):** versión panamericana del instrumento STEPS 3.2 (Ecuador 2018, "corregida por
  OPS/OMS", publicada en el catálogo de la OMS). Desplazamientos: P7 "¿Camina o utiliza bicicleta durante al menos 10
  minutos seguidos en sus desplazamientos?" (Sí/No), P8 "En una semana normal, ¿cuántos días camina o utiliza bicicleta
  durante al menos 10 minutos seguidos en sus desplazamientos?" (número de días), P9 "En un día normal, ¿cuánto tiempo
  camina o usa la bicicleta para desplazarse?" (horas:minutos). Antes va una introducción ("al trabajo, de compras, al
  mercado, al templo…") que la guía de análisis pide no omitir. Sedentarismo: P16 "En un día normal, ¿cuánto tiempo suele
  pasar sentado o reclinado?" (horas:minutos), que incluye trabajo, casa, transporte, lectura y televisión y "No se
  incluye el tiempo que pasa durmiendo". En esta versión P16 está en el cuestionario **ampliado**. Con la OMS, la
  redacción es "sentado o reclinado", no "recostado". ENSANUT 2022 usa otra forma, de tipo IPAQ: "Durante los últimos 7
  días, ¿Cuánto TIEMPO en total estuvo sentado(a) en UNO de esos días de la semana?" (horas y minutos; 88 No responde ·
  99 No sabe).
- **Fact (limpieza GPAQ e IPAQ):** guía de análisis del GPAQ (OMS): días >7 → se excluye el caso; si una subárea
  (trabajo vigoroso o moderado, transporte, recreación vigorosa o moderada) suma **>16 h**, se excluye el caso; días = 0
  con tiempo >0 → se excluye por inconsistente; 15/30/45/60 en la columna de horas se pasan a minutos; P16 es válido de
  **0 a 1440 min**; repreguntar las respuestas de más de 4 h. IPAQ (guías de noviembre de 2005): días de 0 a 7; total de
  caminata + moderada + vigorosa **>960 min/día** → se excluye (supone 8 h de sueño); menos de 10 min → 0; para puntuar,
  cada categoría se trunca a 180 min/día. El IPAQ largo pregunta el tiempo sentado **por separado entre semana y en fin
  de semana**.
- **Fact (bouts de 10 minutos):** la OMS (26-11-2020): "La actividad física de cualquier tipo y de cualquier duración
  puede mejorar la salud". El GPAQ, el IPAQ, el BRFSS y NHANES 2005-2006 son anteriores a esa recomendación y conservan el
  umbral de 10 minutos.
- **Fact (actividad en el trabajo o del día, ítem único):** no se encontró un ítem validado de **3** opciones. Los
  precedentes tienen **4 niveles**. Copenhagen City Heart Study (atribuido a Saltin y Grimby 1968): "Which description
  most precisely covers your pattern of physical activity at work?" → 1 mainly sedentary, desk work · 2 walk around quite
  a bit but do not carry heavy items · 3 walk, often up stairs and lift various items · 4 heavy physical work, carry heavy
  burdens. NHANES 2005-2006 `PAQ180` (≥16 años): "which of these four sentences best describes your usual daily
  activities?", que **incluye** el hogar para quien se dedica a él, las clases para quien estudia y el día típico de
  jubilados y desempleados → 1 se sienta y no camina mucho · 2 está de pie o camina mucho, pero no carga ni levanta cosas
  seguido · 3 levanta cargas ligeras o sube escaleras o cuestas seguido · 4 hace trabajo pesado o carga cosas pesadas
  (en 2005-06: 1 399 / 3 120 / 1 150 / 464; DK 4). El Saltin-Grimby "clásico" (Grimby 2015) es de **tiempo libre**, no
  de trabajo. Existe una asociación opuesta: la actividad física laboral alta se asoció a **más** ausencias largas por
  enfermedad y la del tiempo libre a menos (Holtermann 2012, n = 7 144).
- **Source:** NHIS 2024 adult codebook (pp. 517–520), https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHIS/2024/adult-codebook.pdf
  · NHIS 2024 cuestionario en español (pp. 493–496), https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Survey_Questionnaires/NHIS/2024/SpanishQuest.pdf
  · BRFSS 2022 (sueño), https://www.cdc.gov/brfss/questionnaires/pdf-ques/2022-BRFSS-Questionnaire-508.pdf · BRFSS 2020
  en español, https://www.cdc.gov/brfss/questionnaires/pdf-ques/2020-BRFSS-Questionnaire-Spanish-Verison-508.pdf · BRFSS
  2023 (ejercicio, pp. 22–24 y apéndice 1), https://www.cdc.gov/brfss/questionnaires/pdf-ques/2023-BRFSS-Questionnaire-508.pdf
  · BRFSS 2019 en español (C11.01–C11.08), https://www.cdc.gov/brfss/questionnaires/pdf-ques/2019-BRFSS-Questionnaire-Spanish-Verison-508.pdf
  · BRFSS 2023 variables calculadas, https://www.cdc.gov/brfss/annual_data/2023/pdf/2023-calculated-variables-version4-508.pdf
  · BRFSS 2023 codebook, https://www.cdc.gov/brfss/annual_data/2023/zip/codebook23_llcp-v2-508.zip · PSQI y su
  puntuación, https://www.sleep.pitt.edu/psqi (instrumento: https://www.sleep.pitt.edu/sites/default/files/assets/Instrument%20Materials/PSQI-Instrument.pdf)
  · ENSANUT Continua 2022, cuestionario de actividad física en adultos (`ensafisica2022_adultos_entrega_w.Cuestionarios.pdf`),
  https://ensanut.insp.mx/encuestas/ensanutcontinua2022/descargas.php · NHANES 2017-18 SLQ_J,
  https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/SLQ_J.htm · Roenneberg 2003, J Biol Rhythms 18:80-90, PMID
  12568247 · Lauderdale 2008, Epidemiology 19:838-845, PMC2785092 · Fernandez-Mendoza 2012, Sleep Med 13:207-210, PMID
  22172961 · Escala Atenas (México), https://www.medigraphic.com/pdfs/salmen/sam-2005/sam055e.pdf · PROMIS, Yu 2011,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3261577 · Coleman 2012 (EVS), https://meps.ipums.org/meps/resources/Coleman_et_al_2012.pdf
  · NHANES 2005-06 PAQ_D y PAQIAF_D, https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/PAQ_D.htm y
  https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/PAQIAF_D.htm · STEPS Ecuador 2018 en español,
  https://extranet.who.int/ncdsmicrodata/index.php/catalog/774/download/5404 · GPAQ Analysis Guide (OMS),
  https://www.who.int/docs/default-source/ncds/ncd-surveillance/gpaq-analysis-guide.pdf · IPAQ, guías de noviembre de
  2005 (copia de UK Biobank), https://biobank.ctsu.ox.ac.uk/ukb/ukb/docs/ipaq_analysis.pdf · OPS/OMS 2020-11-26,
  https://www.paho.org/es/noticias/26-11-2020-cada-movimiento-cuenta-para-mejorar-salud-dice-oms · Holtermann 2012 CCHS,
  BMJ Open 2:e000556, https://pmc.ncbi.nlm.nih.gov/articles/PMC3282285 · Holtermann 2012, Br J Sports Med 46:291-295, PMID
  21459873 · Grimby 2015, Scand J Med Sci Sports 25 Suppl 4:119-125, PMID 26589125 · consulted 2026-10-26
- **Confidence:** [VERIFIED] en la fuente primaria: las preguntas, escalas, rangos, códigos y reglas de limpieza de
  NHIS, BRFSS, NHANES, PSQI, ENSANUT 2022, EVS (Coleman), GPAQ/STEPS en español y la guía GPAQ, la Escala Atenas en
  México y el aviso de la OPS. Leído solo el resumen (Europe PMC): Roenneberg, Lauderdale, Fernandez-Mendoza, Grimby,
  Holtermann (BJSM). PROMIS y el ítem del CCHS se leyeron mediante un extractor web de la página de PMC, no el PDF
  completo. El IPAQ se leyó en una copia de UK Biobank, no en el sitio del IPAQ. **[NOT VERIFIED]**: el formato de
  respuesta del ítem de sueño de ENSANUT 2022 (el texto del PDF no lo muestra); la redacción del sueño en ENSANUT MC 2016
  (solo el resumen de Guerrero-Zúñiga 2018, Salud Publica Mex 60:347-355, doi 10.21149/9280, que reporta 7.6 ± 3 h,
  28.4 % <7 h e insomnio 18.8 %; el texto completo estaba bloqueado); la disponibilidad de PROMIS Sleep en español; el
  ítem 3 del PHQ-9 ("dificultad para dormir o permanecer dormido, o dormir demasiado", 4 puntos, 2 semanas), que es el
  único precedente de ítem **combinado** y solo se vio en resultados del buscador; y si existe un GPAQ genérico de la OMS
  en español distinto de la versión panamericana.
- **Consecuencias para el diseño (perfil-habitos-actividad-sueno) [OPINION]:**
  1. **Sueño, horas.** Una sola cifra promedio es el estándar (NHIS, BRFSS, ENSANUT, PSQI): sirve. Hay que elegir el
     marco y decirlo: "por noche" (PSQI) excluye las siestas y "en 24 horas" (NHIS/BRFSS) las incluye. Para el turno
     nocturno "por noche" no aplica; ENSANUT dice "en un día". Pasos de 0.5 h (como NHANES) o horas enteras con la regla
     de redondeo de NHIS. Límite duro 1–24; confirmación suave (no bloqueo) en ≤5 h (NHIS) y en ≥14 h (código de tope de
     NHANES). Separar días laborales y libres solo si se quiere el desfase; no es necesario para registrar.
  2. **Insomnio.** La "a veces" de 3 puntos no tiene precedente en ningún instrumento revisado. Además: (a) junta dos
     síntomas que NHIS, PROMIS y Atenas miden por separado; (b) "casi siempre" absorbe "casi todos los días" y "todos
     los días", así que no se puede convertir a NHIS (al revés sí: 4 → 3 en cualquier momento); (c) "a veces" es un
     cuantificador vago, mientras que NHIS ancla en días. Alternativa defendible y con español oficial: los dos ítems de
     NHIS, recuerdo de 30 días, "nunca · algunos días · casi todos los días · todos los días". Si se quiere un solo
     ítem, al menos usar esas 4 opciones y aceptar que el ítem no es estándar. ISI, Atenas, PROMIS y PSQI dan una
     **puntuación** que la app no debe calcular, y el PSQI además no se puede modificar.
  3. **Ejercicio por actividad.** Capturar varias actividades, cada una con su frecuencia y duración, tiene precedente
     directo: BRFSS con 2 y NHANES 2005-06 sin límite. El EVS fija días 0–7 y minutos con tope de "150 o más". Días por
     semana (EVS) es más simple que veces por semana o por mes (BRFSS); quien hace la actividad dos veces al día queda
     subcontado, y se acepta. La fuerza (pesas, yoga) es otra dimensión: el CDC no la suma a los minutos aeróbicos. Si
     el total semanal suma todo, rotularlo como "tiempo total de lo que registraste", no como "actividad aeróbica", ni
     compararlo con los 150 min.
  4. **Movimiento del día.** El ítem de 3 opciones no está validado. NHANES `PAQ180` tiene 4 niveles, cubre a quien no
     tiene empleo (hogar, estudio, jubilación) y encaja con "actividad principal del día"; adoptarlo o justificar haber
     juntado sus niveles 2 y 3. Desplazamiento activo: GPAQ P7–P8 (sí/no + días 0–7); omitir P9 (tiempo) es un subconjunto
     legítimo, pero entonces no se puede sumar al total semanal. El "al menos 10 minutos seguidos" se puede quitar
     (OMS 2020, "cualquier duración") a costa de no ser comparable con GPAQ. Tiempo sentado: GPAQ P16 "en un día normal",
     "sentado o reclinado", **sin contar el sueño**; rango 0–24 h; confirmación suave si sentado + sueño > 24 h.
  5. **Rangos de captura.** Días por semana 0–7 (EVS, GPAQ, IPAQ). Minutos por sesión 1–600 como límite duro (NHANES
     acepta hasta 600; BRFSS hasta 9:59) y confirmación suave arriba de 240 (GPAQ repregunta lo que pasa de 4 h). Total
     de actividad por día <16 h (GPAQ por subárea, IPAQ 960 min) o <12 h (NHANES). Horas sentado 0–24. Sueño 1–24 (o
     0–24 con "menos de 1" = 1, como NHIS). Las reglas de truncar a 180 min o descartar lo de menos de 10 min son de
     **puntuación**, no de captura: no aplican a una app que no puntúa.
- **Re-check if:** se diseña un aviso FR-021 sobre sueño o actividad (ahí fijar fuentes y cortes); aparece el
  cuestionario de sueño de ENSANUT MC 2016/2018 o el formato del ítem de ENSANUT 2022; se decide exportar a LOINC/FHIR
  (buscar los códigos de NHIS/BRFSS); o el CDC cambia `SLPFLL_A`/`SLPSTY_A` en NHIS 2025+.
