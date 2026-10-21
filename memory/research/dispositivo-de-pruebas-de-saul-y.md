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
