---
id: D21
date: 2026-10-29
status: accepted
---

## D21 — Captura híbrida: el texto del paciente más un código de un vocabulario propio

- **Status:** Accepted · 2026-10-29 · decided by: Saúl Pérez (autor), navegando
  `product/prototipos/captura-hibrida.html`. La dirección híbrida venía del 2026-10-20
  (`memory/inbox/2026-10-20-ronda-2-del-dominio-medicina-diagnostico.md`).
- **Decision:** lo que el paciente escribe como diagnóstico o condición **se guarda siempre con sus palabras**. Si
  la app lo reconoce, se le agrega por dentro un concepto con su código CIE-10.
  1. **Variante A: sugerir mientras escribe.**
     - Hasta 3 conceptos y siempre «Dejarlo como lo escribí».
     - El reconocimiento se ve como «La app lo reconoce como …» y se puede quitar.
     - El código no se le muestra al paciente; lo usan el médico, los enlaces por categoría (FR-014) y la IA.
  2. **Vocabulario propio, no la CIE-10 completa.**
     - Son unos 20 conceptos en palabras de paciente, cada uno con sinónimos y su código.
     - Parte de las claves que ya existen en Crónicas (`frontend/src/components/Profile/history.ts:69`) y en
       Antecedentes familiares (`FamilyHistoryFields.tsx:8`), más diagnósticos comunes de receta.
     - Crece con lo que la gente escribe y no se reconoce.
     - Los conceptos de salud mental quedan sensibles al reconocerse.
     - Un término ambiguo («artritis») ofrece las opciones; la app no adivina.
  3. **«¿Para qué es?» por medicina**, opcional.
     - Liga cada medicina de una receta con una crónica propia o con el diagnóstico de esa receta.
     - La crónica muestra sus medicinas ligadas.
     - El «Tratamiento actual» en texto **convive** con ellas, para lo que no viene en una receta.
  4. **Nombre de medicina:** las sugerencias salen **solo de las recetas propias del paciente**, con la dosis de
     la vez pasada. No hay catálogo externo.
- **Why:**
  - Los nombres oficiales de la CIE-10 de la DGIS no hablan como el paciente: «diabetes tipo 2», «presión alta» y
    «colesterol alto» dan 0 coincidencias.
  - La DGIS no publica licencia, y su propio criterio es registrar el texto junto con el código.
  - FHIR modela lo mismo: `text` más `coding` con `userSelected`.
  - No hay catálogo mexicano de medicinas descargable: el CNIS es un PDF de 42 MB, solo de genéricos.
  - La IA sola acertó el código exacto en 33.9 % de los casos (NEJM AI, 2024), así que reconocer al capturar,
    con el paciente eligiendo, es más confiable que codificar después.
  - Fuentes y fechas en `memory/research/captura-catalogos.md`.
- **Discarded alternatives:**
  - **B, preguntar al guardar:** la pregunta llega después y se ignora; lo no contestado queda como en C.
  - **C, solo texto:** el médico y la IA ven «presión alta» y «Hipertensión» como cosas distintas.
  - **Importar la CIE-10 completa:** licencia no verificada, nombres inservibles para el paciente y 14,498 filas
    que mantener.
  - **El tratamiento de la crónica solo con las medicinas ligadas:** pierde lo que no viene en una receta.
  - **Medicinas sin sugerencias:** gana poco.
- **Consequences and open edges:**
  - Las sugerencias son una lista dinámica, así que caen en la excepción de D18 (buscador, no chips).
  - Cuatro códigos del prototipo son [ASSUMPTION] hasta confirmarlos contra el XLSX de la DGIS: J029, N390, K297
    y G439.
  - Ligar una medicina a «lo de esta receta» no la liga sola a la crónica del mismo concepto. El paciente ve solo
    lo que ligó; el médico ve agrupado por concepto.
  - Si alguna vez se embarca el catálogo DGIS o se ofrece a clínicas, revisar licencia y NOM-024
    (`memory/research/captura-catalogos.md`, «Re-check if»).
- **Applies to:**
  - el diagnóstico suelto (FR-005);
  - el diagnóstico de la receta y sus medicinas (FR-006);
  - «Otra, ¿cuál?» de Crónicas, Enfermedades pasadas y Antecedentes familiares (FR-008, FR-028).

  Se construye como stories nuevas (`product/prd.md` FR-029..031), no al reabrir pantallas por otra razón.
