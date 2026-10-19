# Validación — receta a la mexicana (para Saúl, sin tecnicismos)

Cómo probarlo: `make up`, entra a http://localhost:5173 (o el puerto de tu `make front`), inicia sesión y ve a
**Expediente**. Cada bloque es un criterio del prototipo que navegaste; marca lo que veas.

## AC-1 · Una receta registra varias medicinas
1. Pulsa **A mano** y captura: médico "Dra. Islas (endocrinología)", fecha de hoy, medicina 1 "Levotiroxina 50 µg"
   con dosis "1 tableta en ayunas" y frecuencia "cada 24 h"; **+ Agregar otra medicina**: "Omeprazol 20 mg",
   dosis "1 cápsula antes del desayuno por 14 días", sin frecuencia. Guarda.
- [ ] Aparece la receta con LAS DOS medicinas y la fecha en dd/mm/aaaa.

## AC-3 · El diagnóstico es opcional
- [ ] La receta anterior se guardó SIN diagnóstico y no te lo exigió.
- [ ] Si capturas otra con diagnóstico "faringitis", el chip del diagnóstico se muestra.

## AC-9 · Frecuencia opcional
- [ ] En la lista, la Levotiroxina muestra "· cada 24 h" y el Omeprazol no muestra frecuencia (no se inventó).

## AC-6 · Todo es corregible
1. Edita la receta: cambia la frecuencia, quita el Omeprazol, agrega "Ibuprofeno 400 mg".
- [ ] La lista refleja exactamente lo que dejaste.
- [ ] Si intentas guardar una receta sin ninguna medicina, avisa "Agrega al menos una medicina." y no guarda.

## AC-8 · Archivar cuando el tratamiento termina
1. En una receta activa pulsa **Archivar (tratamiento terminado)**.
- [ ] Desaparece de las activas y aparece abajo en **Archivadas** con su chip.
- [ ] **Desarchivar** la regresa a activas sin perder nada.

## AC-5 · Diagnóstico suelto
1. Registra un diagnóstico sin receta.
- [ ] Se guarda y muestra el estado **"sin confirmar"**.

## AC-4 · La foto original queda adjunta
1. En una receta, adjunta la foto (imagen o PDF).
- [ ] Queda listada en el registro y se puede descargar.

## Tus datos viejos
- [ ] Las recetas que ya tenías aparecen como recetas de UNA medicina; si tenían vigencia, está anotada al final
  de las notas ("Vigencia migrada: …"). Nada se borró.

## Lo que esta entrega NO hace todavía (a propósito)
- **No lee la foto** (OCR/IA): es la segunda story, cuando se decida el proveedor (tu S26 compite con el spike).
- **No hay dictado**: en web el micrófono del navegador manda tu voz a servidores del fabricante; va al spike
  Android.
- **Nadie puede confirmar un diagnóstico aún**: el estado existe, el flujo del médico llega con los enlaces
  (E3/E4).
- No modela laboratorios, vacunas ni notas clínicas (catálogos futuros del discovery).
