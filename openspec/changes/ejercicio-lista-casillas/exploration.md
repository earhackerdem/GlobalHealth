# Exploration — ejercicio-lista-casillas

Fecha: 2026-10-28 · Entrada: `proposal.md` (E-1 a E-4) y la spec delta. La variante la eligió Saúl Pérez en
`product/prototipos/ejercicio-variantes.html` (E); la investigación está en `memory/research/formularios-ux.md`.

## 1. Input validation

| Check | Result |
|---|---|
| As/I want/so that story with a concrete role | ✅ «Como paciente, quiero ver todas las actividades como una lista y marcar las que hago…» |
| Every AC in Given/When/Then with concrete data | ✅ E-1 a E-4 en la spec delta, con actividades, días y minutos concretos |
| No imposed technical solution | ⚠️ «lista con casillas» es una forma de pantalla, pero es justo lo que se decidió (D18 revisada, variante E navegada); no impone una librería |

## 2. Coverage matrix per criterion

| AC | Coverage | Where (file:line / URL + date) | Missing |
|---|---|---|---|
| E-1 lista siempre a la vista | 🟡 Partial | El catálogo y su orden ya existen (`ACTIVITIES`, `HabitsForm.tsx:105`); hoy se pintan como chips (`ChipMultiGroup`, `HabitsForm.tsx:1781-1800`, componente en `ChipGroup.tsx:111`) | Casillas en lugar de chips; la «o» antes de «No hago ejercicio» |
| E-2 marcar abre debajo, desmarcar quita | 🟡 Partial | Precedente en la app: en antecedentes familiares cada casilla abre sus campos debajo (`FamilyHistoryFields.tsx:65-84`, `Checkbox` de `components/ui/checkbox.tsx`, Radix 1.3.11). En hábitos los campos de cada actividad salen después de todo el grupo (`HabitsForm.tsx:1802-1811`, `chosenActivities` en `:194`); lo no elegido ya se descarta al guardar y no entra en el total (`:497`, `:631`) | Pintar los campos dentro de cada fila de la lista |
| E-3 excluyente | ✅ Exists (lógica) | `ChipMultiGroup` ya vacía las demás al elegir la excluyente y la apaga al elegir otra (`ChipGroup.tsx:104-110`) | Llevar esa regla a la lista con casillas |
| E-4 teclado, lector, foco del error | 🟡 Partial | Radix Checkbox es un `button role="checkbox"` con `aria-checked`, Espacio lo marca y el foco se queda; APG checkbox pattern (https://www.w3.org/WAI/ARIA/apg/patterns/checkbox/, consultado 2026-10-28). El foco del error de grupo busca `fieldset[data-invalid] button` (`HabitsForm.tsx:1158-1166`), que también encuentra la primera casilla si el grupo es un `fieldset` | Grupo como `fieldset` con `legend` «¿Qué ejercicio haces?»; comprobar que el foco cae en «Caminar» |
| C-5, C-13…C-17, D20 siguen vigentes | ✅ Exists | Reglas de guardado, obligatoriedad y errores en `HabitsForm.tsx` (`requiredOf`, `visibleNumbers`, `numberField` en `:1413`); el servidor no cambia | Que las pruebas actuales del ejercicio sigan pasando con casillas |

## 3. What looked useful and was discarded (and why)

- **Pestañas (variante A, propuesta original de Saúl Pérez):** a 400 px se ven 4 de 9 pestañas, los errores en las
  ocultas no se ven y un chip marcado se desmarca al tocarlo de nuevo (`memory/research/formularios-ux.md`).
- **Acordeón (B), filas compactas (C), una por una (D):** navegadas en el mismo prototipo; Saúl Pérez eligió la E.
- **Casilla nativa `<input type="checkbox">`:** la app ya usa el `Checkbox` de Radix en antecedentes familiares e
  historial; otro estilo de casilla rompería la consistencia que D18 busca.
- **Cambiar `ChipMultiGroup` para que dibuje casillas:** mezclaría dos patrones en un componente que sigue usando
  «¿Dónde?» del humo ajeno (`HabitsForm.tsx:1725`).

## 4. Non-functional constraints

- **Accesibilidad (NFR del technical brief):** grupo con nombre, casilla con nombre propio, foco visible, error unido
  al grupo (`aria-describedby`); el aviso de que aparecieron campos nuevos no lo da el lector (GOV.UK, WCAG 4.1.2), pero
  los campos quedan justo después de la casilla en el orden del teclado, que es lo que GOV.UK probó sin problemas.
- **Celular (s26-ultra en Playwright):** la lista no se desborda a 400 px (medido en el prototipo).
- **Privacidad, cifrado, servidor:** sin cambios.
- **Idioma:** textos es-MX en `profile.json`; «o» es texto nuevo.

## 5. Classification and questions

**Extension** (solo pantalla). Sin preguntas bloqueantes. Supuesto: la casilla «No hago ejercicio» va al final,
separada con «o», como en la variante E navegada.
