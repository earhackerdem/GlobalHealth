# Validación — hábitos: sustancias y humo, Story C1 (para Saúl Pérez)

Guion no técnico. Necesitas la app corriendo con esta rama: `make up` y luego `docker compose up -d --build backend`
(hay una migración nueva; `make up` la aplica). Entra con tu cuenta y ve a **"Mi perfil médico"** en el menú
lateral. Los ejemplos son solo ejemplos: contesta lo que quieras.

## Qué cambia, en una frase

La tarjeta "Hábitos" ya se abre: alcohol, tabaco y vapeador, humo de otras personas y humo de leña, todo opcional y
sin que la app califique tus respuestas. Ejercicio, movimiento del día, sueño y trabajo llegan con la Story C2.

## Antes de empezar

Registra tu fecha de nacimiento en "Editar datos básicos": con ella la app sabe qué edades son imposibles.

## C-1 · Alcohol
1. Toca la tarjeta **Hábitos**. Debe decir "Sin llenar" antes de empezar.
2. En **Alcohol** elige **Actual**. Aparecen tres preguntas (frecuencia, cuántas bebidas, 6 o más en una ocasión) y
   "Sobre todo fines de semana". Contéstalas.
3. Cambia a **Lo dejé** y escribe una edad mayor que la tuya. Toca **Guardar**.
- [ ] Veo "La edad no puede ser mayor que tu edad actual" debajo de ese campo, y no se guarda.
4. Escribe una edad posible y guarda.
- [ ] Vuelvo a "Mi perfil médico" y la tarjeta dice "Con datos".
- [ ] Al abrirla otra vez veo "Lo dejé" con mi edad, y ya no aparecen las tres preguntas.

## C-2 · Tabaco y vapeador
1. Elige **Antes**, escribe cigarros al día, que empezaste a los 30 y lo dejaste a los 18. Guarda.
- [ ] Veo "No puede ser mayor que la edad en que lo dejaste" junto a la edad de inicio.
2. Corrige las edades, elige un **Vapeador o cigarro electrónico** y guarda.
- [ ] Al reabrir, todo está como lo dejé.

## C-3 · Humo de tabaco de otras personas
1. Elige **Casa** y **Trabajo o escuela** (se pueden varias) y escribe los días por semana. Guarda.
2. Reabre y elige **No me expongo**.
- [ ] Los lugares se desmarcan y desaparecen los días.
- [ ] Al guardar y reabrir, queda "No me expongo".

## C-4 · Humo de leña
- [ ] Elijo **Antes**, escribo los años aproximados, guardo y al reabrir lo veo igual.

## C-6 · La app no califica
- [ ] Con respuestas "fuertes" (mucho alcohol, fumar a diario), ni la pantalla de hábitos ni "Mi perfil médico"
  muestran puntajes, niveles de riesgo ni consejos.

## Todo es opcional
- [ ] Puedo contestar una sola cosa (por ejemplo, vapeador "Nunca"), guardar, y la tarjeta dice "Con datos".
- [ ] "Cancelar" vuelve sin guardar.

## Lo que todavía NO hace
- Ejercicio, movimiento del día, sueño y el bloque "Trabajo" del perfil básico (Story C2).
- No avisa si sales de la pantalla sin guardar: lo contestado se pierde, igual que en las otras secciones.
- La experiencia por pasos con mascota ("casi como Duolingo") sigue en el inbox.
