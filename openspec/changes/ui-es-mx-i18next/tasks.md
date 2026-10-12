# Tasks

## 1. Infraestructura i18n (single)

- [x] 1.1 `bun add i18next react-i18next` (pin exacto) en frontend; `src/i18n.ts` (es-MX único, recursos estáticos,
      namespaces common/auth/layout/items/admin/settings/consent) importado en `src/main.tsx`
- [x] 1.2 Verificar: build del frontend OK y la app arranca con i18next inicializado (smoke en dev)

## 2. Pantallas + Playwright es-MX (test→impl)

- [x] 2.1 (tester, rojo) Migrar las aserciones de texto de `frontend/tests/*.spec.ts` y `tests/utils/*` a los
      textos es-MX acordados en los recursos (el JSON de claves/textos se fija ANTES, como contrato del grupo)
- [x] 2.2 (commit `test:`) rojo verificado por el orquestador (suite Playwright roja contra la UI inglesa)
- [x] 2.3 (implementer, verde) Extraer y traducir todos los strings visibles de `src/routes` y `src/components`
      (sin `components/ui/` ni `client/`) a los recursos; ConsentGate y login Google se mueven byte a byte
- [x] 2.4 Suite Playwright completa verde; grep de remanentes en inglés limpio (documentado)

## 3. Backend details + correos es-MX (test→impl)

- [x] 3.1 (tester, rojo) Aserciones es-MX en `backend/tests` para los `detail` visibles (login/users/items/utils) y
      en `reset-password.spec.ts`/utils de Mailpit para asunto+cuerpo es-MX
- [x] 3.2 (commit `test:`) rojo verificado
- [x] 3.3 (implementer, verde) Traducir details visibles, asuntos en `app/utils.py` y plantillas React Email;
      regenerar `backend/app/email-templates/*.html`
- [x] 3.4 pytest 0/0/0 con cobertura ≥90 y Playwright completo verde

## 4. Cierre (single)

- [x] 4.1 ADR D15 (react-i18next, es-MX único, namespaces; backend sin biblioteca i18n) en `memory/decisions.md`
- [x] 4.2 `evidence.md` (números rojo/verde por grupo, grep de remanentes, nota del texto de consentimiento
      intacto), `validation.md` no técnico, journal
- [x] 4.3 PR abierto; fila es-MX del inbox: diferida a post-merge (ediciones en vuelo del PR #3; ver evidence
      §Deuda)
