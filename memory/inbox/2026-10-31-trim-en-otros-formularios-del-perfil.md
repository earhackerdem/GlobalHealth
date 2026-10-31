---
date: 2026-10-31
status: open
---

Otros formularios del perfil deciden «vacío» con `.trim()` y aceptan un texto invisible (U+200B, U+3164, U+2800) como
dato: `EditBasicData.tsx:91`, `EditFamilyHistory.tsx:78`, `EditWork.tsx:66-67`, `OnboardingWizard.tsx:97/132/205/351`,
`WhenField.tsx:85` (en `frontend/src/components/Profile/`). Lo vio el implementer de validaciones-hoy-y-texto-invisible
(2026-10-31), que pagó solo el historial (B2). `isBlank` ya está compartido en `Profile/text.ts`; el backend de esos
campos usa `.strip()` o nada. Ninguno es un campo requerido, así que el efecto es «guardado algo invisible», no un
requerido saltado. Candidato a la tarea de deudas de la web.
