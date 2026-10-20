# Verified research

Facts with source, verification date and confidence level. A fact here is cited with **the authority its record
gives it**, never more. If two records of the same fact disagree, the more conservative one rules until you go back
to the source. Market-sensitive records expire after ~3 months.

## <topic> <a id="topic"></a>
- **Fact:** …
- **Source:** <URL or file:line> · consulted YYYY-MM-DD
- **Confidence:** [VERIFIED] / [OPINION/HYPE] / NOT VERIFIED
- **Re-check if:** <what would make it expire>

## Comorbilidades crónicas con evidencia (para la IA proactiva) <a id="comorbilidades"></a>
Pedido por Saúl Pérez 2026-10-11 ("investigar si hay evidencia de enfermedades crónicas que impliquen otras").
Nota de alcance: esto es evidencia de ASOCIACIÓN para priorizar qué huecos señalar; el software nunca la presenta
como causalidad ni como diagnóstico.

- **Fact:** SII (colitis/intestino irritable) y ansiedad/depresión co-ocurren en ambas direcciones: cohorte
  nacional taiwanesa 2026 — SII → mayor riesgo de ansiedad (aHR 1.68) y depresión (aHR 1.55), y a la inversa;
  meta-análisis 2017: más ansiedad y depresión en todos los subtipos de SII vs controles. El mecanismo
  (eje intestino-cerebro) sigue siendo hipótesis, no está confirmado en humanos para SII.
- **Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC5503284 (meta-análisis 2017) · cohorte 2026 vía
  https://www.cambridge.org/core/services/aop-cambridge-core/content/view/S0033291726103328 · consulted 2026-10-11
- **Confidence:** [VERIFIED] la asociación bidireccional; NOT VERIFIED el mecanismo.
- **Re-check if:** se redacta contenido clínico para usuarios; revisar los papers originales, no los resúmenes.

- **Fact:** Trastornos de ansiedad y consumo problemático de alcohol: ~2x odds de trastorno por sustancias con
  ansiedad; la ansiedad suele PRECEDER al problema de alcohol (consistente con automedicación, no prueba). NESARC
  longitudinal (n=34,653): quienes bebían para calmar la ansiedad tuvieron ~2.6x odds de desarrollar trastorno por
  alcohol en 3 años (12.6% vs 4.7%). Solo ~20% de personas con ansiedad se automedican con alcohol.
- **Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC2763929 y https://apt.rcpsych.org/content/8/2/107.full ·
  consulted 2026-10-11 (resúmenes secundarios; cifras exactas → Robinson et al. 2011, J Anxiety Disorders)
- **Confidence:** [VERIFIED] la asociación y el orden temporal típico; cifras puntuales pendientes de fuente primaria.
- **Re-check if:** la IA vaya a citar números concretos al usuario.

- **Fact:** Historial familiar como disparador de tamizaje: un familiar de primer grado con diabetes ≈ duplica el
  riesgo (ADA: tamizaje más temprano/frecuente que el corte general de 45 años). Cáncer colorrectal: ACS/USMSTF
  recomiendan iniciar a los 40 o 10 años antes del caso familiar más joven. Mama: mayor beneficio de mamografía
  regular con madre/hermana afectada. OJO: fuentes de 2004–2019; las guías vigentes (USPSTF actual, ADA Standards
  of Care del año) deben verificarse antes de codificar reglas.
- **Source:** https://www.aafp.org/afp/2019/1215/p771.pdf · https://pmc.ncbi.nlm.nih.gov/articles/PMC2726801/ ·
  https://stacks.cdc.gov/view/cdc/119217/cdc_119217_DS1.pdf · consulted 2026-10-11
- **Confidence:** [VERIFIED] el principio (historial familiar adelanta el tamizaje); NOT VERIFIED los umbrales vigentes 2026.
- **Re-check if:** SIEMPRE antes de implementar cada regla de sugerencia — ir a la guía vigente con fecha.

- **Fact:** La multimorbilidad se agrupa en clústers reproducibles (p.ej. artritis+depresión+ansiedad en España;
  dolor crónico+respiratorio en hombres, ánimo irritable+cefalea en mujeres en Brasil), pero los clústers dependen
  de la muestra y del método: sirven como heurística de "qué preguntar", no como regla clínica.
- **Source:** https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6382818/ (São Paulo) ·
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3896355 (COURAGE España) · consulted 2026-10-11
- **Confidence:** [VERIFIED] que existen patrones; [OPINION/HYPE] cualquier uso predictivo individual.
- **Re-check if:** se diseñe el motor de sugerencias; buscar guías clínicas, no estudios transversales.

## Stack y proveedores (technical brief) <a id="stack"></a>
- **Fact:** Anthropic no entrena modelos con contenido de clientes de la API por defecto (Commercial Terms);
  retención por defecto reportada en conflicto entre fuentes (7 días desde sept 2025 vs 30 días); ZDR existe pero
  se solicita, no es automático.
- **Source:** https://aibusiness.com/nlp/anthropic-will-not-train-its-ai-on-clients-data ·
  https://char.com/blog/anthropic-data-retention-policy (secundarias) · consulted 2026-10-11
- **Confidence:** [VERIFIED] el no-training por defecto (múltiples fuentes coincidentes); NOT VERIFIED la ventana
  de retención exacta → ir a Commercial Terms/DPA oficiales antes del primer dato real (NFR-005).
- **Re-check if:** SIEMPRE antes de mandar el primer dato de salud real; política puede cambiar.

- **Fact:** El template full-stack de tiangolo vive hoy en la org fastapi (github.com/fastapi/full-stack-fastapi-template):
  FastAPI + SQLModel + Postgres + Alembic, React/TS + Vite + Tailwind + shadcn, Docker Compose + Traefik, GH Actions,
  pytest + Playwright. MIT. Snapshot feb 2026.
- **Source:** https://github.com/fastapi/full-stack-fastapi-template y https://fastapi.tiangolo.com/project-generation ·
  consulted 2026-10-11
- **Confidence:** [VERIFIED]
- **Re-check if:** se reconsidera el stack (ADR D6 lo descartó para v1).

- **Fact:** El template migró de Poetry a uv (#1356) y adoptó `docker compose watch` para desarrollo local (#1354),
  ambos en septiembre 2024; los archivos compose fueron renombrados a compose.yml (#2106). Entorno local documentado:
  Docker Compose para los servicios + uv para el venv/deps del backend.
- **Source:** https://code.morphllm.com/fastapi/full-stack-fastapi-template/commits/0.8.0/master/backend/README.md
  (mirror del commit log) · consulted 2026-10-11
- **Confidence:** [VERIFIED] la migración a uv y compose watch (commit log); los comandos exactos del development.md
  vigente NOT VERIFIED → T1 los confirma contra el repo oficial.
- **Re-check if:** T1 de cuenta-consentimiento (instalación real).

- **Fact (T1, empírico):** el método oficial de instalación HOY es el botón "Use this template" de GitHub (ya no
  copier; hooks/post_gen_project.py es residuo del generador). Clonado el repo oficial (commit 7257e60,
  2026-10-08): el frontend usa **bun** (workspaces: frontend + packages/react-email) y biome, el backend sirve el
  frontend construido desde backend/app/frontend (los tests lo exigen), tests del backend en `backend/tests/`,
  flujo dev: `docker compose up -d db mailpit` + `uv sync` + `uv run bash scripts/prestart.sh` + `uv run fastapi dev`
  + `bun install` + `bun run dev`. Playwright levanta Vite solo (webServer) y lee credenciales del .env raíz.
  OJO: la suite de pytest limpia datos de la BD local compartida (re-correr prestart tras pytest para re-sembrar).
- **Source:** clon local del template (scratchpad), README.md y development.md del commit 7257e60 · verified 2026-10-11
- **Confidence:** [VERIFIED] (ejecutado: pytest 58 passed, Playwright chromium 62 passed)
- **Re-check if:** make harness-update del template / upgrade del template.

- **Fact:** LFPDPPP: datos de salud = sensibles; art. 9 exige consentimiento expreso y por escrito (o equivalente)
  para tratarlos, con carga de la prueba en el responsable; existe excepción de transferencia para
  prevención/diagnóstico médico (citada como art. 36 o 37 según la fuente — numeración por confirmar en DOF).
  La reforma 2025 habría cambiado la autoridad (ya no INAI) — NOT VERIFIED.
- **Source:** https://sdv.com.mx/compendio/ley-proteccion-datos-personales/articulo-9/ ·
  https://sdv.com.mx/compendio/ley-proteccion-datos-personales/articulo-37/ ·
  https://iapp.org/news/a/la-proteccion-de-datos-personales-en-los-expedientes-clinicos · consulted 2026-10-11
- **Confidence:** [VERIFIED] el principio (consentimiento expreso para sensibles); NOT VERIFIED numeración vigente,
  reforma 2025 y autoridad competente → texto en DOF + abogado antes de abrir a usuarios distintos de Saúl (NFR-004).
- **Re-check if:** antes del primer cambio de cumplimiento; antes de cualquier usuario externo.

## Nombre del producto (decisión pendiente de Saúl Pérez) <a id="naming"></a>
- **Fact:** "GlobalHealth" colisiona: GlobalHealth, Inc. (aseguradora de Oklahoma) tiene app homónima en tiendas
  (apps.appfollow.io/ios/globalhealth/1109445182) y Global Health Limited (Luxemburgo) tiene marca viva
  "GLOBAL HEALTH CONNECTING CLINICIANS AND CONSUMERS" para seguros de salud (la frase "GLOBAL HEALTH" está
  disclaimed en esa marca). Hay además filings EGLOBALHEALTH y un GLOBALHEALTH de software de 1999 abandonado.
- **Source:** https://trademarks.justia.com/791/84/global-health-connecting-clinicians-and-79184762.html ·
  https://trademark.justia.com/758/22/globalhealth-75822561.html · consulted 2026-10-11
- **Confidence:** [VERIFIED] las colisiones citadas; NO es un clearance legal completo (USPTO/EUIPO/IMPI + abogado
  antes de marca pública).
- **Re-check if:** se decida el nombre definitivo.

- **Fact:** "Vitacora" (vita+bitácora): búsqueda sin producto existente con ese nombre. "Anamnesis": usado por un
  proyecto estudiantil (Drexel), papers y una patente 2012; existe "AnamnIA" (transcriptor de historias clínicas).
  Competidores de la categoría con nombre: Apple Health Records, MyChart, Fasten Health (PHR open-source self-hosted,
  FHIR), CommonHealth, MyLinks, One Record, TidyHealth, VertexMD, HealthMemo.
- **Source:** https://cci.drexel.edu/SeniorDesign/2021_2022/ANAMNESIS/index.html · https://anamnia1.odoo.com ·
  https://selfhostyourself.com/alternative-to/apple-health-records · consulted 2026-10-11
- **Confidence:** [VERIFIED] lo encontrado; la ausencia de colisiones de "Vitacora" es evidencia débil (una búsqueda).
- **Re-check if:** antes de registrar marca o publicar en tiendas: IMPI/USPTO + App Store/Play Store del finalista.

## Wearables con API accesible (fuera de v1; camino futuro) <a id="wearables"></a>
- **Fact:** En Android, los datos de un Galaxy Watch llegan a terceros vía Health Connect: watch → app Samsung
  Health (sincroniza con Health Connect desde la v6.22.5, oct 2022) → tu app lee con permiso del usuario. Health
  Connect corre en el teléfono, no en Wear OS. Hay reportes de sincronización poco fiable en algunos dispositivos.
- **Source:** https://developer.samsung.com/health/blog/reading-body-composition-data-with-galaxy-watch-via-health-connect-api y https://developer.samsung.com/health/overview.html · consulted 2026-10-11
- **Confidence:** [VERIFIED]
- **Re-check if:** Samsung o Google cambian el modelo de permisos de Health Connect; al implementar la integración.

- **Fact:** La Fitbit Web API legacy está en deprecación (anunciada para sept 2026, guías de migración hacia
  Google Health APIs); el tipo de app "Personal" solo accede a la cuenta del propio desarrollador (OAuth 2.0 + PKCE).
- **Source:** https://dev.fitbit.com/build/reference/web-api/developer-guide/authorization/ · consulted 2026-10-11
- **Confidence:** [VERIFIED] (la fecha exacta de corte, re-verificar: hoy ya es posterior al anuncio)
- **Re-check if:** antes de cualquier integración Fitbit — verificar estado actual de Google Health APIs.

- **Fact:** Garmin Health API requiere aprobación como partner (portal no self-serve); Polar AccessLink y Oura
  API v2 existirían como APIs de desarrollador pero no se verificaron sus términos.
- **Source:** solo fuente secundaria (blog de vendor thryve.health) · consulted 2026-10-11
- **Confidence:** NOT VERIFIED
- **Re-check if:** se decide integrar alguno — ir a developer.garmin.com / polar.com/accesslink-api / cloud.ouraring.com.

- **Fact (nota de diseño, no externa):** fallback universal sin API: importar los reportes PDF que exportan las
  apps de los fabricantes como documentos del expediente. No requiere partner ni OAuth.
- **Source:** decisión de diseño, product/brief.md (Out of scope) · 2026-10-11
- **Confidence:** [OPINION/HYPE] (propuesta propia, no verificada con reportes reales)
- **Re-check if:** al probar con un reporte real del dispositivo de Saúl.

## Regulación mexicana de datos de salud (verificado 2026-10-18, texto vigente)

- **Fact:** La LFPDPPP vigente es una **Nueva Ley** publicada en el DOF el 2025-03-20 (última reforma DOF
  2025-11-14); abroga la de 2010 y la autoridad ya NO es el INAI sino la **Secretaría Anticorrupción y Buen
  Gobierno** (art. 3 fr. XV).
- **Source:** texto oficial Cámara de Diputados, https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf ·
  consulted 2026-10-18
- **Confidence:** [VERIFIED]
- **Re-check if:** nueva reforma en el DOF; antes de redactar el aviso de privacidad definitivo.

- **Fact:** El "estado de salud presente o futuro" y la información genética son **datos personales sensibles**
  (art. 3 fr. VI). Para tratarlos se exige **consentimiento expreso Y por escrito** "a través de su firma
  autógrafa, firma electrónica, o cualquier mecanismo de autenticación que al efecto se establezca" (art. 8).
  Además: no pueden crearse bases de datos sensibles sin justificar finalidades legítimas y concretas (art. 8),
  y el periodo de tratamiento debe limitarse al mínimo indispensable (art. 12).
- **Source:** LFPDPPP arts. 3, 8, 12 (texto citado) · consulted 2026-10-18
- **Confidence:** [VERIFIED]
- **Re-check if:** el flujo de consentimiento cambie — hoy el checkbox dentro de una cuenta autenticada encaja en
  "mecanismo de autenticación" [OPINION: confirmarlo con abogado antes de producción].

- **Fact:** Otras obligaciones de la LFPDPPP que GlobalHealth hereda: aviso de privacidad que identifique qué
  datos son sensibles y los mecanismos ARCO y de revocación (arts. 7, 14-15); medidas de seguridad no menores a
  las de la propia información del responsable, ponderando la sensibilidad (art. 18); **notificación inmediata al
  titular de vulneraciones de seguridad** que afecten significativamente sus derechos (art. 19); confidencialidad
  que sobrevive a la relación (art. 20); cancelación con periodo de bloqueo antes de la supresión (art. 24).
  Multas hasta 320,000 UMA, que **se duplican con datos sensibles** (art. 59); los delitos también duplican pena
  en sensibles (art. 64).
- **Source:** LFPDPPP arts. 7, 14-15, 18-20, 24, 59, 62-64 · consulted 2026-10-18
- **Confidence:** [VERIFIED]
- **Re-check if:** al diseñar el plan de incidentes y el flujo de borrado de cuenta (US-02 ya contempla borrar;
  falta el bloqueo previo del art. 24).

- **Fact:** NOM-004-SSA3-2012 (expediente clínico) obliga a los **prestadores de servicios de atención médica**
  (5.1), no al paciente: el expediente es **propiedad del prestador**, pero el paciente tiene "derechos de
  titularidad sobre la información" (5.4); conservación mínima **5 años desde el último acto médico** (5.4);
  los datos solo se dan a terceros con **solicitud escrita del paciente** o de un médico autorizado por él
  (5.5.1); el resumen clínico se entrega a solicitud escrita (5.6); toda nota lleva fecha, hora, nombre y firma
  autógrafa/electrónica/digital (5.10).
- **Source:** texto oficial DOF 2012-10-15, https://www.gob.mx/cms/uploads/attachment/file/512094/NOM-004-SSA3-2012.pdf
  · consulted 2026-10-18
- **Confidence:** [VERIFIED]
- **Re-check if:** —. Implicación [OPINION]: GlobalHealth como app del paciente NO es el expediente clínico del
  prestador; el paciente compartiendo por enlace es ejercicio de su titularidad (5.4/5.5.1), y el enlace revocable
  es análogo digital de la "solicitud escrita". Validar con abogado si el portal del profesional (E4) cambia esto.

- **Fact:** NOM-024-SSA3-2012 regula los SIRES (sistemas de registro electrónico para la salud) de los
  prestadores, con certificación ante la DGIS; NO se verificó en fuente primaria si una app personal controlada
  por el paciente queda dentro de su ámbito.
- **Source:** solo fuentes secundarias (prensa/vendors) · consulted 2026-10-18
- **Confidence:** NOT VERIFIED
- **Re-check if:** antes del portal del profesional (E4) — leer el texto DOF completo de la NOM-024 y el acuerdo
  de intercambio de información en salud; si GlobalHealth intermedia datos hacia médicos, el análisis cambia.

## Dispositivo de pruebas de Saúl y IA en dispositivo (verificado 2026-10-18)

- **Fact:** El dispositivo de pruebas de Saúl Pérez es un **Samsung Galaxy S26 Ultra 1 TB** — la única
  configuración con **16 GB de RAM** (las de 256/512 GB llevan 12 GB). Chipset Snapdragon 8 Elite Gen 5 for
  Galaxy (3 nm), NPU +39% vs generación anterior según Samsung/Qualcomm. Anunciado 2026-02-25 (Unpacked),
  lanzamiento 2026-03-06. Pantalla: 6.9" Dynamic AMOLED 2X LTPO, **1440×3120 px físicos** (~500 ppi, 120 Hz).
  En el navegador eso es un **viewport CSS de ~384×832** (DPR 3.75); el ajuste FHD+ de Samsung no lo cambia
  (baja el DPR, no los px CSS). Dato para la cobertura móvil de Playwright (hallazgo K9 de receta-mexicana).
- **Source:** https://www.gsmarena.com/samsung_galaxy_s26_ultra_5g-14320.php y ficha samsung.com/mx ·
  consulted 2026-10-18 (especificaciones de prensa/catálogo; RAM por configuración coincide en 2 fuentes)
- **Confidence:** [VERIFIED] (gama alta 2026 con NPU: candidato ideal para IA en dispositivo)
- **Re-check if:** —

- **Fact:** Google expone Gemini Nano a apps de terceros vía **ML Kit GenAI APIs** sobre **AICore** (servicio de
  sistema Android). Tareas hoy: **Prompt (texto y multimodal), Summarization, Proofreading, Rewriting, Image
  Description y Speech Recognition**. Privacidad por construcción: la inferencia es local, AICore "aísla cada
  petición y no guarda registro de entradas ni salidas tras procesarlas" y no tiene acceso directo a internet
  (los modelos llegan vía Private Compute Services).
- **Source:** https://developer.android.com/ai/gemini-nano (page updated 2026-10-08) · consulted 2026-10-18
- **Confidence:** [VERIFIED]
- **Re-check if:** antes del spike — la página oficial NO declara estatus (alpha/beta/estable), NI lista de
  dispositivos soportados, NI límites de tokens. Blogs 2026 hablan de Prompt API en alpha/beta con ~4,000 tokens
  de entrada y ~255 de salida [NOT VERIFIED — 255 de salida sería poco para extraer una receta completa], y de
  soporte en Galaxy S24/S25/S26 [NOT VERIFIED]. Verificar en developers.google.com/ml-kit/genai y en el S26 real.

- **Fact (implicación de diseño, no externa):** la inferencia en dispositivo satisfaría NFR-005 (cero retención
  del proveedor) por construcción y con costo marginal cero — candidato natural para el peldaño 3 de la escalera
  de captura (foto+IA) y para el dictado (Speech Recognition local). La web app NO puede tocar AICore: este camino
  implica app Android. El fallback híbrido de Firebase AI Logic manda a la nube cuando Nano no está: si se usa,
  NFR-005 exige desactivarlo o pasar por el proveedor cloud ya evaluado.
- **Source:** análisis propio sobre la fuente anterior · 2026-10-18
- **Confidence:** [OPINION] hasta que el spike lo mida con el corpus real de 74 fotos.
- **Re-check if:** al abrir la story de IA (Q4) / el spike Android.

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

## Humo de leña como factor de riesgo respiratorio en México (verificado 2026-10-19) <a id="humo-lena"></a>
- **Fact:** en México la exposición crónica al humo de leña es una causa reconocida de EPOC adicional al
  tabaquismo, sobre todo en hogares rurales que cocinan o calientan con leña (INER); tesis de la UNAM atribuyen
  25–35 % de los casos de EPOC a la exposición a biomasa (60–70 % al tabaco) y reportan RM 5 (IC95 % 2.4–10.3)
  para el uso doméstico de leña o carbón. La EPOC por biomasa tiene un fenotipo clínico propio.
- **Source:** Revista del INER (2002), https://www.medigraphic.com/pdfs/iner/in-2002/in024a.pdf · tesis UNAM
  https://ru.dgb.unam.mx/bitstream/20.500.14330/TES01000311003/3/0311003.pdf · consulted 2026-10-19
- **Confidence:** [VERIFIED] el riesgo (fuente institucional + tesis coincidentes). NO se encontró un formato
  estándar de historia clínica para registrar la exposición (años, horas/año): la forma de captura en
  product/dominio.md (nunca/antes/actual + años aprox.) es [ASSUMPTION].
- **Re-check if:** se diseña un aviso FR-021 que use la exposición (ahí fijar umbral con guía GOLD o la guía
  mexicana de EPOC).

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

## Mascota, gamificación, onboarding y color (verificado 2026-10-20) <a id="mascota-color"></a>
Pedido por Saúl Pérez 2026-10-20 ("casi como Duolingo"; inbox: "Experiencia casi como Duolingo"). La evidencia de
mascotas en salud es débil; la de accesibilidad y la de explicar por qué se pide un dato es la más sólida.

- **Fact:** Gamificación en actividad física: efecto pequeño-moderado que decae (g=0.42 al final, 0.15 a ~14
  semanas; 16 ECA, n=2,407). En salud mental es heterogénea y casi nunca justificada (70 artículos). En adultos
  mayores la evidencia es escasa (12 estudios, n 9–60).
- **Source:** https://www.jmir.org/2022/1/e26779 · https://mental.jmir.org/2019/6/e13717 ·
  https://pmc.ncbi.nlm.nih.gov/articles/PMC8437506 · consulted 2026-10-20
- **Confidence:** [VERIFIED]
- **Re-check if:** se diseña la gamificación.

- **Fact:** Explicar por qué se pide un permiso aumenta la aceptación (CHI 2014, n=772; Google reporta que la tasa
  de rechazo baja a la mitad). Es sobre permisos del teléfono, no sobre datos clínicos: trasladarlo es inferencia.
- **Source:** https://blues.cs.berkeley.edu/wp-content/uploads/2014/07/p91-tan.pdf ·
  https://research.google/pubs/pub50646/ · consulted 2026-10-20
- **Confidence:** [VERIFIED] el hallazgo; su aplicación a datos clínicos [OPINION].
- **Re-check if:** se mide la tasa de llenado con y sin explicación.

- **Fact:** Agentes con cara: evidencia mixta en adultos mayores (unos prefieren el agente caricatura, otros un
  presentador humano). La gente revela más datos sensibles a un agente virtual si cree que ningún humano observa
  (n=239). No se encontró estudio sobre premiar la divulgación de datos sensibles.
- **Source:** https://www.jmir.org/2020/4/e13726 · https://ict.usc.edu/?p=10267 · consulted 2026-10-20
- **Confidence:** [VERIFIED] (Lucas 2014 vía comunicado); el riesgo de presionar a revelar es [OPINION] sin estudio.
- **Re-check if:** se prueba la mascota con usuarios reales.

- **Fact:** Rachas rotas reducen el uso posterior (7 estudios), menos si se pueden reparar; Duolingo lo reconoce y
  ofrece congeladores. Su registro diferido (+~20 % DAU) y la meta elegida por la persona son cifras de la empresa.
- **Source:** https://udspace.udel.edu/handle/19716/34160 · https://blog.duolingo.com/duolingo-streak-research/ ·
  https://review.firstround.com/the-tenets-of-a-b-testing-from-duolingos-master-growth-hacker/ · consulted 2026-10-20
- **Confidence:** [VERIFIED] el estudio; cifras de Duolingo sin auditoría independiente.
- **Re-check if:** se diseña cualquier mecánica de constancia.

- **Fact:** Color y accesibilidad: WCAG 2.2 AA (4.5:1 texto, 3:1 componentes, 24×24 px de objetivo táctil, el color
  nunca como único medio). NHS: fondo gris claro #f0f4f5, texto #212b32, azul #005eb8, apunta a AAA. El azul se
  percibe algo más confiable en sitios médicos (efecto "limitado"); el campo de color-emoción es incipiente. Con la
  edad empeora la discriminación azul-amarillo. Texto oscuro sobre claro rinde mejor a cualquier edad.
- **Source:** https://www.w3.org/TR/WCAG22/ · https://service-manual.nhs.uk/design-system/styles/colour ·
  https://www.stc.org/techcomm/?p=1499 · https://pmc.ncbi.nlm.nih.gov/articles/PMC3648508 ·
  https://www.nngroup.com/articles/dark-mode/ · consulted 2026-10-20
- **Confidence:** [VERIFIED]; preferencias de color propias de México NOT VERIFIED (no se encontró evidencia).
- **Re-check if:** se define la paleta.

- **Fact:** Expedientes familiares: eRedbook (Reino Unido) digitaliza el libro rojo infantil (crecimiento, vacunas,
  hitos); en My Health Record (Australia) el padre o la madre representa al hijo hasta los 14 años y luego la cuenta
  pasa al adolescente. En México la regla de la LFPDPPP 2025 para menores no se pudo leer en el texto oficial.
- **Source:** https://www.evelinalondon.nhs.uk/about-us/news-events/2022-news/20220110-free-app-easier-for-parents.aspx
  · https://digitalhealth.gov.au/initiatives-and-programs/my-health-record/getting-started/authorised-representatives
  · consulted 2026-10-20
- **Confidence:** [VERIFIED] los dos casos; regla mexicana NOT VERIFIED.
- **Re-check if:** se aborda el expediente de los hijos (consulta legal).
