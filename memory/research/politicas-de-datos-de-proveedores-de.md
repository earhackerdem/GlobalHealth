## Políticas de datos de proveedores de IA (verificado 2026-10-18)

- **Fact:** Términos de la **Gemini API** (effective 2026-03-23, updated 2026-04-28): en los **servicios NO
  pagados** (cuota gratuita de Google AI Studio) Google **usa los prompts y respuestas para proveer, mejorar y
  desarrollar productos y tecnologías de ML**, con **revisores humanos** que pueden leer/anotar la entrada y
  salida (desvinculada de la cuenta), y los términos piden literalmente "Do not submit sensitive, confidential,
  or personal information to the Unpaid Services". En los **servicios pagados** (proyecto Cloud con billing)
  Google NO usa los datos para mejorar productos, pero **loguea prompts/respuestas por un periodo limitado** para
  detección de abuso (sin plazo publicado, almacenamiento posible en cualquier país). La excepción EEA/UK/Suiza
  (términos de pago aun en el gratis) NO cubre a México.
- **Source:** https://ai.google.dev/gemini-api/terms · consulted 2026-10-18
- **Confidence:** [VERIFIED]
- **Implicación:** la cuota gratuita de AI Studio es **incompatible con NFR-005 y con recetas (dato sensible,
  LFPDPPP art. 3-VI)** — descartada para producción; a lo sumo para pruebas con datos sintéticos. El tier de pago
  tampoco es "cero retención" estricta (log de abuso): evaluar contra NFR-005 tal como está redactado.
- **Re-check if:** Google cambie términos; al redactar el tech-brief del proveedor.

- **Fact:** La **API de Anthropic** NO usa entradas/salidas de productos comerciales para entrenar por default
  (solo con opt-in/feedback; el feedback se conserva hasta 5 años desvinculado de IDs). El plazo general de
  retención de la API y la opción de zero data retention viven en los Commercial Terms / Trust Center (no
  verificados en esta pasada).
- **Source:** https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training · consulted
  2026-10-18
- **Confidence:** [VERIFIED] lo del no-entrenamiento por default; retención exacta y ZDR: NOT VERIFIED aún.
- **Re-check if:** al evaluar Anthropic como proveedor en el tech-brief (leer Commercial Terms y Trust Center).

- **Fact:** Los planes Max incluyen crédito API mensual: **Max 5x = 100 USD, Max 20x = 200 USD** (Team: 20/100
  USD por asiento, tope 500). Sirve para Messages API, Batches, Console Playground, Managed Agents y Agent SDK;
  NO para Claude Code interactivo ni Bedrock/Vertex/Foundry. **No acumulable: expira cada ciclo**; se reclama en
  UNA organización de Console vinculada, con plan activo 7 días antes.
- **Source:** https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans ·
  consulted 2026-10-18 (enlace aportado por Saúl Pérez)
- **Confidence:** [VERIFIED]. BYOK (el usuario selecciona su propio proveedor/API key) sigue siendo idea de
  producto pendiente de diseño.
- **Re-check if:** al armar el tech-brief — verificar el crédito en la cuenta real; BYOK implica además análisis
  LFPDPPP (el responsable sigue siendo GlobalHealth aunque la key sea del usuario) y UX para no-técnicos.

- **Fact (panorama de capas gratuitas que "no entrenan", solo fuentes secundarias):** un análisis de oct-2026
  contra los términos de 18 proveedores concluye que **los tiers gratuitos son donde más se entrena con los
  datos** y que "no entrenar" no responde la pregunta aparte de la retención. Por proveedor: **Groq** no
  entrenaría con entradas/salidas (services agreement) pero con logs de hasta 30 días por abuso; **Mistral** en
  su tier gratuito usa los datos para entrenar salvo opt-out (toggle), su API de pago no entrena y el tier
  gratuito retiene 30 días; **Cerebras** habría eliminado su tier gratuito permanente en jul-2026. Fuentes entre
  sí contradictorias.
- **Source:** https://www.developersdigest.tech/blog/which-ai-apis-train-on-your-data (oct-2026),
  https://openrouter.ai/blog/tutorials/free-llm-apis-compared/ , https://merginit.com/blog/16062026-free-ai-api-inference-comparison
  · consulted 2026-10-18
- **Confidence:** NOT VERIFIED por proveedor (secundarias en conflicto). Conclusión operativa [OPINION]: **no
  existe hoy una capa gratuita cloud que garantice no-entrenamiento + cero retención** al nivel que exige una
  receta (dato sensible); para datos reales el camino gratuito es **on-device** (Gemini Nano, spike D17), y los
  créditos Max (200 USD/mes) cubren el desarrollo con la API de Anthropic. El tech-brief verifica términos
  primarios solo de quien llegue a la short-list.
- **Re-check if:** tech-brief del proveedor; cualquier proveedor que entre a la lista blanca BYOK.

- **Fact:** NOM-004-SSA3-2012, numeral **6.1.1** (historia clínica → interrogatorio, contenido mínimo): "ficha
  de identificación, en su caso, grupo étnico, antecedentes heredo-familiares, antecedentes personales
  patológicos (incluido uso y dependencia del tabaco, del alcohol y de otras sustancias psicoactivas…) y no
  patológicos, padecimiento actual… e interrogatorio por aparatos y sistemas". Numeral **6.1.2** (exploración
  física, mínimo): "habitus exterior, signos vitales (temperatura, tensión arterial, frecuencia cardiaca y
  respiratoria), peso y talla".
- **Source:** texto oficial DOF 2012-10-15, https://www.gob.mx/cms/uploads/attachment/file/512094/NOM-004-SSA3-2012.pdf
  · consulted 2026-10-19 (extraído del PDF oficial)
- **Confidence:** [VERIFIED]
- **Re-check if:** —. Uso: ancla del catálogo perfil/antecedentes (product/dominio.md, rebanada onboarding):
  los campos que pidió Saúl Pérez (nacimiento, peso, estatura, AHF) son exactamente el mínimo que la norma exige
  al médico preguntar/medir; sexo (ficha de identificación) y alergias (APP) son las propuestas del harness.

- **Fact (anamnesis — estructura estándar de los antecedentes que piden los médicos):** las guías docentes de
  historia clínica coinciden en subdividir los **APP** en: enfermedades crónico-degenerativas, infecciosas
  (hepatitis…), **quirúrgicos** (tipo de operación, fecha, complicaciones), **traumáticos** (fracturas, esguinces,
  luxaciones), **transfusionales** (fecha, componente, reacción; a veces grupo sanguíneo) y **alérgicos**
  (medicamentos, alimentos, otras sustancias), cada uno con momento de aparición/tratamiento/secuelas; los **APNP**
  cubren hábitos (alimentación, sueño, ejercicio, higiene) e inmunizaciones (tabaco/alcohol/sustancias quedan
  dentro de APP por la propia NOM-004 6.1.1). Para **AHF**, la práctica recomendada es registrar **3 generaciones
  separando línea materna y paterna**, con parentesco y **edad al diagnóstico** (los cuestionarios oncológicos lo
  piden explícitamente); un formato mexicano (IPN) lo captura como tabla padecimiento × familiar.
- **Source:** lista de cotejo Historia Clínica, Fac. Medicina Universidad Veracruzana (uv.mx, 2020)
  https://www.uv.mx/medicina/files/2020/01/Concentrado-Lista-de-Cotejo-Historia-Clinica_ENE20.docx · guía de
  Historia Clínica Semiológica (UTP) https://academia.utp.edu.co/basicoclinica/files/2018/08/Historia-Cl%C3%ADnica-Semiol%C3%B3gica-GU%C3%8DA.pdf
  · WA DOH "Historial de salud familiar" (3 generaciones, ambos lados) https://doh.wa.gov/sites/default/files/2025-11/141-197-FamilyHealthHistory-Spanish.pdf
  · cuestionario AHF oncológico con familia materna/paterna y edad al diagnóstico (Texas Oncology)
  https://www.texasoncology.com/getmedia/36d92ae2-8461-4031-9f5f-95b338f2c4d9/texas-oncology-great-family-history-questionnaire-spanish.pdf
  · formato historia clínica IPN https://www.ipn.mx/assets/files/cecyt10/docs/estudiantes/servicios/2024/historia-clinica.pdf
  · consulted 2026-10-19
- **Confidence:** [VERIFIED] como práctica docente/clínica convergente (fuentes secundarias múltiples y
  coincidentes); el esqueleto normativo (AHF/APP/APNP + interrogatorio por aparatos y sistemas) es primario:
  NOM-004 6.1.1 (entrada anterior). Lo de cuestionarios POR especialidad (urología, proctología, ORL) NO se
  investigó a fondo: se difirió como capa futura (E4/FR-022).
- **Re-check if:** al diseñar la story de llenado de secciones APP/APNP (ahí se decide el detalle por sección) y
  al abordar cuestionarios por especialidad.
