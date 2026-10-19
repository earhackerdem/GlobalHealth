# Validación — onboarding de perfil (para Saúl Pérez)

Guion no técnico. Necesitas la app corriendo (`make up` y `make front`) y una cuenta NUEVA (el onboarding solo se
ofrece una vez por cuenta; si usas una vieja, la verás una única vez al entrar a la home).

## Camino 1 — Completar el onboarding

1. Crea una cuenta nueva y acepta el consentimiento.
   - [ ] Inmediatamente después de aceptar aparece "Datos básicos — Paso 1 de 3".
2. Pon tu fecha de nacimiento, sexo, peso y estatura; Continuar.
   - [ ] Al llegar al resumen, la fecha se ve dd/mm/aaaa y nada te obligó a llenar todo.
3. En "Antecedentes familiares" marca Diabetes: aparecen los parentescos.
   - [ ] Puedes distinguir "Abuelo paterno" de "Abuelo materno" (lo que pediste) y añadir un detalle
         (p. ej. "diagnosticado a los 50"). Anota también una alergia.
4. Continuar → Resumen → "Guardar perfil".
   - [ ] Aterrizas en tu Expediente con el aviso "Perfil guardado".
5. Entra a "Mi perfil médico" (menú lateral).
   - [ ] Están tus datos, el peso con la fecha de hoy, tu antecedente con parentesco y detalle, y
         6 secciones más ("Fracturas y lesiones", "Hábitos"…) marcadas "Sin registros".
6. Vuelve al Panel / recarga / cierra sesión y entra de nuevo.
   - [ ] El onboarding NO se vuelve a ofrecer.

## Camino 2 — Omitirlo todo

1. Con otra cuenta nueva, acepta el consentimiento y pulsa "Ahora no, llévame a mi expediente".
   - [ ] Entras directo al expediente sin llenar nada, y al volver a iniciar sesión nadie te lo vuelve a pedir.
2. Abre "Mi perfil médico".
   - [ ] Todo dice "Sin registrar" y puedes completarlo desde ahí con "Editar datos básicos".

## Camino 3 — Editar después

1. En "Mi perfil médico" → "Editar datos básicos", agrega o corrige tu fecha de nacimiento.
   - [ ] Se guarda y se muestra con tu edad calculada.
2. Registra un peso nuevo otro día (o cambia el valor hoy).
   - [ ] El perfil muestra el más reciente con su fecha; el anterior no se pierde (quedó como historial).
3. En la sección "Antecedentes familiares" → "Editar antecedentes" (tu feedback del 2026-10-19).
   - [ ] Puedes agregar o quitar condiciones y parentescos aunque hayas omitido todo el onboarding.
4. En el wizard, llega hasta el Resumen.
   - [ ] Ya NO hay botón de omitir ahí: solo guardar o volver (tu feedback del 2026-10-19).

## Qué NO hace todavía

- Las 6 secciones adicionales (crónicas, hepatitis/pasadas, cirugías, fracturas, transfusiones, hábitos) se VEN
  pero aún no se capturan: ese llenado es la siguiente historia (FR-028/US-18).
- Si escribes una fecha de nacimiento futura, el sistema la rechaza y te lo dice en español (tras el review
  adversarial, además del aviso ahora hay mensaje junto al campo).
- La pantalla de inicio ("Panel") ya no es el aterrizaje: con consentimiento dado, entrar te lleva al expediente.
- Nada de esto se comparte aún con médicos (eso llega con los enlaces, E3/E4) ni alimenta avisos de la IA (E5).
