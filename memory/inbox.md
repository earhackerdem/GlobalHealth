# Inbox

Entry is cheap (one row: what and why it matters, no research, no decision). Exit is mandatory: ✅ done (anchor to
the PR or commit), ❌ discarded (reason), 💤 snoozed until YYYY-MM-DD. Nothing is deleted. An inbox item is not a
task: if the person you work with doesn't mention it, it is not started.

## Open

| Date | What | Why it matters | Status |
|---|---|---|---|
| 2026-10-12 | Atomic Design + Storybook para el frontend (pedido de Saúl Pérez al decidir i18n). Objeción anotada del harness: el template ya trae su propia organización (shadcn/ui + components/ por dominio) y Storybook es mantenimiento no funcional continuo para un solo dev pre-producto; alternativa barata: posponer a cuando haya un segundo consumidor de componentes (diseñador, segundo dev, design system). Si Saúl reafirma, va como story propia con ADR | Reorganizar components/ toca TODO el frontend; mejor decidirlo con exploración y no de pasada | abierto |
| 2026-10-12 | `scripts/generate-client.sh` reformatea TODO el árbol del frontend (`biome --write --unsafe`) como efecto colateral de regenerar el cliente; sorprendió al implementer del grupo 3 de expediente-registros | Un script de codegen no debería tocar archivos ajenos a `src/client/`; radio de daño inesperado en working trees sucios | ✅ cerrado (fix/dev-migraciones-y-cliente, 2026-10-20): el script ya no corre `bun run lint`; el cliente está excluido de biome y el resto se formatea al commitear (hook local-biome-check) |
| 2026-10-12 | **Receta a la mexicana** (feedback de Saúl Pérez tras probar el PR #6; no leyó las delta specs y el resultado no cumplió su expectativa): una receta real trae varias medicinas, fecha de expedición y nombre del paciente; NO trae vigencia inicio/fin y normalmente NO trae diagnóstico (se dice de palabra) → el modelo debería ser receta con medicinas[] y diagnóstico como campo opcional, no dos tipos con vigencia obligatoria. Intención de fondo: subir foto de la receta (o cámara) y que OCR+IA llene los campos. Prototipo clickeable para validar el flujo: https://claude.ai/artifact/PJUNDJ5d2c8R8YHq6qPXtZ | Toca el modelo recién fusionable (PR #6), el PRD (FR-005/FR-006; la captura por foto no tiene FR) y FR-025 (recordatorios usaban la vigencia); merece story propia (reshape) + story de captura foto/OCR tras decidir proveedor IA (NFR-005) | ✅ cerrado el reshape (PR #13 mergeado 2026-10-19: receta+medicinas[], sin vigencia, dx opcional/suelto, archivado; prototipo en product/prototipos/receta-primero.html); la captura foto/OCR sigue pendiente del proveedor IA (story 2) |
| 2026-10-12 | **Prototipo mock como paso del ciclo**: pedido de Saúl Pérez — antes de (o junto con) las specs, generar un frontend solo-mock para que usuarios no programadores validen la idea sin leer delta specs; opciones: artifact clickeable generado por el harness (demostrado hoy), o emitir un prompt para Claude Design / v0 / Stitch | El gate humano del propose hoy exige leer specs; un prototipo navegable detecta expectativas rotas ANTES de ejecutar (hoy costó un ciclo completo) → meta-mejora al harness | ✅ cerrado (improve/harness-0.3.1, 2026-10-20): gate de prototipo desde 0.2.0; desde 0.3.1 el prototipo es HTML local en `product/prototipos/`, sin copia hospedada salvo que se pida |
| 2026-10-20 | **Ronda 2 del dominio: medicina ↔ diagnóstico/crónica.** Saúl Pérez, al validar perfil-cronicas: una receta trae medicinas de varias enfermedades, así que el enlace va **por medicina** (no por receta) hacia un diagnóstico o una crónica propios; elegir/crear la crónica desde la receta ("¿para qué es?"). Respuestas del mismo día: (1) para ligar NO hace falta catálogo (se liga por id, como `diagnosis_id`); (2) crónicas **fuera** del onboarding; (3) enlace por medicina. Preocupación: fatiga por capturar dos veces el tratamiento → la crónica debería mostrar las medicinas ligadas sin recapturarlas | Toca receta (FR-005/FR-006), crónicas (FR-028) y el futuro de la IA; texto libre vs catálogo vs híbrido se decide con la investigación de `docs/investigacion-captura-ux` antes de `/product-discovery` ronda 2 | abierto · investigación hecha (research.md#captura-catalogos); falta la decisión de Saúl Pérez y la ronda 2 |
| 2026-10-20 | **Experiencia "casi como Duolingo"**: mascota que hace el onboarding, explica por qué se pide cada dato y felicita; paleta de colores cómoda para cualquier persona (Saúl Pérez). Objeción anotada del harness: felicitar por "perfil completo" puede presionar a revelar datos sensibles (salud mental, adicciones); alternativa: celebrar hábitos de cuidado, no la completitud | Es identidad de producto (onboarding, design system, tono); merece evidencia (gamificación en salud, WCAG, adultos mayores) antes de diseñar | abierto · investigación hecha (research.md#mascota-color); falta decidir con Saúl Pérez |
| 2026-10-20 | **Expediente de los hijos desde que nacen** (padres que llevan el registro de sus hijos), idea de Saúl Pérez; fuera de alcance por ahora | Cambia el modelo de cuenta (titular ≠ paciente, ya visto en el corpus de recetas: product/dominio.md:21), el consentimiento (menores, tutela, LFPDPPP) y la UX (vacunas, crecimiento) | abierto |

## Closed

| Date | What | Closure |
|---|---|---|
| 2026-10-11 | Traducir es-MX el resto de la UI del template (login, settings, sidebar…) — NFR-012. Decisión de Saúl Pérez (2026-10-12): con **react-i18next**, no traducción directa | ✅ Resuelto por el cambio ui-es-mx-i18next (PR #4, fusionado 2026-10-12): toda la UI, errores del API y correos en es-MX desde recursos i18next; Playwright asierta los textos como contrato. Archivado en openspec/changes/archive/2026-10-12-ui-es-mx-i18next |
| 2026-10-11 | Cobertura backend exactamente en 90% (= umbral del CI) | ✅ Resuelto en el apply de la revisión del PR #1 (tests de google_oauth con httpx mockeado + decrypt_str): 93.69% real, ~3.7 pts de margen. Archivado con cuenta-consentimiento (2026-10-12) |
| 2026-10-11 | Decidir nombre del producto (candidatos: Vitacora, Anamnesis; colisiones de GlobalHealth en research.md#naming) | 💤 Decisión de Saúl Pérez (2026-10-12): se queda GlobalHealth por el momento; re-evaluar ANTES de publicar en tiendas o abrir el repo (ahí la colisión de marca sí muerde). Candidatos siguen en research.md#naming |
| 2026-10-11 | Despersonalizar los artefactos (identidad Google real narrada como dato dev — G20) | ✅ Aplicado a pedido de Saúl Pérez (2026-10-12, PR #3): specs, evidence y journal reescritos a "usuario OAuth real"/"cuenta Google del propietario"; correo literal retirado de evidence. LÍMITE honesto: la historia de git conserva las versiones viejas — una apertura del repo exigiría además squash/reescritura de historia o repo nuevo. La identidad git de los commits (nombre+correo) se mantiene: es metadato de autoría presente en cada commit |
- [2026-10-18] Spike Android / IA en dispositivo (pedido implícito de Saúl Pérez al anunciar su S26 Ultra 1TB/16GB):
  evaluar ML Kit GenAI (Gemini Nano on-device) leyendo recetas del corpus real de 74 fotos como candidato a
  proveedor Q4/NFR-005 — cero retención por construcción, costo cero. Acotado: un spike con criterios medibles
  (¿cuántas recetas impresas/manuscritas extrae bien? ¿límite de tokens de salida alcanza?), NO la app Android
  completa. Entra vía tech-brief cuando se cierre el gate del discovery. Recomendación del harness registrada:
  web primero mientras el modelo de dominio se asienta.
- [2026-10-18] Q1-B diferida (decisión de Saúl Pérez al cerrar Q1 con A): vigencia derivada de la duración del
  tratamiento (inferida por IA, editable) como complemento del archivado manual — retomar cuando el proveedor de
  IA (Q4/tech-brief) esté resuelto.
- [2026-10-18] BYOK para la capa IA (idea de Saúl Pérez): el usuario elige proveedor/API key propia; opción
  "gratis" vía Google AI Studio DESCARTADA para datos reales (términos permiten entrenamiento + revisores humanos;
  memory/research.md 2026-10-18). Diseñar con lista blanca de proveedores/modos compatibles con NFR-005 y análisis
  LFPDPPP. Entra al tech-brief del proveedor junto con el spike on-device (D17).
- [2026-10-18] `scripts/generate-client.sh` y `bun run lint` (biome `--write --unsafe`) reformatean también
  `frontend/tests/`: el implementer del grupo 2 de receta-mexicana tuvo que restaurar el spec del tester con git.
  Candidato: excluir `tests/` del barrido de biome en el script (se suma a la fila existente del blast radius).
  **✅ Cerrado (fix/dev-migraciones-y-cliente, 2026-10-20)** en lo que toca al script: ya no lintea. `bun run lint`
  a mano sigue formateando todo `frontend/` por diseño; un implementer no lo corre a mitad de tarea.
- [2026-10-18] Enlace diagnóstico↔receta + confirmación por correo (idea de Saúl Pérez tras validar receta-mexicana):
  cuando haya proveedor de IA resuelto, permitir enlazar un diagnóstico no confirmado a recetas y, si la receta trae
  los datos del médico, enviarle un correo para que confirme que esa receta corresponde a ese diagnóstico. Extiende
  § Diagnóstico suelto y su confirmación de product/dominio.md; aterriza con E3/E4 (enlaces) + decisión de correo.
- [2026-10-18] Pruebas exploratorias con Claude in Chrome como paso del ciclo (pedido de Saúl Pérez): tras el verde
  de /epe-3-execute, el orquestador navega la app como usuario real E intenta romperla (datos raros, cambios de
  pestaña, doble submit) antes del gate humano. Candidato a regla en epe-3-execute § Final verification del template.
  **✅ Cerrado (improve/harness-0.3.1, 2026-10-20):** paso 2 de la verificación final de epe-3-execute y paso 3 de
  epe-5-apply; primero explora el agente y después valida el humano. Se saltó tras el apply de perfil-eventos por
  vivir solo aquí.
- [2026-10-18] SIGUIENTE TAREA (pedido de Saúl Pérez, prioridad al cerrar receta-mexicana): **onboarding de perfil
  del paciente** justo después de aceptar el consentimiento — fecha de nacimiento, peso actual, estatura, y
  antecedentes médicos familiares ("lo que preguntan mucho los médicos": diabetes o cáncer en la familia…).
  Encaje: rebanada nueva de discovery (catálogo perfil/antecedentes AHF; la evidencia de las 74 fotos ya mostró
  AHF/APP/APNP en la nota IMSS y signos vitales dispersos en recetas) → FR nuevo en el PRD → story con prototipo.
  Dato sensible todo (LFPDPPP art. 3-VI: salud + datos de familiares): cifrado y consentimiento ya resueltos.
  **✅ Resuelto en PR #16 (2026-10-19):** wizard de 3 pasos con datos básicos (fecha, sexo, peso, estatura) + antecedentes familiares (diabetes, cáncer, etc. con parentesco paterno/materno y nota). Perfil completo editable. Todo cifrado, 94% cobertura backend, tests e2e en 384px. Archivado.

- [2026-10-19] Las suites e2e heredadas del template (login, user-settings, admin) NO pasan en viewport móvil
  384×832 (timeouts/elementos no visibles — visto en CI del PR #13 cuando el proyecto s26-ultra corrió sin
  testMatch). El proyecto quedó acotado a health-records.spec.ts; extender la cobertura móvil al resto de la UI
  (y arreglar esas pantallas en 384px) es trabajo propio, probablemente junto con la primera pasada responsive
  general.
- [2026-10-19] El contenedor backend NO corre migraciones Alembic al (re)arrancar: tras crear d5f2a8c41e07 la BD
  dev dio 500 ("relation patient_profile does not exist") hasta un `docker compose exec backend alembic upgrade
  head` manual (visto por el implementer del grupo 2 de onboarding-perfil). Decidir: prestart que migre, o
  documentar el paso en make up. **✅ Cerrado (fix/dev-migraciones-y-cliente, 2026-10-20):** `make up` migra al
  final y `make migrate` lo hace a mano tras crear una migración (corre `scripts/prestart.sh`, idempotente).
- [2026-10-19] sr-only del SidebarTrigger dice "Contraer barra lateral" aunque el sheet móvil esté cerrado: deriva
  del estado `open` de escritorio, no de `openMobile` (frontend/src/components/ui/sidebar.tsx:274-277; hallazgo del
  tester móvil de onboarding-perfil). Quirk de accesibilidad del componente del template.
- [2026-10-19] `formatDateMx` (frontend/src/components/Profile/format.ts) duplica lógica y comentario-razón de
  `Records/RecordDialogs.tsx formatDate` (G20 del review de onboarding-perfil; extraer a un helper compartido
  excedía el scope del apply porque toca Records). Tercera copia en camino si no se extrae.

- [2026-10-20] `validate_birth_date` (backend/app/models.py) compara con `date.today()` del servidor, no con la
  fecha de México: entre las 18:00 y las 24:00 de México el "hoy" del servidor en UTC ya es mañana, y una fecha de
  nacimiento de "mañana" en México pasaría. Mismo tipo de defecto que la tarea 1.0 de perfil-eventos arregló en el
  test de mediciones (visto por el implementer del grupo 1). Candidato: un helper `today_mx()` compartido.
- [2026-10-20] El daemon de Docker Desktop de la máquina de Saúl no logra bajar imágenes base (ghcr.io/astral-sh/uv,
  python:3.14: `DeadlineExceeded` vía el proxy `http.docker.internal:3128`), aunque el host sí llega a ghcr.io. Sin
  rebuild, `make migrate` aplica migraciones que el contenedor no trae. Revisar la configuración de proxy de Docker
  Desktop; mientras tanto, `docker compose cp backend/app backend:/app/backend/` o `docker compose watch`.
- [2026-10-20] Nombres de tabla sin convención: `oauthidentity`, `consentgrant`, `healthrecord`,
  `healthrecordmedicine` y `healthrecordattachment` salen del default de SQLModel (`cls.__name__.lower()`,
  sqlmodel/main.py:907), y desde onboarding-perfil las tablas nuevas declaran `__tablename__` en snake_case
  (`patient_profile`, `medical_history_entry`). Lo detectó Saúl Pérez explorando la BD. Decidir con un ADR:
  renombrar (cambio propio `fix/tablas-snake-case`: `__tablename__` + migración nueva con `op.rename_table`, FKs a
  `healthrecord.id`, índices y constraints, y 4 tests con nombres crudos) o fijar la convención solo para tablas
  nuevas. Editar las migraciones viejas no sirve: no corren otra vez en las BD existentes.
