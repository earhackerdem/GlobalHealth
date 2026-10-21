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
