---
date: 2026-10-12
status: done
---

**Prototipo mock como paso del ciclo**: pedido de Saúl Pérez — antes de (o junto con) las specs, generar un frontend solo-mock para que usuarios no programadores validen la idea sin leer delta specs; opciones: artifact clickeable generado por el harness (demostrado hoy), o emitir un prompt para Claude Design / v0 / Stitch

**Why it matters:** El gate humano del propose hoy exige leer specs; un prototipo navegable detecta expectativas rotas ANTES de ejecutar (hoy costó un ciclo completo) → meta-mejora al harness

**Status:** ✅ cerrado (improve/harness-0.3.1, 2026-10-20): gate de prototipo desde 0.2.0; desde 0.3.1 el prototipo es HTML local en `product/prototipos/`, sin copia hospedada salvo que se pida
