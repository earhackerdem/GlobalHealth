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
  lanzamiento 2026-03-06.
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
