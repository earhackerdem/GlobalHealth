---
date: 2026-10-20
status: applied
---

Memoria por entrada (harness 0.4.0), pedida por Saúl Pérez tras el choque de #27 con #26

**Por qué:** dos ramas que agregaban filas a `inbox.md` y `research.md` chocaron al mergear, y dos podían tomar el
mismo `D18`. Saúl Pérez eligió el arreglo de fondo ("Lo prefiero de fondo") sobre `merge=union`: toda la memoria y el
CHANGELOG por fragmentos.

**Dónde vive:** earhackerdem/harness#4 (C-11), traído en #28; migración en este PR (`make memory-migrate`).
