---
id: D23
date: 2026-10-29
status: accepted
---

## D23 — Mascota: Axo, un ajolote que explica por qué se pide cada dato y celebra el cuidado, no la completitud

- **Status:** Accepted · 2026-10-29 · decided by: Saúl Pérez (autor), navegando `product/prototipos/mascota.html`.
  El pedido venía del 2026-10-20 («casi como Duolingo»,
  `memory/inbox/2026-10-20-experiencia-casi-como-duolingo-mascota-que.md`).
- **Decision:**
  1. **Personaje: Axo, un ajolote** (variante A del prototipo). Dibujo decorativo: el lector de pantalla lee el
     texto, no al personaje.
  2. **Explica por qué se pide cada dato.** Un «¿Por qué lo pedimos?» junto a cada campo del perfil, con una o dos
     frases. Esto es lo único con evidencia sólida, así que las explicaciones se quedan aunque se apague a Axo.
  3. **Tono:** nunca regaña, nunca insiste, nunca cuenta lo que falta. Si el paciente omite algo, Axo le dice dónde
     lo encuentra después.
  4. **Secciones sensibles** (salud mental, alcohol y otras sustancias): Axo no festeja. Dice quién lo ve y que se
     puede dejar vacío; al guardar solo aparece «Guardado».
  5. **Celebra acciones de cuidado:** compartir el resumen con un médico, registrar una toma, subir un estudio.
     **Nunca un porcentaje de perfil completo.**
  6. **Constancia en las tomas: cuenta semanal** («12 de 14 tomas esta semana»). Sin rachas de días.
  7. **Se puede apagar** en Ajustes › Apariencia, y no se anima si el teléfono pide menos movimiento.
  8. **Axo no es la IA.** Explica la app, no la salud de nadie: no responde preguntas médicas ni sugiere estudios.
     Eso lo hace la IA, siempre con su fuente (O4, O6).
  9. **Cuándo:** se construye como su propio cambio **después de la C2b** (orden de Saúl Pérez: investigación de UX
     → C2b → deudas). La celebración de tomas y de compartir llega con E6 y E3, que todavía no existen.
- **Why:**
  - Explicar por qué se pide un permiso sube la aceptación (CHI 2014, n=772). Trasladarlo a datos clínicos es
    inferencia (`memory/research/mascota-color.md`).
  - Premiar la completitud empuja a revelar datos sensibles para subir el número. Es la objeción anotada el
    2026-10-20; no se encontró estudio a favor ni en contra.
  - Perder una racha reduce el uso después (7 estudios). La cuenta semanal informa sin castigar el día que se falla;
    esto último es propuesta nuestra, no algo medido.
  - [OPINION] El ajolote es de México y regenera sus tejidos, y da calidez a la paleta D22, que puede verse
    institucional.
- **Discarded alternatives:**
  - **B · Lati, un corazón:** identidad genérica; es el símbolo más usado en apps de salud.
  - **C · Sin personaje:** cuesta menos, pero no es lo que Saúl Pérez pidió.
  - **Celebrar el perfil completo (%)** y **no celebrar nada.**
  - **Racha de días** y **no contar las tomas.**
  - **Construir ya, antes de la C2b** y **después de las deudas.**
- **Risks the agent noted, accepted by Saúl Pérez:**
  - Con personas mayores la evidencia de agentes con cara es mixta (JMIR 2020).
  - Un animal caricaturesco junto a temas sensibles puede sentirse infantil; lo mitigan los puntos 4 y 7.
  - Ningún criterio mide todavía si las explicaciones suben el llenado: se mide cuando haya usuarios.
- **Applies to:** `product/prd.md` (FR-032, FR-033, US-20); el asistente de bienvenida
  (`frontend/src/components/Profile/OnboardingWizard.tsx`), las secciones del perfil, Ajustes y el expediente vacío
  cuando se construya. Criterios MA-1..MA-7 en el prototipo.
