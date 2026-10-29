## Formularios: pestañas, acordeón, campos que aparecen (verificado 2026-10-28) <a id="formularios-ux"></a>
Lo pidió Saúl Pérez el 2026-10-28 (`memory/inbox/2026-10-28-investigacion-ux-completa.md`). En Ejercicio, los
campos de cada actividad elegida se apilan unos debajo de otros, y él propuso pestañas. Las variantes están en
`product/prototipos/ejercicio-variantes.html`.

- **Fact:** NN/g recomienda pestañas cuando el contenido largo tiene grupos claros y las etiquetas son cortas. No
  las recomienda si hay muchas pestañas ("the fewer tabs, the better") ni si el usuario tiene que comparar o
  consultar varias. Las pestañas no seleccionadas deben verse. El acordeón funciona mejor en el celular y las
  pestañas en escritorio. No dice nada sobre formularios ni sobre errores dentro de una pestaña.
- **Source:** https://www.nngroup.com/articles/tabs-used-right/ · consulted 2026-10-28
- **Confidence:** [VERIFIED]
- **Re-check if:** se diseña un patrón de pestañas para el perfil.

- **Fact:** GOV.UK Design System no recomienda pestañas para contenido que se recorre paso a paso, para comparar,
  ni como navegación de página. Advierte que esconden contenido. El componente no se ha probado con usuarios, y
  queda pendiente cómo funciona en pantallas pequeñas y con lector de pantalla.
- **Source:** https://design-system.service.gov.uk/components/tabs/ · consulted 2026-10-28
- **Confidence:** [VERIFIED]
- **Re-check if:** GOV.UK publica investigación del componente.

- **Fact:** GOV.UK (casillas): mostrar una pregunta al marcar una opción sirve para una sola pregunta simple. Si
  es complicada o tiene varias partes, recomienda pasarla a la página siguiente. No siempre se avisa al lector de
  pantalla cuando la pregunta aparece (falla WCAG 2.2, 4.1.2). En sus pruebas, las preguntas simples no causaron
  problemas y las complicadas confundieron.
- **Source:** https://design-system.service.gov.uk/components/checkboxes/ · consulted 2026-10-28
- **Confidence:** [VERIFIED]
- **Re-check if:** cambia la guía de "conditional reveal".

- **Fact:** El patrón de pestañas de la APG (W3C) usa `tablist`, `tab` (con `aria-selected` y `aria-controls`) y
  `tabpanel`. Las flechas mueven entre pestañas y dan la vuelta al llegar al final; Home y End son opcionales. Se
  recomienda la activación automática cuando el panel aparece sin demora. Se ve un solo panel a la vez.
- **Source:** https://www.w3.org/WAI/ARIA/apg/patterns/tabs/ · consulted 2026-10-28
- **Confidence:** [VERIFIED]
- **Re-check if:** se implementan pestañas.

- **Fact (medido en el prototipo, Chromium headless a 400 px, 2026-10-28):** con las 9 actividades elegidas:
  - Pestañas: la fila se desborda y solo se ven 4 pestañas; las demás quedan fuera hasta desplazarla de lado.
  - Si una actividad elegida se vuelve a tocar en los chips, se desmarca, así que los chips no sirven como
    pestañas; hace falta una segunda fila.
  - Filas compactas: 9 filas sin desborde horizontal.
  - Acordeón: el resumen de cada actividad cerrada muestra lo que falta.
  - Lista con casillas (variante E, propuesta de Saúl Pérez el 2026-10-28): las 9 actividades siempre a la vista y
    sin desborde. Una actividad marcada abre sus campos debajo. Espacio sobre la casilla los abre y Tab entra al
    primero. «No hago ejercicio» desmarca las demás, y marcar otra desmarca «No hago ejercicio».
- **Source:** `product/prototipos/ejercicio-variantes.html` · recorrido con Playwright, 2026-10-28
- **Confidence:** [VERIFIED] en el prototipo. La variante E elegida se confirmó en la pantalla real a 384 px y en Chrome (`openspec/changes/archive/2026-10-28-ejercicio-lista-casillas/evidence.md`, 2026-10-28).
- **Re-check if:** cambia el catálogo de actividades.
