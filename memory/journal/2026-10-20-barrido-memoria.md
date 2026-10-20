# 2026-10-20 · Barrido de memoria (/epe-memory)

**Quién:** Saúl Pérez (author) pidió `/epe-memory` al cerrar la sesión de perfil-eventos y del harness 0.3.x.

**Compactaciones barridas:** 4 (3 de la sesión del 18–19, 1 de esta). Se releyeron sus transcripts, solo los mensajes
de Saúl. Ya había pedido el 2026-10-19 que no se le confirmara cada paso ("escribe eso en el json de los permisos").
Ese pedido terminó en su `settings.local.json` con una lista `"allow"` fuera de `"permissions"`. Hoy se resolvió en
el harness 0.3.2, con `mcp__claude-in-chrome__*` y `guard-browser.py`.

**Repo:**
- `meta-improvements.md`: 4 filas decían "Proposed" y ya estaban aplicadas en el template desde 0.2.0, verificado
  con `file:line`: product-tech-brief:25, epe-3-execute:57, `make install-hooks` y epe-2-plan:45. Se corrigieron.
- `meta-improvements.md`: se agregó la propuesta de `lint.py` contra PEP 758, que solo vivía en `evidence.md`;
  ahora también está en el inbox del template (earhackerdem/harness#2).
- `inbox.md` y `decisions.md`: sin cambios. El inbox ya se había cerrado en #21 y #23, y ninguna decisión cambió.

**Privada del agente:** 4 corregidas o ampliadas, ninguna borrada y ninguna nueva. Perfil de Saúl: mergea antes de
que se le avise. Proceso: navegador sin confirmar y permisos en `permissions.allow`. Vite y Playwright: la URL base
real. Prek: lo instala `make install-hooks`, y el tropiezo con archivos generados.
