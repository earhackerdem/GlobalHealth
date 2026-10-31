---
date: 2026-10-29
status: open
---
App de Android: ¿`FLAG_SECURE` en las pantallas con datos de salud? (X1 de la revisión del PR #44)

**Why it matters:** sin `FLAG_SECURE` (`android/app/src/main/java/mx/globalhealth/paciente/MainActivity.kt`):
- el sistema guarda la miniatura de Recientes con «Mi perfil médico» (alergias, peso, trabajo) fuera de los archivos
  de la app;
- otras apps con permiso de grabar la pantalla pueden verla.

Con la bandera, el paciente tampoco puede hacer capturas de su propio perfil. Es una línea de código, pero la decisión
es de producto. Saúl Pérez la mandó aquí el 2026-10-29: «Al inbox». Conviene decidirla antes de que la app muestre
más datos (la cámara y los recordatorios, D24).
