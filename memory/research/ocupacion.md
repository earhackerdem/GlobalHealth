## Ocupación y actividad física por dominio (verificado 2026-10-19) <a id="ocupacion"></a>
- **Fact (dónde va la ocupación):** la NOM-004 6.1.1 exige ficha de identificación y antecedentes no patológicos,
  pero el texto consultado no enumera los campos; las plantillas mexicanas de historia clínica ponen la
  **ocupación en la ficha de identificación** (junto a estado civil). NIOSH (CDC) estandarizó el dato laboral para
  expedientes (*Occupational Data for Health*): situación laboral, trabajo actual (ocupación e industria) y
  trabajo habitual/de más años, con catálogos y traducción al español; no se encontró turno de trabajo en él.
- **Source:** AgendaPro (plantilla 2026) https://agendapro.com/blog/como-hacer-una-historia-clinica-en-mexico/ ·
  Rev. Médica Universidad Veracruzana 2024 https://www.medigraphic.com/pdfs/veracruzana/muv-2024/muv242f.pdf ·
  CDC/NIOSH ODH https://www.cdc.gov/niosh/ehr/odh/ · consulted 2026-10-19
- **Confidence:** [VERIFIED] NIOSH; plantillas = fuente secundaria convergente.

- **Fact (dominios de actividad física):** el GPAQ de la OMS mide la actividad en tres dominios (trabajo,
  desplazamiento, tiempo libre) más el tiempo sentado; todos los dominios deben preguntarse. Su validez contra
  acelerómetro fue "pobre" en un estudio colombiano de 76 personas.
- **Source:** copia en español del GPAQ https://studylib.es/doc/535955/cuestionario-mundial-sobre-actividad-f%C3%ADsica--
  (no es el sitio de la OMS) · Ghana, PMC9224181 https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9224181/ ·
  consulted 2026-10-19
- **Confidence:** [VERIFIED] los dominios; el texto exacto de las preguntas no se verificó en fuente OMS.

- **Fact (paradoja de la actividad física):** la actividad física del trabajo no da los beneficios de la del
  tiempo libre: en empleados daneses la de tiempo libre bajó el ausentismo largo y la del trabajo lo subió
  (dosis-respuesta); en 104,046 adultos de Copenhague la de tiempo libre se asoció a menos eventos
  cardiovasculares y menor mortalidad y la del trabajo a más riesgo. → En la app no se suman.
- **Source:** Holtermann et al., BJSM 2012 https://bjsm.bmj.com/content/46/4/291 · Holtermann et al., BJSM 2018
  https://bjsm.bmj.com/content/52/3/149 · editorial Eur Heart J 2021;42(15):1512
  https://dbpia.nl.go.kr/eurheartj/article/42/15/1512/6213773 · consulted 2026-10-19
- **Confidence:** [VERIFIED] la asociación en población danesa; generalización a México NO verificada.

- **Fact (turno nocturno):** la IARC clasificó el trabajo nocturno como «probablemente cancerígeno para los humanos»
  (Grupo 2A), con evidencia limitada en humanos para cáncer de mama, próstata y colon y recto. Lo define como trabajo
  durante las horas habituales de sueño de la población general. El grupo dice qué tan fuerte es la evidencia, no
  qué tan grande es el riesgo.
- **Source:** IARC Monographs vol. 124 https://www.iarc.who.int/news-events/iarc-monographs-volume-124-night-shift-work
  · consulted 2026-10-29
- **Confidence:** [VERIFIED]
- **Re-check if:** la app llegara a usar el turno para algo más que registrarlo (no debe: C-6).

- **Fact (situación laboral):** el value set de NIOSH ODH para situación laboral no se pudo leer (la página de HL7
  dio 404); un resumen de búsqueda dice que tiene solo tres conceptos (empleado, desempleado, fuera de la fuerza
  laboral). INEGI (ENOE), según otro resumen, divide a la población no económicamente activa en hogar, estudio,
  jubilados o pensionados e «impedimentos personales».
- **Source:** https://inegi.org.mx/contenidos/saladeprensa/boletines/2024/IOE/IOE2024_09.pdf (texto no extraíble) ·
  consulted 2026-10-29
- **Confidence:** NOT VERIFIED en las fuentes primarias.
- **Re-check if:** se codifica la situación laboral.
