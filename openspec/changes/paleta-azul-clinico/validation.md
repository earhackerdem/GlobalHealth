# Validación — paleta azul clínico

Para: Saúl Pérez (autor). Tiempo: unos 10 minutos. Lo recorrió primero el agente, en Chrome, el 2026-10-29.

**Qué cambia para el paciente:** la app pasa del verde azulado al azul clínico que elegiste (D22). Ahora cualquier
texto se lee con contraste suficiente, los campos y las casillas tienen un borde que se ve, y las casillas son más
grandes. En Ejercicio, la pregunta pesa más que las actividades.

**Antes de empezar:** abre http://localhost:8000 con tu cuenta de prueba. El tema se cambia en la barra lateral, en
«Apariencia».

## P-1 y P-5 · Se lee bien, en claro y en oscuro
1. Con el tema **claro**, entra a «Mi perfil médico» y luego a «Hábitos».
2. Mira el botón «Guardar»: es azul con letras blancas. Mira el texto gris de la introducción.
3. Cambia al tema **oscuro** y vuelve a «Hábitos».
4. El botón es azul claro con letras oscuras, y todo el texto se lee sin esforzarte.

- [ ] Lo vi: en los dos temas se lee bien, y el azul es el del prototipo.

## P-2 · Los controles se ven
1. En «Hábitos», mira los chips sin elegir (por ejemplo «Nunca» en Alcohol) y las casillas de Ejercicio sin marcar.
2. Cada uno tiene un borde gris oscuro que se distingue del fondo. Antes casi no se veía.
3. Haz lo mismo en oscuro.

- [ ] Lo vi: chips, casillas y campos tienen un borde visible en los dos temas.

## P-6 · Casillas y la pregunta primero
1. En Ejercicio, mira «¿Qué ejercicio haces?» y las actividades.
2. La pregunta está en negritas y las actividades en letra normal. Las casillas son más grandes que antes (20 px).
3. Abre «Mi perfil médico› Antecedentes familiares › Editar antecedentes»: esas casillas también son más grandes, y
   el diálogo no se descuadra.

- [ ] Lo vi.

## P-3 · El error no es solo color
1. En Ejercicio, marca «Correr» y no escribas los días.
2. Pulsa «Guardar».
3. Junto al campo aparece el texto «Contesta esta pregunta.», además del borde rojo.

- [ ] Lo vi. Si no vas a guardar, desmarca «Correr».

## P-4 · Con daltonismo
1. En «Hábitos», abre las herramientas de Chrome (⌥⌘I) › menú ⋮ › More tools › **Rendering**.
2. En «Emulate vision deficiencies», elige **Deuteranopia**, luego **Protanopia** y luego **Tritanopia**.
3. En cada una, revisa que se distingan la casilla marcada de las demás, el chip elegido de los demás y, si dejaste
   el error del paso anterior, el campo con error.
4. Al terminar, vuelve a «No emulation».

- [ ] Lo vi en las tres.

## Qué NO hace todavía
- Las pantallas que heredamos de la plantilla (Administración, Items, el avatar del menú y la imagen del login)
  tienen colores fijos que no cambiaron.
- Los avisos emergentes (toasts) usan los colores propios de su librería.
- Los prototipos que ya hicimos conservan sus colores; los nuevos usarán esta paleta.
- La mascota viene después, sobre esta paleta.
