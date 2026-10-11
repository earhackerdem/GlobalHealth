# Validation — cuenta-consentimiento (guion no técnico)

Para: Saúl Pérez. Qué puedes probar tú mismo en 5 minutos para dar el visto bueno.

## Preparación (una vez)
1. En una terminal: `docker compose up -d db mailpit`
2. En otra: `cd backend && uv run bash scripts/prestart.sh && uv run fastapi dev`
3. En otra: `bun run dev` (frontend en http://localhost:5173)

## Qué validar
1. **Alta con correo**: entra a http://localhost:5173/signup, crea una cuenta con un correo inventado.
   ✔ Esperado: entras al dashboard y aparece una tarjeta en español pidiendo tu consentimiento para tratar
   datos de salud, con el texto completo visible (marcado como versión v1, placeholder legal).
2. **El bloqueo es real**: antes de aceptar, cualquier intento de guardar un dato de salud por la API responde
   403 "CONSENT_REQUIRED" (los tests lo prueban; si quieres verlo, desde http://localhost:8000/docs autentícate
   y prueba POST /api/v1/health-records).
3. **Aceptar consentimiento**: pulsa "Acepto el tratamiento de mis datos sensibles".
   ✔ Esperado: la tarjeta desaparece y no vuelve a aparecer al recargar; en /docs, GET /api/v1/consent te dice
   la versión y la fecha exacta en que lo otorgaste.
4. **Nadie ve lo tuyo**: crea una segunda cuenta en otra ventana de incógnito y acepta su consentimiento.
   ✔ Esperado: cada cuenta solo lista sus propios registros (GET /api/v1/health-records); pedir por id un
   registro de la otra cuenta responde "no encontrado", sin revelar que existe.
5. **Botón de Google**: el backend ya tiene el flujo completo (con PKCE), pero probarlo de verdad requiere
   credenciales de Google Cloud (ver "Qué falta de ti").

## Qué falta de ti
- **Credenciales de Google** para la prueba real: en Google Cloud Console crea un OAuth Client (tipo Web),
  redirect URI `http://localhost:8000/api/v1/login/google/callback`, y pásame CLIENT_ID y CLIENT_SECRET
  (van al .env local, no se commitean).
- **Remoto git**: no hay remoto configurado; cuando exista, abro el PR y el CI corre solo.
- Recuerda: el texto del consentimiento es un borrador (v1-placeholder). Antes de que lo use alguien que no
  seas tú, revisión legal (quedó en el presupuesto NFR).
