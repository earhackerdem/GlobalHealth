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
- **Fact (metodología):** ofrecer "no sé" atrae más a quien contesta por escrito o con poco esfuerzo y no mejora la
  calidad de los datos (Krosnick et al. 2002, POQ 66:371-403); lo que menos faltantes dejó en línea fue no ofrecerlo y
  repreguntar con amabilidad (de Leeuw, Hox y Boevé 2016, resumen).
- **Fact (México):** la NOM-004-SSA3-2012 (6.1.1) pide en el interrogatorio el uso de tabaco, alcohol y otras
  sustancias, pero no dice cómo registrar un dato desconocido.
- **Source:** NHIS 2024 adult codebook https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHIS/2024/adult-codebook.pdf
  · NSDUH 2023 codebook https://www.samhsa.gov/data/system/files/media-puf-file/nsduh-2023-ds0001-info-codebook_v2.pdf
  · BRFSS 2024 https://www.cdc.gov/brfss/questionnaires/pdf-ques/2024-BRFSS-Questionnaire-508.pdf · NCHS RSS-8
  https://www.cdc.gov/nchs/data/rss/round8/questionnaire.pdf · AUDIT (OMS 2001) https://www.paho.org/sites/default/files/Auditmanual_ENG.pdf
  · VA https://www.va.gov/vdl/documents/Clinical/CPRS-Clinical_Reminders/pxrm_1_5_21_setup.pdf · FHIR
  https://terminology.hl7.org/CodeSystem-data-absent-reason.html y https://hl7.org/fhir/R5/questionnaire-definitions.html
  · LOINC vía tx.fhir.org `$lookup` · Krosnick 2002 https://web.stanford.edu/dept/communication/faculty/krosnick/docs/2002/2002%20The%20impact%20of%20no%20opinion%20response%20options%20on%20data%20quality-%20N.pdf
  · de Leeuw 2016 https://research-portal.uu.nl/en/publications/handling-do-not-know-answers-exploring-new-approaches-in-online-a/
  · NOM-004 https://dof.gob.mx/nota_detalle_popup.php?codigo=5272787 · consulted 2026-10-22
- **Confidence:** [VERIFIED] todo lo anterior en la fuente primaria, salvo: de Leeuw 2016 (solo el resumen), Poe et al.
  1988 (citado por Krosnick, no leído), el AUDIT-C de Bush 1998 y el umbral VA ≥5 (fuentes secundarias, no se usan aquí).
- **Consecuencia para la captura (perfil-habitos-completitud):** "No recuerdo" solo en preguntas sobre el pasado
  (edades de inicio y fin; cantidades de "Antes"); nunca en las tres preguntas de frecuencia del alcohol ni en lo que
  describe el presente; guardado como un valor propio, no como un número especial, para que "no recuerda" no se
  confunda con "sin respuesta" ni contamine un promedio.
- **Re-check if:** se mide en producción que "No recuerdo" pasa claramente del ~1 % de NHIS en algún ítem (señal de
  que se usa como salida rápida), o se exporta a FHIR (mapear a `asked-unknown`).
