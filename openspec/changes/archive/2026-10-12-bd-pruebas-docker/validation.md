# Validación (no técnica) — bd-pruebas-docker

**Qué cambió, en una frase:** las pruebas automáticas del backend ahora usan su propia base de datos desechable y
ya no pueden tocar —ni borrar— tus datos de desarrollo.

## Por qué importa

Hasta hoy, cada corrida de pruebas borraba los usuarios de la base de desarrollo: tu cuenta de Google y el
consentimiento que otorgaste desaparecían cada vez. De hecho ocurrió una última vez durante este mismo cambio
(tuviste que existir antes de que la protección existiera). A partir de ahora es imposible por construcción.

## Cómo comprobarlo tú mismo (5 minutos)

1. Entra a la app (`http://localhost:5173`), inicia sesión con Google y acepta el consentimiento si te lo pide.
2. En una terminal: `cd ~/projects/personal/sandbox/backend && uv run pytest -q`
   — espera el verde (≈8 s).
3. Recarga la app: **sigues con sesión y tus datos siguen ahí.** Antes de este cambio, este paso te habría
   devuelto a una base vacía.
4. (Opcional) Apaga la base de prueba (`docker compose rm -sf db-test`) e intenta el paso 2: las pruebas se niegan
   a correr con un mensaje claro en español; tus datos nunca estuvieron en riesgo.

## Qué NO cambió

- La app que usas a diario (web, login con Google, consentimiento) se comporta igual.
- Las pruebas de interfaz (Playwright) siguen usando el entorno real, como corresponde.
