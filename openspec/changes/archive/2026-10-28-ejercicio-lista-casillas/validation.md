# Validación — Ejercicio como lista con casillas

Para Saúl Pérez. Abre la app (`http://localhost:8000`) con una cuenta de prueba y entra a **Mi perfil médico →
Hábitos**. El bloque es **Ejercicio**. Pruébalo también en el celular.

## E-1 · La lista siempre a la vista

1. Con una cuenta sin ejercicio guardado, baja hasta Ejercicio.
2. Bajo «¿Qué ejercicio haces?» hay nueve casillas sin marcar: Caminar, Correr, Bicicleta, Nadar, Pesas o gimnasio,
   Fútbol u otro deporte, Yoga o pilates, Baile y Otra. Después aparece una «o» y la casilla «No hago ejercicio».
3. No hay ningún campo de días ni de minutos.

- [ ] Lo vi así

## E-2 · Al marcar aparecen sus preguntas y al desmarcar se quitan

1. Marca **Correr**. Justo debajo de Correr, y antes de Bicicleta, aparecen «Días por semana» y «Minutos cada vez».
2. Marca **Otra**. Debajo aparece primero «¿Cuál?» y luego sus días y minutos.
3. En Correr escribe 3 días y 40 minutos. El total dice «Total de lo anotado: 120 minutos por semana».
4. Desmarca **Correr**. Sus campos desaparecen y el total ya no lo cuenta.
5. Vuelve a marcar **Correr**. Reaparecen tus 3 días y 40 minutos.
6. Desmarca **Correr** y **Otra**. Marca **Caminar**, escribe 5 días y 30 minutos, y pulsa **Guardar**.
7. Vuelve a abrir Hábitos. Caminar está marcada con 5 días y 30 minutos, y Correr no está marcada.

- [ ] Lo vi así

## E-3 · «No hago ejercicio» excluye a las demás

1. Caminar ya está marcada con 5 días y 30 minutos desde E-2 (si no, márcala y escríbelos).
2. Marca **No hago ejercicio**. Caminar se desmarca, y sus campos y el total desaparecen.
3. Marca **Bicicleta**. «No hago ejercicio» se desmarca sola.

- [ ] Lo vi así

## E-4 · Con el teclado

1. Con Tab, llega a la casilla **Caminar** y pulsa **Espacio**. Se marca y el cursor se queda en ella.
2. Pulsa **Tab**. El cursor pasa a «Días por semana» de Caminar.

- [ ] Lo vi así

## Lo de siempre, igual que antes

- Si guardas con un dato faltante, el cursor va al primero que falta y aparece «Contesta esta pregunta.» o «Escribe
  cuál.».
- Mientras guarda, las casillas no se pueden cambiar.
- Si sales con cambios sin guardar, aparece «¿Salir sin guardar?».

- [ ] Lo vi así

## Qué NO hace todavía

- Las casillas son del mismo tamaño que en antecedentes familiares: 16 × 16 px, con el nombre de la actividad como
  zona para tocar. En el prototipo que aprobaste las filas eran más altas. Si en el celular te cuesta atinarles, dímelo
  y lo agrandamos en toda la app, porque es una decisión de estilo de la casa.
- Si pulsas «Guardar» sin marcar nada en Ejercicio, se guarda el bloque vacío y no sale ningún mensaje, como en los
  demás hábitos. En el prototipo salía «Elige al menos una actividad…». Lo aprobaste el 2026-10-28.
- «¿Dónde?» del humo de tabaco ajeno sigue con chips (D18 revisada: tiene un solo «días por semana»).
- El resto de la investigación de UX (mascota y colores, captura) va en cambios aparte.
