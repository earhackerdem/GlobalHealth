---
date: 2026-10-19
status: open
---

[2026-10-19] sr-only del SidebarTrigger dice "Contraer barra lateral" aunque el sheet móvil esté cerrado: deriva
del estado `open` de escritorio, no de `openMobile` (frontend/src/components/ui/sidebar.tsx:274-277; hallazgo del
tester móvil de onboarding-perfil). Quirk de accesibilidad del componente del template.
