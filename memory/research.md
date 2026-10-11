# Verified research

Facts with source, verification date and confidence level. A fact here is cited with **the authority its record
gives it**, never more. If two records of the same fact disagree, the more conservative one rules until you go back
to the source. Market-sensitive records expire after ~3 months.

## <topic> <a id="topic"></a>
- **Fact:** …
- **Source:** <URL or file:line> · consulted YYYY-MM-DD
- **Confidence:** [VERIFIED] / [OPINION/HYPE] / NOT VERIFIED
- **Re-check if:** <what would make it expire>

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
