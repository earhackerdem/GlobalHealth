## Captura de diagnósticos y medicinas: texto libre, catálogo o híbrido (verificado 2026-10-20) <a id="captura-catalogos"></a>
Pedido por Saúl Pérez 2026-10-20 al validar perfil-cronicas (inbox: "Ronda 2 del dominio"). Contexto: ligar
medicina ↔ diagnóstico/crónica se hace por id y no necesita catálogo; esto es sobre consistencia, IA, análisis e
interoperabilidad.

- **Fact:** El catálogo de diagnósticos de la DGIS es la CIE-10 (actualización 16/04/2024): XLSX de 14,498 códigos
  (1,811 de 3 caracteres, 12,687 de 4) y 76 columnas, casi todas de vigilancia epidemiológica y mortalidad. Nombres
  oficiales en mayúsculas, sin sinónimos: "diabetes tipo 2", "presión alta", "colesterol alto" y "EPOC" dan 0
  coincidencias; "asma" da 38, casi todas falsas (dentro de "histoplasma", "micoplasma"). Las 13 condiciones de la
  lista de crónicas sí mapean a códigos limpios (E11, I10X, J45, E039, E780, J449, G40, F32/F33, F41, F31, F10/F19),
  salvo "Artritis", que es ambigua: artritis reumatoide (M069) o artrosis (M199).
- **Source:** archivo `DIAGNOSTICOS_20240416.xlsx` (descargado por Saúl Pérez; mismo que
  https://gobi.salud.gob.mx/gobi/catalogos/catalogosmaestros/DIAGNOSTICOS_20240416.zip), leído por el agente ·
  consulted 2026-10-20
- **Confidence:** [VERIFIED] (empírico sobre el archivo)
- **Re-check if:** la DGIS publica una actualización o cambia a CIE-11.

- **Fact:** El criterio de uso de la DGIS dice que la CIE-10 no sustituye el texto del médico: ambos se registran.
  La DGIS no publica licencia: remite a cada institución para conocer condiciones de uso. El sitio tenía el
  certificado TLS vencido el día de la consulta.
- **Source:** http://www.dgis.salud.gob.mx/contenidos/intercambio/diagnostico_gobmx.html ·
  http://www.dgis.salud.gob.mx/contenidos/intercambio/iis_catalogos_gobmx.html · consulted 2026-10-20
- **Confidence:** [VERIFIED] el criterio; licencia NOT VERIFIED (no publicada).
- **Re-check if:** se va a embarcar el catálogo en la app (pedir términos a DGIS/CEMECE).

- **Fact:** NOM-024-SSA3-2012 obliga a establecimientos del SNS que adopten un SIRES y a quienes lo distribuyan o
  comercialicen; exige usar los catálogos fundamentales (CIE vigente, medicamentos del CSG) y exportar la
  información del paciente. Vigente (ratificada 2018) y en modificación: inscrita en el PNIC 2025 y 2026, con plazo
  enero–diciembre 2026; no se encontró PROY-NOM publicado.
- **Source:** https://dof.gob.mx/nota_detalle.php?codigo=5280847&fecha=30/11/2012 ·
  https://platiica.economia.gob.mx/normalizacion/?p=35250 · https://sidof.segob.gob.mx/notas/docFuente/5780781 ·
  consulted 2026-10-20
- **Confidence:** [VERIFIED] el texto y la revisión en curso; que NO aplique a un expediente del paciente es
  [OPINION] (interpretación, no asesoría legal).
- **Re-check if:** se publica el PROY-NOM, o GlobalHealth se ofrece a clínicas o recibe expedientes de prestadores.

- **Fact:** Medicinas: el Compendio Nacional de Insumos (CNIS 2025, DOF 26/04/2025, actualizaciones en 2026) lista
  solo genéricos con clave de 12 dígitos y se publica en PDF (42 MB); no se encontró CSV/XLS. El visor de COFEPRIS
  (abril 2026) busca por marca y por genérico y ofrece exportar; formato y licencia no verificados.
- **Source:** https://sidof.segob.gob.mx/notas/docFuente/5799600 · https://www.csg.gob.mx/Comp26042025.pdf ·
  https://www.gob.mx/cofepris/es/articulos/cofepris-presenta-visor-de-registros-sanitarios-de-medicamentos ·
  consulted 2026-10-20
- **Confidence:** [VERIFIED] contenido y formato del CNIS; COFEPRIS exportación y licencia NOT VERIFIED.
- **Re-check if:** se quiere sugerir marcas → genérico.

- **Fact:** CIE-11 en México: transición en curso solo para mortalidad (curso OPS/DGIS/CEMECE abril–julio 2026), sin
  fecha de reemplazo de la CIE-10. Licencia CIE-11 CC BY-ND 3.0 IGO; traducciones y crosswalks requieren acuerdo con
  la OMS.
- **Source:** https://www.paho.org/es/noticias/21-4-2026-secretaria-salud-ops-inauguran-curso-regional-sobre-cie-11-para-fortalecer
  · https://icd.who.int/en/docs/icd11-license.pdf · consulted 2026-10-20
- **Confidence:** [VERIFIED]
- **Re-check if:** la DGIS publica catálogo CIE-11.

- **Fact:** FHIR modela el concepto como `text` + `coding[]` opcional (`userSelected` marca el código elegido por el
  usuario). `Condition.asserter` y `MedicationStatement.informationSource` aceptan al paciente;
  `MedicationStatement.reasonReference` liga la medicina a una Condition; `Dosage.text` es libre. IPS: si la fuente
  solo tiene texto, se usa solo el texto, y la ausencia se dice con códigos explícitos (no-known-problems). No se
  encontró guía FHIR mexicana oficial.
- **Source:** https://hl7.org/fhir/R4/datatypes-definitions.html · https://hl7.org/fhir/R4/condition.html ·
  https://hl7.org/fhir/R4/medicationstatement.html · https://hl7.org/fhir/uv/ips/design.html · consulted 2026-10-20
- **Confidence:** [VERIFIED]
- **Re-check if:** se diseña exportación o intercambio.

- **Fact:** IA codificando sola: GPT-4 reprodujo el código ICD-10-CM exacto en 33.9 % de los casos y generó códigos
  inexistentes (NEJM AI, abril 2024).
- **Source:** https://www.mountsinai.org/about/newsroom/2024/despite-ai-advancements-human-oversight-remains-essential
  · consulted 2026-10-20
- **Confidence:** [VERIFIED] vía comunicado institucional; el artículo dio 403.
- **Re-check if:** se planea codificar con IA; buscar estudios con modelos actuales.

- **Fact:** Apps: ninguna app mexicana revisada (IMSS Digital, Benavides, Del Ahorro, Guadalajara, San Pablo,
  Similares, Doctoralia) deja al paciente capturar medicinas o padecimientos; el IMSS solo muestra lo que recetó y
  las farmacias usan el catálogo para vender. Internacionales (Apple Salud, Medisafe, MyTherapy): búsqueda en
  catálogo con salida a texto libre; dosis y frecuencia en campos separados. Apple Salud no usa su catálogo fuera de
  EE. UU. (captura manual) y lo capturado a mano no entra a la revisión de interacciones. Medisafe usa lista cerrada
  de padecimientos; CareClinic pasó a texto libre.
- **Source:** https://www.imss.gob.mx/node/110116 · https://apps.apple.com/mx/app/id6469937996 ·
  https://support.apple.com/en-us/105064 · https://help-center.medisafe.com/en/articles/8102973 ·
  https://apps.apple.com/us/app/id1455648231 · consulted 2026-10-20
- **Confidence:** [VERIFIED] en fichas y ayuda públicas; lo que está detrás de inicio de sesión NOT VERIFIED.
- **Re-check if:** se diseña la pantalla de captura (ver las apps de verdad, no solo sus fichas).

- **Fact:** Exactitud al capturar medicinas (85 pacientes, 14 días): lista de catálogo 97 %, texto libre 84 %,
  código NDC 87 %; los autores dicen que el texto libre ayuda a que la lista quede completa. Con pacientes que
  escriben de memoria, dosis y frecuencia son lo que más falla (16.7 % y 25 % correctas, n=11, 2004).
- **Source:** https://academic.oup.com/jamiaopen/article/8/5/ooaf118/8287826 ·
  https://pmc.ncbi.nlm.nih.gov/articles/PMC1550597/ · consulted 2026-10-20
- **Confidence:** [VERIFIED]; muestras chicas.
- **Re-check if:** se decide la UX de captura de medicinas.
