# Exploration — paleta-azul-clinico

Date: 2026-10-29 · Explored by: the agent (orquestador) for Saúl Pérez (autor)

## 1. Input validation

- Historia con rol concreto (paciente de cualquier edad), qué y para qué: ✅
- P-1, P-2, P-3, P-5 y P-6 tienen umbrales y datos concretos («Caminar», «Contesta esta pregunta.», `#005eb8`,
  20 px, peso 400/600): ✅
- P-4 es validación manual con la emulación de Chrome. Es observable, pero no automatizable con lo que hay: ✅ manual.
- ⚠️ P-5 fija valores exactos (`#005eb8` y `#5aa9f0`). Imponer un valor técnico en este caso es la decisión misma
  (D22), no un detalle de implementación.

## 2. Coverage matrix

| Criterio | Qué hay hoy | Clase |
|---|---|---|
| P-1 texto | Los tokens de shadcn, con la marca `oklch(0.598 0.107 182)`, están en `frontend/src/index.css:52` (claro) y `:86` (oscuro). Texto blanco sobre ella: 3.61:1 y 2.95:1, medido el 2026-10-29 con la fórmula de luminancia de WCAG sobre los valores convertidos de oklch a sRGB. El texto secundario `#737373` da 4.73:1, al límite. | 🟡 cambiar tokens |
| P-2 controles | `--input` vale `oklch(0.922 0 0)` (`index.css:62`) y da 1.26:1. Lo usan `checkbox.tsx:15`, `input.tsx:11` y la variante `outline` de `button.tsx:15-16`. Esa variante usa `border` (decorativo) en claro y `border-input` solo en oscuro, y es el chip sin elegir de `ChipGroup.tsx:53,152`. | 🟡 tokens + `outline` |
| P-3 no solo color | Los mensajes de error ya son texto («Contesta esta pregunta.») con `aria-invalid`. Lo cubren las pruebas de C-14, C-15 y C-17 en `frontend/tests/profile-habits.spec.ts`. | ✅ existe; una prueba lo vuelve a mirar en la pantalla medida |
| P-4 daltonismo | No hay nada automatizado. Chrome DevTools tiene «Emulate vision deficiencies» en Rendering. | ❌ validación manual |
| P-5 oscuro | El tema `dark`/`light`/`system` vive en `components/theme-provider.tsx:9`, se guarda en `localStorage["vite-ui-theme"]` (`:34`) y pone la clase en `<html>` (`:57-69`). Los tokens oscuros están en `.dark` (`index.css:78-112`). | 🟡 cambiar tokens |
| P-6 casillas | `checkbox.tsx:15` usa `size-4` (16 px). La etiqueta va en `font-semibold` en `HabitsForm.tsx:1558` y la `legend` en `font-medium` en `:1846`. | 🟡 |

**Contraste de los tokens propuestos** (script del agente, 2026-10-29, en `design.md § Tokens`):
- **Claro:**
  - texto 13.02 y 14.42;
  - secundario 5.75–6.37;
  - botón 6.38;
  - error 4.57 sobre el fondo y 5.06 sobre las tarjetas;
  - borde de controles 5.75–6.37.
- **Oscuro:**
  - texto 13.22–15.05;
  - secundario 5.86–8.26;
  - botón 7.03;
  - error 6.78–7.72;
  - borde de controles 4.76–5.42 contra el fondo, y 3.00 contra el relleno `dark:bg-input/30` de su propio
    campo, que es justo el límite. Lo que manda es el contraste contra lo que rodea al campo.
  - el botón destructivo, `dark:bg-destructive/60` con texto blanco, da 5.01.

## 3. Lo que parecía útil y no lo fue

- **Una prueba de captura de pantalla (`toHaveScreenshot`).** El proyecto no la usa, y es frágil entre las fuentes
  de la máquina y las de CI. Medir el contraste con `getComputedStyle`, convirtiendo cualquier formato de color con un
  canvas, sí prueba el criterio.
- **Repintar los colores fijos de la plantilla** (`bg-green-500`, `text-green-500`, `bg-zinc-600`,
  `dark:bg-zinc-900`). Están en pantallas de la plantilla (Admin, Items, avatar, login) y no son los tokens. Quedan
  fuera y anotados.
- **Los colores de sonner (`richColors`).** Son de la librería, con su propia paleta. Quedan fuera.

## 4. Constraints

- **Accesibilidad:** es el objetivo (WCAG 2.2 AA, 1.4.3 y 1.4.11).
- **Rendimiento, seguridad, privacidad y licencias:** sin efecto. Solo cambian CSS y clases.
- **Idioma:** sin textos nuevos.
- **Riesgo:** casi todas las pantallas cambian de color. Las pruebas existentes no miran colores (búsqueda de
  `toHaveCSS` y `getComputedStyle`: solo hay una lectura de `opacity` en `profile-habits.spec.ts:1597`), así que no
  deberían romperse. Lo confirma la suite completa.

## 5. Classification and hints

**Extension:** tokens y dos componentes de `ui/`, con una prueba nueva. No hay preguntas abiertas: Saúl Pérez ya
eligió la paleta, el momento y las casillas.
