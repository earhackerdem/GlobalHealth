# Evidence — ui-es-mx-i18next

Fecha: 2026-10-12 · Rama: feat/ui-es-mx-i18next · Ejecutor: Claude (orquestador) + subagentes
autor-de-recursos/tester/implementer por grupo. Comandos: `cd backend && uv run coverage run -m pytest -q` ·
`cd frontend && PLAYWRIGHT_BASE_URL=http://localhost:8000 bunx playwright test --project=chromium`.

## Números por grupo (rojo → verde, re-ejecutados por el orquestador antes de cada commit)

| Grupo | Rojo (commit `test:`) | Verde |
|---|---|---|
| 1 Infra i18n (single) | n/a | build del frontend OK con i18n.ts + 203 claves en 7 namespaces (8fdb244) |
| 2 Pantallas + Playwright (test→impl) | 1 failed (auth.setup "Iniciar sesión" vs UI inglesa) + 61 bloqueados por la dependencia del setup (8c5666a) | **Playwright 62 passed / 0 failed** (5a8a4c9) |
| 3 Backend + correos (test→impl) | backend **28 failed / 76 passed** + Playwright **6 failed / 56 passed** (6d278ad) | backend **104 passed / 0 failed / 0 errors / 0 skipped** · cobertura **93.69%** · Playwright **62 passed** (7cec812) |

- `make tdd-check` ✓ (3 commits `test:` al momento de la revisión: 2 rojos —uno por grupo test→impl— + 1 de
  formato biome sin tocar aserciones; el apply añade 1 más. Rutas de tests sin diff tras el último).
- El rojo del grupo 2 es estructural: el `[setup]` de Playwright bloquea los 61 tests dependientes; el rojo del
  grupo 3 detalla 28+6 aserciones exactas contra el backend aún en inglés.

## Contratos del cambio

- Frontend: `frontend/src/locales/es-MX/*.json` (203 claves) + `mapping-es-mx.md` (archivo→clave→inglés→es-MX).
- Backend/correos: `backend-details-es-mx.md`. El tester encontró un hueco real (los `message=` de éxito no
  estaban en el contrato); se extendió el contrato ANTES de migrar las aserciones, no al revés.
- `CONSENT_REQUIRED` intacto (código de máquina que intercepta ConsentGate). Texto legal del consentimiento: solo
  movido a recursos, byte a byte — los tests de consent y el sha256 en BD no cambiaron.

## Escenario: cero strings de interfaz hardcodeados (grep documentado)

```
$ cd frontend/src && grep -rnE --exclude-dir=ui --exclude-dir=client '>[A-Z][a-z]+ [a-z]+|"[A-Z][a-z]+ [a-z]+ [a-z]+' routes components hooks utils.ts | grep -vE 't\(|i18nKey|className|^[^:]+:[0-9]+:\s*(//|\*|\{?/\*)'
hooks/useCopyToClipboard.ts:13:      console.warn("Clipboard not supported")
```

Único hit: un `console.warn` no visible al usuario. Strings visibles en inglés en los componentes de dominio: 0.

## Escenario: correo de recuperación es-MX end-to-end

`reset-password.spec.ts` (2 flujos) lee el correo REAL desde Mailpit: asunto
"{project_name} - Recuperación de contraseña para {email}", cuerpo con botón "Restablecer contraseña", enlace
funcional hasta cambiar la contraseña. Plantillas regeneradas con `bun run export` (react-email →
backend/app/email-templates/*.html), placeholders `{{ link }}/{{ project_name }}/{{ username }}/{{ valid_hours }}`
verificados en el HTML generado.

## Deuda anotada (fuera del alcance)

- `routes/utils.py:26` `message="Test email sent"` (endpoint de utilidad, sin test que lo asierte, no en contrato).
- DataTable: la paginación perdió el `<span class="font-medium">` en los totales (el recurso es string plano);
  cosmético.
- `playwright.config.ts` default baseURL apunta a :5173 (dev server); la suite corre con
  `PLAYWRIGHT_BASE_URL=http://localhost:8000` explícito contra el build servido por el backend (así corre en CI).
- El hook lint.py (python del sistema) sigue dando falso positivo PEP 758 en deps.py al editarlo — ya en
  meta-improvements/closed.md.
- La fila es-MX del inbox se cierra tras el merge (el inbox tiene ediciones en vuelo en el PR #3; cerrarla aquí
  fabricaría un conflicto).

## Ronda /epe-4-review → /epe-5-apply (2026-10-12)

Saúl Pérez aprobó: grupo A completo (pins 26.4.2/17.0.15 por la regla ≥2 semanas, lang es-MX en index.html y
correos, pytest del detail, carve-out al spec, bajas de una línea), y de B: tests de pantallas de error/títulos
AHORA, test del correo de alta, fallbacks de toast traducidos, sr-only de ui/ traducidos; de C: aserción del toast
de recover. Diferidos a closed.md: placeholders .first() (heredado) y typos por ruta.
Fixer 14/14 sin rebotes + tester con 4 archivos de cobertura (verdes al primer intento: cubren comportamiento ya
embarcado). Números post-apply: backend **106 passed / 0 failed / 0 errors / 0 skipped** · cobertura **93.69%** ·
Playwright **65 passed** (62 + errors.spec.ts ×3). Total commits `test:` de la rama tras el apply: 4.
