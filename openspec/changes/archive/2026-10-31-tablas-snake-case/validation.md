# Validación — nombres de tabla en snake_case

Para: Saúl Pérez. Unos 3 minutos. En pantalla no cambia nada: cambian los nombres dentro de la base.

**Antes de empezar**, con esta rama, reconstruye la API y aplica la migración:
`docker compose up -d --build --force-recreate --no-deps --wait backend && make migrate`
- [ ] Termina sin errores. Si tu base todavía tenía los nombres viejos, verás
  `Running upgrade 26de7399b12f -> c4a9e1d7b2f5`; en esta Mac ya está migrada (la migró el agente), así que no sale
  esa línea.

## 1 · Las tablas tienen el nombre nuevo y conservan sus datos
1. Copia y pega:
   `docker compose exec -T db psql -U postgres -d app -c "\dt"`
- [ ] Ves `health_record`, `health_record_medicine`, `health_record_attachment`, `consent_grant` y `oauth_identity`.
- [ ] Ya no aparecen `healthrecord`, `consentgrant` ni `oauthidentity`.

## 2 · La app sigue igual
1. En http://localhost:8000 entra con tu cuenta de prueba y abre «Expediente».
- [ ] Ves tus registros, sus medicinas y sus adjuntos como antes.
2. Agrega un diagnóstico y bórralo.
- [ ] Se agrega y se borra sin errores.

## Lo que NO hace
- `user` e `item` se quedan con su nombre (son del template; D25).
- Si alguna vez tienes una base vieja en otro equipo, `make migrate` la pone al día; las migraciones anteriores no
  cambiaron.
