---
date: 2026-10-26
status: open
---

**Dos `<main>` anidados en el layout autenticado** (visto por el implementer de perfil-habitos-actividad-sueno,
2026-10-26): `SidebarInset` ya rinde un `<main>` (`frontend/src/components/ui/sidebar.tsx:325`) y
`frontend/src/routes/_layout.tsx:31` agrega otro adentro. Vienen del commit del esqueleto `cb48c3a`. Un landmark
`main` anidado es inválido (WCAG 1.3.1 / ARIA landmarks) y hace que `page.locator("main")` choque con el modo estricto
de Playwright (la fila 10 de esa C2a tuvo que acotar su localizador). Arreglo probable: el interior como `<div>`, con
la suite completa de Playwright como red. Entra en la tarea de deudas (`2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`).

**Why it matters:** los lectores de pantalla anuncian dos regiones principales, y cada prueba nueva que busque `main`
vuelve a tropezar.
