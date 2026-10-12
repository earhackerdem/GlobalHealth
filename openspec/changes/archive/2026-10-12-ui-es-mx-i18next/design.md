# Design

Status: APPROVED
Approved by: Saúl Pérez (author) on 2026-10-12 ("plan approved")

## Context

- Frontend: React 18 + TanStack Router (template full-stack FastAPI), strings en inglés hardcodeados en 12 rutas y
  ~20 componentes con texto; las pantallas de E1 (ConsentGate, botón Google) ya están en es-MX hardcodeado.
- Playwright: 7 specs + utils con **177 aserciones de texto** en inglés (`getByText/getByRole name:/getByLabel/
  getByPlaceholder`) — son el contrato efectivo del idioma.
- Acople transversal verificado: `login.spec.ts:69` asierte `"Incorrect email or password"`, que nace en
  `backend/app/api/routes/login.py:49`; los asuntos de correo nacen en `backend/app/utils.py` y las plantillas en
  `packages/react-email/emails/*` (el build de emails genera `backend/app/email-templates/*.html`).
- Decisión de Saúl Pérez (2026-10-12): react-i18next; sin selector de idioma (no está en el PRD).

## Goals / Non-Goals

**Goals:** NFR-012 completo (pantallas + toasts con errores del API + correos) con recursos de traducción;
Playwright como contrato es-MX; infraestructura lista para un segundo idioma (con selector + recarga; el cambio
en caliente requiere refactor puntual de los `i18n.t` de module scope).
**Non-Goals:** selector de idioma y detección de locale del navegador; segundo locale; traducir logs del servidor,
OpenAPI/docs, Adminer; i18n del backend con biblioteca (los details se traducen como strings es-MX directos:
un solo locale embarcado no justifica gettext/babel); renombrar claves de la API o códigos de error.

## Interface contract

- **Paquetes**: `i18next@26.4.2` + `react-i18next@17.0.15` (pin exacto; la regla del design exige versiones con
  ≥ 2 semanas de vigencia, por eso no se toma la última publicada).
- **`frontend/src/i18n.ts`**: inicializa i18next con `lng: "es-MX"`, `fallbackLng: "es-MX"`,
  `interpolation.escapeValue: false`, recursos importados estáticamente (sin backend HTTP de traducciones).
  Importado por efecto en `frontend/src/main.tsx` antes del render.
- **Recursos**: `frontend/src/locales/es-MX/<ns>.json` con namespaces `common` (botones, acciones, validaciones
  compartidas), `auth` (login/signup/recover/reset), `layout` (sidebar, user menu, footer), `items`, `admin`,
  `settings`, `consent` (migra los textos ya escritos, sin cambiarlos). Claves kebab/camel descriptivas, no el
  texto inglés como clave.
- **Componentes (patrón dual)**: en componentes, `const { t } = useTranslation("<ns>")`; textos visibles →
  `t("clave")`. Para strings de module scope (schemas zod, arrays de columnas) y para las primitivas de
  `components/ui/`, `import i18n from "@/i18n"` + `i18n.t("ns:clave")`. Nota: un cambio de idioma en caliente
  exigiría mover los `i18n.t` de module scope a render-time. Los textos es-MX ya existentes (ConsentGate, login
  Google) se MUEVEN a recursos sin cambiar su redacción (citers: tests de consent).
- **Fallbacks es-MX de `utils.ts`**: el toast de error nunca muestra inglés: la ruta 422 (lista de errores de
  Pydantic) cae a `common:errors.validation` y la ruta `err.message` de Axios a `common:errors.generic`; los
  `detail` string del backend (ya es-MX) pasan tal cual.
- **Backend details es-MX** (solo los que ve el usuario): los `HTTPException(detail=…)` de `routes/login.py`,
  `routes/users.py`, `routes/items.py`, `routes/utils.py` y los asuntos/plantillas de `app/utils.py`; los tests
  backend que los asiertan se actualizan en el mismo grupo. Los nombres de claves/códigos HTTP no cambian.
- **Emails**: `packages/react-email/emails/{new_account,reset_password,test_email}.tsx` a es-MX; se regenera
  `backend/app/email-templates/*.html` con el build del workspace; asuntos en `app/utils.py` a es-MX. El año del
  footer no se congela en build: la plantilla emite el literal `{{ year }}` y los tres `generate_*` de
  `app/utils.py` añaden `year` al contexto Jinja.
- **Playwright**: aserciones de texto migradas a los textos es-MX exactos de los recursos; `tests/utils/*` que
  busca correos por asunto usa los asuntos nuevos.
- **Guard de no-regresión del idioma**: el gate del cambio incluye una búsqueda documentada (grep en evidence.md)
  de strings visibles en inglés remanentes en `frontend/src/routes` y `frontend/src/components` (excluyendo
  `components/ui/` del design system, atributos no visibles y el código generado `src/client/`). Carve-out de
  `components/ui/` acotado: queda fuera del barrido general, pero su texto de accesibilidad (sr-only, aria,
  SheetTitle/Description del sidebar móvil) sí se traduce vía `i18n.t`.

## Decisions

- **react-i18next con es-MX único**: pedido explícito; la alternativa barata (traducción directa) se descartó por
  decisión de Saúl Pérez 2026-10-12 (quedó asentada en el inbox). → ADR D15 en este cambio.
- **Namespaces por dominio** y no un JSON único: los recursos siguen la estructura de pantallas; un archivo de
  ~250 claves se vuelve inmanejable y los namespaces permiten carga por pantalla si algún día pesa.
- **Backend sin biblioteca i18n**: con un solo locale, `detail="Correo o contraseña incorrectos"` directo; una
  biblioteca (babel/gettext) pagaría infraestructura para cero variación. Si entra un segundo idioma, se revisa.
- **Los tests E2E son el contrato del idioma**: el rojo del grupo 2 es Playwright asertando es-MX contra la UI
  inglesa; no hay "test de i18n" sintético aparte.
- **`components/ui/` (shadcn) fuera del barrido**: son primitivas del design system casi sin texto propio; lo que
  muestren viene por props desde los componentes de dominio, que sí se traducen. Excepción (decisión del dueño):
  su texto accesible propio (sr-only/aria del dialog y el sidebar) usa recursos es-MX con `i18n.t`.

## Test plan (one row per scenario, mandatory)

| Spec · scenario | Test |
|---|---|
| localization · Las pantallas del template quedan en es-MX | suite Playwright completa (7 specs, 177 aserciones migradas a es-MX): roja contra la UI en inglés, verde tras traducir; números en evidence.md |
| localization · Cero strings de interfaz hardcodeados | revisión del diff + grep documentado en evidence.md (frontend/src/{routes,components} sin `components/ui/` ni `client/`): 0 strings visibles en inglés |
| localization · Credenciales incorrectas en es-MX | `login.spec.ts` asierte el toast es-MX end-to-end + `backend/tests/api/routes/test_login.py` asierte el `detail` es-MX |
| localization · Recuperación de contraseña en es-MX | `reset-password.spec.ts` lee el correo de Mailpit con asunto es-MX y completa el flujo |

## Non-functional constraints addressed

- **NFR-012 (UI es-MX)**: es el objetivo del cambio; el gate lo mide con la suite E2E completa + grep.
- **NFR-010 (operable por una persona)**: sin servicios nuevos; recursos estáticos en el bundle.
- **NFR-001/004**: sin impacto (no se tocan cifrado ni consentimiento; los textos de consentimiento SOLO se mueven
  de sitio sin cambiar redacción — su sha256 de evidencia vive en la BD, no en el frontend).

## Risks / Trade-offs

- [177 aserciones migradas a mano pueden divergir de los recursos] → las aserciones copian el texto exacto del
  JSON; cualquier divergencia sale roja en el propio Playwright.
- [El bundle crece por los JSON] → un locale estático son pocos KB; sin backend HTTP de traducciones.
- [Cambiar los `detail` del backend rompe consumidores que los parseen] → el único consumidor es este frontend
  (toasts muestran el string tal cual); el contrato de códigos HTTP no cambia.
- [El texto legal del consentimiento podría "corregirse" al moverlo] → regla explícita: se mueve byte a byte; el
  test de idempotencia de consent y el sha256 en BD no cambian.

## Gate that closes the work

`bunx playwright test --project=chromium` verde completo (≈62 tests con aserciones es-MX) + `cd backend && uv run
pytest -q` verde (0/0/0, cobertura ≥90) + grep de remanentes en inglés documentado en evidence.md + `make
tdd-check` + CI del PR verde.

## Execution per task group

| Grupo | Flavor | Por qué |
|---|---|---|
| 1 Infra i18n (paquetes, i18n.ts, namespaces vacíos, main.tsx) | single | plumbing declarativo; lo verifica el build y el grupo 2 |
| 2 Pantallas + Playwright es-MX | test→impl | rojo = specs Playwright migrados a es-MX contra UI inglesa; verde = extracción+traducción hasta suite completa |
| 3 Backend details + correos (pytest + flujo de reset) | test→impl | rojo = aserciones es-MX en pytest/reset-password.spec; verde = details/asuntos/plantillas traducidos |
| 4 Evidencia, ADR D15, grep de remanentes, validation, PR | single | cierre documental |
