# 2026-10-20 · Memoria migrada a un archivo por entrada (harness 0.4.0)

- Saúl Pérez mergeó #27 y #28. Con la capa 0.4.0 ya en `main`, se corrió `make memory-migrate DRY_RUN=1` y después
  la migración real, en su propio PR.
- Resultado: 27 inbox (16 abiertos, 1 aparcado, 10 cerrados), 39 veredictos en `closed/`, 18 decisiones, 8
  meta-improvements y 13 temas de investigación. La comprobación de cobertura pasó: cada línea no vacía de los
  archivos viejos está en los nuevos. `CHANGELOG.md` se genera idéntico byte por byte desde `changelog.d/_legacy.md`.
- Verificación: `make memory-check` limpio (ids únicos, estados conocidos); `make doctor` lista las carpetas sin
  avisos; `make inbox` y `make closed` (39 veredictos) funcionan; `make decision-next` da D19.
- Lo que cambia para quien trabaja aquí: una idea nueva es `memory/inbox/YYYY-MM-DD-slug.md`, un veredicto es
  `memory/closed/…`, una decisión es `memory/decisions/D<n>-slug.md` (`make decision-next`), y al archivar un
  cambio se escribe un fragmento en `changelog.d/`; `make changelog` genera el CHANGELOG en `main`, nunca en el PR
  de un cambio. Cada carpeta tiene un README con la plantilla.
- Pendiente para Saúl Pérez: el inbox pide triage (16 abiertos). 11 eran viñetas añadidas bajo `## Closed` sin marca
  de cierre, que el hook viejo nunca mostraba. Entre ellas están el ADR de nombres de tabla y FR-014.
