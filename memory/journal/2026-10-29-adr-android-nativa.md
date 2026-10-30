---
date: 2026-10-29
---

# D24: la app de Android nativa

**Quién e intención.** Durante la revisión del PR #40, Saúl Pérez (autor) pidió priorizar la app de Android. Después
pidió que fuera nativa, con iPhone nativo más adelante.

**Objeción y respuesta.** El agente objetó una vez, con chips: tres bases de código para una persona, y D7 había
descartado Kotlin por la curva. Propuso como alternativas Kotlin Multiplatform, React Native o Flutter. Saúl Pérez
respondió que ahora le dedica la mayor parte de su tiempo al proyecto y que quiere aprovechar el hardware. Es su
decisión y quedó así.

**Lo que eligió (las cuatro recomendaciones):**
- v1 «hardware primero»: cuenta, cámara para FR-007, recordatorios de FR-025 y ver el perfil;
- el código en `android/` de este repo;
- un APK por `adb` al principio y la prueba interna de Play después;
- la versión mínima de Android, a decidir con la exploración.

**Qué se registró.**
- D24.
- D7 pasa a `revised`.
- D17 y D23 llevan una nota de revisión: el spike deja de ser la puerta de entrada y la mascota va después de la v1
  de Android.
- `product/technical-brief.md` (§3 y §5) y NFR-011 en el PRD.

**Riesgos que quedan para la exploración:**
- dónde vive el token de la sesión en el teléfono (Keystore);
- nada sensible en claro en el dispositivo (NFR-001);
- si la receta de hoy guarda los horarios de las tomas que necesita FR-025.

**Siguiente.** `/triage` y el primer cambio de Android con el ciclo EPE. Ese cambio suma `android/` a
`harness.json → code` y `tests`.
