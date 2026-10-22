## Humo de leña como factor de riesgo respiratorio en México (verificado 2026-10-19) <a id="humo-lena"></a>
- **Fact:** en México la exposición crónica al humo de leña es una causa reconocida de EPOC adicional al
  tabaquismo, sobre todo en hogares rurales que cocinan o calientan con leña (INER); tesis de la UNAM atribuyen
  25–35 % de los casos de EPOC a la exposición a biomasa (60–70 % al tabaco) y reportan RM 5 (IC95 % 2.4–10.3)
  para el uso doméstico de leña o carbón. La EPOC por biomasa tiene un fenotipo clínico propio.
- **Source:** Revista del INER (2002), https://www.medigraphic.com/pdfs/iner/in-2002/in024a.pdf · tesis UNAM
  https://ru.dgb.unam.mx/bitstream/20.500.14330/TES01000311003/3/0311003.pdf · consulted 2026-10-19
- **Confidence:** [VERIFIED] el riesgo (fuente institucional + tesis coincidentes). NO se encontró un formato
  estándar de historia clínica para registrar la exposición (años, horas/año): la forma de captura en
  product/dominio.md (nunca/antes/actual + años aprox.) es [ASSUMPTION]. *Superado el 2026-10-21: ver
  [cómo se mide la exposición](#humo-lena-horas-ano).*
- **Re-check if:** se diseña un aviso FR-021 que use la exposición (ahí fijar umbral con guía GOLD o la guía
  mexicana de EPOC).

<a id="humo-lena-horas-ano"></a>
- **Fact (cómo se mide la exposición, verificado 2026-10-21):** el estudio mexicano de referencia (casos y
  controles, mujeres mayores de 40 años, Ciudad de México) mide la exposición acumulada en **horas-año = años de
  exposición × horas promedio al día**. El riesgo creció linealmente con las horas-año; por encima de 200 horas-año
  frente a no expuestas: bronquitis crónica OR 15 (IC95 % 5.6–40) y bronquitis crónica con obstrucción OR 75 (18–306).
  Otro estudio mexicano usa >100 h/año (OR 9.65): el umbral varía entre fuentes.
- **Source:** Pérez-Padilla R, Regalado J, Vedal S, Paré P, Chapela R, Sansores R, Selman M, Am J Respir Crit Care
  Med 1996;154(3 Pt 1):701-6, PMID 8810608 (resumen vía Europe PMC,
  https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8810608%20AND%20SRC:MED&resultType=core&format=json)
  · Rev Med Hosp Gen Mex 2015, https://www.elsevier.es/en-revista-revista-medica-del-hospital-general-325-pdf-download-S0185106315000554
  (PDF no leído; datos del resultado del buscador) · consulted 2026-10-21
- **Confidence:** [VERIFIED] la medida y los OR de 1996 (resumen del artículo en Europe PMC); [NOT VERIFIED] el
  estudio de 2015 (solo el resultado del buscador, sin abrir la fuente). Sigue sin encontrarse un formato de historia clínica oficial (GPC IMSS de EPOC no leída).
- **Consecuencia para la captura:** edad de inicio, edad de fin (si es *Antes*) y **horas al día en promedio**; la
  app guarda los datos crudos y no calcula horas-año (C-6). Esto reemplaza la [ASSUMPTION] de "años aprox.".
- **Re-check if:** se diseña un aviso FR-021 con la exposición (fijar umbral con GOLD o la guía mexicana de EPOC).
