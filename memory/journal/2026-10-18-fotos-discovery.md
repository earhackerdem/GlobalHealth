# 2026-10-18 · Evidencia empírica para el discovery de receta-mexicana

**Quién:** Saúl Pérez (author) aportó 74 fotos reales de sus documentos médicos (2015–2026) en una carpeta local
(`~/Downloads/Photos-1-001`, fuera del repo) y pidió inventariar "qué podemos utilizar".

**Intención:** sustituir [ASSUMPTION] por [VERIFIED] en `product/dominio.md` con datos reales antes de cerrar el
gate del discovery, siguiendo la regla "empírico antes que documental".

**Qué se hizo:** 3 subagentes leyeron las 74 fotos en paralelo con regla estricta de privacidad (solo estructura:
tipo de documento y campos presentes/ausentes; cero valores personales, cero nombres de medicinas o diagnósticos).
El consolidado entró a `product/dominio.md` § "Evidencia empírica": inventario por tipo (~50 documentos únicos),
confirmaciones y correcciones del catálogo, implicaciones del pipeline foto-OCR y catálogos futuros fuera de la
rebanada. Las 4 preguntas abiertas ganaron una línea de evidencia cada una; el catálogo de Medicina ganó duración y
vía como atributos verificados.

**Hallazgos clave:** diagnóstico escrito solo en ~⅓–½ de recetas; vigencia impresa en 2 de ~33; mitad de las
recetas manuscritas (OCR genérico no basta); ~⅓ del corpus son retomas del mismo papel (hace falta dedupe); hay
documentos de familiares (titular ≠ paciente); la dosis puede ser escalonada/condicional; tipos enteros fuera del
modelo actual (resultados de laboratorio con analitos, órdenes de estudios, comprobantes ligados a portales,
vacunación, nota clínica institucional).

**Verificación:** las fotos no entran al repo (LFPDPPP / regla "nada confidencial"); el diff solo toca
`product/dominio.md` y este journal. Sigue en `Status: draft`: el gate (prototipo + 4 preguntas) sigue siendo de
Saúl.

**Deuda:** los catálogos futuros (laboratorio, vacunación, etc.) quedan anotados pero sin modelar; el prototipo v2
no refleja aún la evidencia nueva (p. ej. dosis escalonada) — se actualiza si Saúl lo pide en el gate.
