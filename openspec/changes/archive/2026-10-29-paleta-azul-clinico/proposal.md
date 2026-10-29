# Proposal

Origin: Saúl Pérez (autor) decidió el 2026-10-29 la paleta B · Azul clínico en `product/prototipos/paleta.html`, que
quedó como D22 (`memory/decisions/D22-paleta-azul-clinico-con-contraste-wcag.md`). Dijo «Ya, antes de la mascota» y
pidió sumar la deuda de las casillas: «Sí, 20 px y borde 3:1». Investigación: `memory/research/mascota-color.md`.
Triage: change. Toca `code` (tokens del frontend y dos componentes de `ui/`) y suma una capacidad. Es la primera
parte del hilo 2 (identidad) de la investigación de UX (`memory/inbox/2026-10-28-investigacion-ux-completa.md`). La
mascota va después.

## Why

Los colores de hoy no pasan WCAG 2.2 AA. Son los de shadcn/ui con el verde azulado de la marca
(`frontend/src/index.css:44-119`):
- el texto blanco del botón principal da 3.61:1 en claro y 2.95:1 en oscuro, y se pide 4.5:1;
- el borde de campos y casillas sin marcar da 1.26:1, y se pide 3:1.

Las casillas miden 16 px. En Ejercicio, el nombre de cada actividad va en negritas y pesa más que la pregunta del
grupo. Es la deuda R2-4 de `memory/closed/2026-10-28-ronda-2-de-ejercicio-lista-casillas.md`.

## User story

Como paciente de cualquier edad, quiero una app con colores cómodos y fáciles de leer, para revisar y llenar mi
expediente sin esfuerzo, vea bien o no.

## Acceptance criteria

Los Given/When/Then con datos concretos van en la spec delta.
- **P-1 Texto legible:** todo texto que se mide mide al menos 4.5:1 contra su fondo, en claro y en oscuro. Cuenta
  el título, el texto secundario, el botón principal, el chip elegido y los mensajes de error.
- **P-2 Controles visibles:** el borde de campos, casillas sin marcar y chips sin elegir mide al menos 3:1 contra
  el fondo que los rodea, en claro y en oscuro.
- **P-3 No solo color:** el error se dice con texto junto al campo.
- **P-4 Daltonismo:** con deuteranopía, protanopía y tritanopía emuladas se distinguen el chip elegido, la casilla
  marcada y el error. Es validación manual.
- **P-5 Claro y oscuro:** la marca es el azul de D22 en los dos modos. P-1 y P-2 se miden en ambos.
- **P-6 Casillas:** miden 20 × 20 px. En Ejercicio, la etiqueta de cada actividad va en peso normal y la pregunta
  del grupo en negritas.

## What Changes

- Los tokens de color de `frontend/src/index.css` (`:root` y `.dark`) pasan a la paleta B de D22.
- El `Checkbox` de `components/ui/checkbox.tsx` mide 20 px, y su borde usa el token de controles.
- La variante `outline` de `Button`, que usan los chips sin elegir y los botones secundarios, usa el borde de
  controles en claro también.
- En Ejercicio (`HabitsForm.tsx`), la etiqueta de cada actividad pasa a peso normal y la `legend` a negritas.

## Capabilities

### New Capabilities
- `ux/visual-accessibility`: paleta con contraste medido, controles visibles, casillas y su jerarquía.

### Modified Capabilities
Ninguna. El comportamiento del perfil no cambia.

## Impact

- **Frontend:** `index.css`, `components/ui/checkbox.tsx`, `components/ui/button.tsx` (variante `outline`) y
  `HabitsForm.tsx` (dos `className`).
- **Pruebas:** una nueva, `frontend/tests/visual-accessibility.spec.ts`.
- **Fuera:**
  - el backend;
  - los prototipos ya hechos, que no se repintan (D22);
  - los colores fijos de la plantilla (`Admin/columns.tsx:62`, `Items/columns.tsx:27`, `Sidebar/User.tsx:33`,
    `AuthLayout.tsx:12`);
  - los colores propios de los toasts de sonner (`richColors`, `main.tsx:66`);
  - los tokens de gráficas (`--chart-*`);
  - la mascota.
