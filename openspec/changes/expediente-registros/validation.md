# Validación — expediente-registros (para quien aprueba, sin tecnicismos)

Necesitas la app corriendo (`docker compose up -d` y el frontend en http://localhost:5173) y una cuenta con el
consentimiento aceptado.

## 1. Registrar un diagnóstico
1. Entra y abre **Expediente** en la barra lateral.
2. Pulsa **Agregar diagnóstico**; llena diagnóstico, fecha, profesional y notas; **Guardar**.
- [ ] Veo el aviso "Diagnóstico registrado." y el diagnóstico aparece en la lista con su fecha.

## 2. Registrar una receta
1. Pulsa **Agregar receta**; llena medicamento, fecha, dosis y las dos fechas de vigencia; **Guardar**.
2. Intenta guardar una receta sin dosis.
- [ ] La receta completa se registra ("Receta registrada."); la incompleta no pasa (el formulario lo impide).

## 3. Corregir y eliminar
1. En un registro, abre el menú → **Editar registro**, cambia la dosis y guarda.
2. Luego menú → **Eliminar registro** y confirma.
- [ ] Veo "Registro actualizado." con el cambio reflejado, y tras confirmar, "Registro eliminado." y el registro
      ya no está.

## 4. Adjuntos
1. Abre un registro (click en su título) → sección **Adjuntos** → **Subir archivo** con un PDF o una foto.
2. Descárgalo con **Descargar**.
3. Intenta subir otro tipo de archivo (p. ej. un .zip o .exe).
- [ ] El PDF/foto sube ("Adjunto agregado."), se descarga igual que el original, y el archivo no permitido se
      rechaza con el mensaje "Tipo de archivo no permitido (solo PDF, JPEG o PNG)".

## 5. Privacidad (de palabra, verificado por tests)
- Nadie más ve tus registros: otra cuenta que intente abrirlos recibe "no encontrado", como si no existieran.
- Todo el texto clínico y los archivos quedan cifrados en la base de datos: quien mire la BD directamente solo ve
  texto ilegible.
- Sin aceptar el consentimiento no se puede capturar nada.

## Qué NO hace todavía
- No hay búsqueda ni filtros del expediente (siguiente historia US-06) ni historial familiar (US-05).
- No se comparte nada con profesionales (épica E3): el expediente es solo tuyo.
- Los recordatorios de medicación (tomas de la receta) llegan después (US-16).
- Aviso: los datos de prueba del stub anterior se perdieron con la migración (eran andamiaje de desarrollo).
