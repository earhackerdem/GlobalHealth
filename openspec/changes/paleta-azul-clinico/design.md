# Design

Status: DRAFT

**En una frase:** los tokens de color del frontend pasan a la paleta B · Azul clínico de D22, con contraste AA medido
en claro y en oscuro; las casillas miden 20 px; y en Ejercicio la pregunta pesa más que sus opciones. Todo se
comprueba con una prueba que mide los colores reales de la pantalla de hábitos.

## Context

- D22: Saúl Pérez eligió la paleta en `product/prototipos/paleta.html`.
- Hoy: tokens de shadcn en `frontend/src/index.css:44-112`, con la marca en verde azulado. Las mediciones y las citas
  están en `exploration.md § 2`.

## Goals / Non-Goals

- **Goals:** P-1, P-2, P-3, P-5 y P-6, probados automáticamente; P-4, validado a mano.
- **Non-Goals:**
  - los colores fijos de la plantilla (Admin, Items, avatar, `AuthLayout`);
  - los toasts de sonner;
  - los tokens `--chart-*`;
  - los prototipos ya hechos;
  - la mascota;
  - el backend.

## Qué se toca / qué NO

- **Se toca:**
  - `frontend/src/index.css`: solo los valores de `:root` y `.dark`. No se tocan nombres de token ni `@theme`.
  - `frontend/src/components/ui/checkbox.tsx`: `size-4` pasa a `size-5`, y el ícono a `size-4`.
  - `frontend/src/components/ui/button.tsx`: la variante `outline` usa `border-input` también en claro.
  - `frontend/src/components/Profile/HabitsForm.tsx`: la etiqueta de la actividad (`:1558`) pasa a peso normal y la
    `legend` (`:1846`) a `font-semibold`.
  - `frontend/tests/visual-accessibility.spec.ts`: prueba nueva, la escribe el tester.
- **NO se toca:**
  - los demás componentes de `ui/`;
  - `ChipGroup.tsx`, porque hereda la variante `outline`;
  - `FamilyHistoryFields.tsx`, que hereda el tamaño de la casilla;
  - los textos y las traducciones;
  - el backend.

## Tokens

Los valores van en hex. Así `getComputedStyle` devuelve `rgb()` y queda una sola fuente que se puede comparar con
`P.B` del prototipo.

| Token | Claro | Oscuro |
|---|---|---|
| `--background` | `#f0f4f5` | `#0f1a22` |
| `--foreground`, `--card-foreground`, `--popover-foreground`, `--secondary-foreground`, `--accent-foreground`, `--sidebar-foreground`, `--sidebar-accent-foreground` | `#212b32` | `#e8eef1` |
| `--card`, `--popover`, `--sidebar` | `#ffffff` | `#172630` |
| `--primary`, `--sidebar-primary`, `--ring`, `--sidebar-ring` | `#005eb8` | `#5aa9f0` |
| `--primary-foreground`, `--sidebar-primary-foreground` | `#ffffff` | `#0b1a26` |
| `--secondary`, `--muted`, `--accent`, `--sidebar-accent` | `#e8edee` | `#223644` |
| `--muted-foreground` | `#4c6272` | `#a3b4bf` |
| `--destructive` | `#d5281b` | `#ff8a80` |
| `--border`, `--sidebar-border` (decorativo) | `#d8dde0` | `#2a3b47` |
| `--input` (borde de controles) | `#4c6272` | `#7a92a1` |
| `--chart-*`, `--radius` | sin cambio | sin cambio |

## Interface contract

Lo que ejercita `frontend/tests/visual-accessibility.spec.ts`: Playwright, chromium y s26-ultra, con una cuenta
creada por API como en `profile-habits.spec.ts`.

- **Pantalla:** `/perfil/habitos`.
- **Tema oscuro:** `localStorage["vite-ui-theme"] = "dark"` antes de cargar. `<html>` lleva la clase `dark`.
- **Medición:**
  - El color se lee con `getComputedStyle` y se normaliza a sRGB pintándolo en un `canvas` 1×1 y leyendo el píxel.
    Así sirve para cualquier formato.
  - El fondo efectivo es el primer `background-color` con alfa mayor que 0 del elemento o de sus ancestros.
  - El contraste usa la fórmula de WCAG 2.2: luminancia relativa y (L1 + 0.05) / (L2 + 0.05).
- **Elementos (por rol y nombre, como el resto de la suite):**
  - el título: `heading` «Hábitos»;
  - el texto secundario: el párrafo que empieza «Contesta los hábitos que quieras»;
  - «Guardar»: `button` «Guardar». Se mide `color` contra `background-color`, en reposo y sin hover; el foco va
    fuera antes de medir;
  - el chip elegido y el chip sin elegir: un grupo de chips de la pantalla, eligiendo una opción;
  - la casilla «Caminar» y la casilla «Correr»: `checkbox`. Se mide `border-color` de «Correr» sin marcar;
  - «Días por semana» de caminar: `spinbutton` o `textbox`, como hoy en `profile-habits.spec.ts`. Se mide
    `border-color`;
  - el error «Contesta esta pregunta.», que aparece al pulsar «Guardar» con «Caminar» marcada y sin días.
- **Umbrales:** 4.5 para texto; 3 para bordes, contra el fondo efectivo del padre del control.
- **Exactos:** `background-color` de «Guardar» es `rgb(0, 94, 184)` en claro y `rgb(90, 169, 240)` en oscuro. La
  casilla «Caminar» mide 20 × 20 px, con ±0.5 px de tolerancia (`boundingBox`). El `font-weight` de la etiqueta
  «Caminar» es 400 y el de la `legend` «¿Qué ejercicio haces?» es al menos 600.

## Decisions

1. **Tokens en hex**, no en oklch. Coinciden uno a uno con D22 y con el prototipo, y la prueba los compara directo.
   Se descarta convertirlos a oklch como el resto de shadcn: no aporta nada aquí y oscurece la comparación.
2. **`--border` decorativo separado de `--input`.** Las líneas de tarjetas y separadores quedan suaves (`#d8dde0`).
   Solo los controles llevan el borde de 3:1. Se descarta subir todo `--border` a 3:1: llenaría la pantalla de líneas
   oscuras.
3. **`outline` con `border-input` en claro.** El chip sin elegir es un control: P-2 aplica. Se descarta tocar
   `ChipGroup`, porque la variante es la fuente.
4. **Casilla a 20 px en el componente**, no en cada uso. Afecta también a los antecedentes familiares, que es lo que
   Saúl Pérez pidió («para toda la app»).
5. **El modo oscuro es nuestro** (D22: el NHS no tiene). Se mide igual que el claro.

Citers que caducan en este mismo cambio:
- D22, que pasa a «aplicada» al archivar;
- `memory/closed/2026-10-28-ronda-2-de-ejercicio-lista-casillas.md`: R2-4 y el tamaño de casilla quedan resueltos;
- el inbox de la investigación de UX.

## Test plan

| # | Escenario | Nivel | Prueba |
|---|---|---|---|
| 1 | P-1 texto legible en claro | e2e | «P-1 texto legible en claro» |
| 2 | P-2 controles visibles en claro | e2e | «P-2 controles visibles en claro» |
| 3 | P-5 oscuro: P-1 y P-2 con la marca `#5aa9f0`, y claro con `#005eb8` | e2e | «P-5 …» |
| 4 | P-3 el error dice texto y `aria-invalid` | e2e | «P-3 el error no es solo color» |
| 5 | P-6 casilla de 20 px y jerarquía en Ejercicio | e2e | «P-6 casillas y jerarquía» |
| 6 | P-4 daltonismo emulado | manual | `validation.md`, emulando tres deficiencias en Chrome |
| 7 | Regresión: nada más cambia | e2e | la suite completa, en verde como CI |

## Risks / Trade-offs

- **Todas las pantallas cambian de color.** Mitigación: suite completa, más un pase exploratorio en Chrome por
  login, expediente, perfil, hábitos y ajustes, en claro y en oscuro.
- **La casilla de 20 px puede mover el diseño en antecedentes familiares.** Mitigación: revisarlo en el pase
  exploratorio.
- **El hover de `bg-primary/90`** no se mide: es un estado transitorio y su contraste es muy parecido al del reposo.

## Gate

`visual-accessibility.spec.ts` en verde en chromium y s26-ultra; suite completa como CI; `tsc` y `biome` limpios;
`make tdd-check`; pase exploratorio sin defectos; `validation.md` recorrido por el agente antes que Saúl Pérez.
