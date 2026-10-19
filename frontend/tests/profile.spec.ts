import { expect, type Locator, type Page, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import { randomEmail, randomPassword } from "./utils/random"
import { logInUser, logOutUser } from "./utils/user"

test.use({ storageState: { cookies: [], origins: [] } })

// --- Contrato de UI que este spec fija (el implementer lo lee de aquí) -------
//
// data-testid nuevos:
//   onboarding-wizard          contenedor del wizard de onboarding (home)
//   profile-basic-data         sección "Datos básicos" en /perfil
//   profile-family-history     sección de antecedentes familiares en /perfil
//   profile-pending-sections   contenedor de las 6 secciones aún sin captura
// data-testid reutilizados (ya existen): consent-accept-button, email-input,
//   password-input, user-menu.
//
// Textos es-MX asertados como contrato:
//   Wizard: encabezados "Datos básicos", "Antecedentes familiares", "Resumen";
//     botón por paso "Omitir este paso"; botón global
//     "Ahora no, llévame a mi expediente" visible en los pasos 1 y 2 pero NO
//     en el Resumen (feedback de Saúl Pérez, 2026-10-19: con todo capturado,
//     un botón de omitir confunde); avanzar "Continuar"; cierre
//     "Guardar perfil".
//   Paso 2: checkboxes de condición "Diabetes", "Cáncer", "Hipertensión",
//     "Enfermedad del corazón", "Otra condición"; al marcar una condición
//     aparecen sus parentescos como checkboxes "Madre", "Padre",
//     "Abuela materna", "Abuelo materno", "Abuela paterna", "Abuelo paterno",
//     "Hermana/o", "Otro".
//   /perfil: heading "Mi perfil médico" y entrada de navegación con ese mismo
//     texto; campo básico vacío muestra "Sin registrar"; editar básicos:
//     botón "Editar datos básicos", campo con label "Fecha de nacimiento"
//     (input de fecha rellenable con ISO aaaa-mm-dd), guardar con botón
//     "Guardar"; fecha mostrada en es-MX dd/mm/aaaa y edad derivada "N años".
//   Sexo (wizard paso 1 y "Editar datos básicos", hallazgo G9): Select de
//     Radix (role combobox con label "Sexo"), opciones "Mujer", "Hombre",
//     "Prefiero no decir"; se elige con clic al trigger + clic a la opción.
//   Registrar medición en /perfil (hallazgo G1): botón
//     data-testid="add-measurement" abre el diálogo
//     data-testid="measurement-dialog" "Registrar medición" (label
//     "Tipo de medición", opciones "Peso (kg)" / "Estatura (cm)"; el campo de
//     valor lleva el label de la unidad), guardar "Guardar", toast
//     "Medición registrada"; valor fuera de rango → error inline
//     "El peso debe estar entre 0.1 y 400 kg" y NO guarda.
//   Resumen del wizard: con fecha capturada muestra "dd/mm/aaaa (N años)"
//     con la edad derivada a la fecha actual (hallazgos M31c + M29).
//   Editar antecedentes desde /perfil (feedback): en la sección de
//     antecedentes, botón "Editar antecedentes" que abre el MISMO editor de
//     condiciones/parentescos del wizard (checkboxes "Diabetes", "Madre", …);
//     guardar con botón "Guardar" (exact) cierra el editor y deja el
//     antecedente visible en la sección.
//   Secciones sin captura (6, con estado vacío "Sin registros" cada una):
//     "Enfermedades crónicas", "Enfermedades pasadas e infecciosas",
//     "Cirugías y hospitalizaciones", "Fracturas y lesiones",
//     "Transfusiones y grupo sanguíneo", "Hábitos".
// ---------------------------------------------------------------------------

const PENDING_SECTIONS = [
  "Enfermedades crónicas",
  "Enfermedades pasadas e infecciosas",
  "Cirugías y hospitalizaciones",
  "Fracturas y lesiones",
  "Transfusiones y grupo sanguíneo",
  "Hábitos",
] as const

/** Edad cumplida a la fecha `on` para quien nació en `birth`. */
function ageOn(birth: Date, on: Date): number {
  let age = on.getFullYear() - birth.getFullYear()
  const beforeBirthday =
    on.getMonth() < birth.getMonth() ||
    (on.getMonth() === birth.getMonth() && on.getDate() < birth.getDate())
  if (beforeBirthday) age -= 1
  return age
}

/** Hoy en dd/mm/aaaa (es-MX), con la fecha LOCAL (no UTC). */
function todayMx(): string {
  const now = new Date()
  const day = String(now.getDate()).padStart(2, "0")
  const month = String(now.getMonth() + 1).padStart(2, "0")
  return `${day}/${month}/${now.getFullYear()}`
}

/**
 * Cuenta nueva: alta por API privada, login por UI y aceptar el consentimiento
 * en la home. Devuelve las credenciales para poder reiniciar sesión.
 */
async function freshUserWithConsent(page: Page) {
  const email = randomEmail()
  const password = randomPassword()
  await createUser({ email, password })
  await logInUser(page, email, password)

  const consentButton = page.getByTestId("consent-accept-button")
  await expect(consentButton).toBeVisible()
  await consentButton.click()
  await expect(consentButton).not.toBeVisible()

  return { email, password }
}

/**
 * Inicia sesión SIN asumir en qué pantalla aterriza (con el onboarding cerrado
 * el contrato manda directo al expediente, no a la home con saludo).
 */
async function logInExpectingExpediente(
  page: Page,
  email: string,
  password: string,
) {
  await page.goto("/login")
  await page.getByTestId("email-input").fill(email)
  await page.getByTestId("password-input").fill(password)
  await page.getByRole("button", { name: "Iniciar sesión" }).click()
  await page.waitForURL(/\/expediente/)
}

/**
 * En viewport móvil (s26-ultra, 384×832) la navegación y el menú de usuario
 * viven detrás del trigger del sidebar (sr-only de SidebarTrigger: "Abrir
 * barra lateral" / "Contraer barra lateral"; en móvil el texto sigue el
 * estado de ESCRITORIO, quirk preexistente del componente, de ahí el regex).
 * Abre el menú SOLO si el objetivo no está ya visible; en escritorio no toca
 * nada. Ninguna aserción se debilita: el objetivo debe quedar visible.
 */
async function revealInSidebar(page: Page, target: Locator) {
  if (await target.isVisible().catch(() => false)) return
  await page.getByRole("button", { name: /barra lateral/ }).click()
  await expect(target).toBeVisible()
}

/**
 * Cierra sesión siendo robusto al viewport: en móvil abre primero el sidebar
 * para que el user-menu exista; luego delega en logOutUser (utils/user.ts),
 * que otras suites usan tal cual y no se toca.
 */
async function logOutRobust(page: Page) {
  await revealInSidebar(page, page.getByTestId("user-menu"))
  await logOutUser(page)
}

/** Cierra el onboarding con el "Ahora no" global y aterriza en el expediente. */
async function skipOnboardingToExpediente(page: Page) {
  const wizard = page.getByTestId("onboarding-wizard")
  await expect(wizard).toBeVisible()
  await page
    .getByRole("button", { name: "Ahora no, llévame a mi expediente" })
    .click()
  await page.waitForURL(/\/expediente/)
  await expect(wizard).not.toBeVisible()
}

test.describe("Perfil médico — onboarding y /perfil", () => {
  test("Escenario 8: 'Ahora no' lleva al expediente y el onboarding no se repite al reiniciar sesión", async ({
    page,
  }) => {
    const { email, password } = await freshUserWithConsent(page)

    // Tras aceptar el consentimiento la home ofrece el onboarding.
    const wizard = page.getByTestId("onboarding-wizard")
    await expect(wizard).toBeVisible()

    // "Ahora no" aterriza en el expediente sin llenar nada.
    await skipOnboardingToExpediente(page)
    await expect(
      page.getByRole("button", { name: "Registrar receta" }),
    ).toBeVisible()

    // Cerrar sesión y volver a entrar: el onboarding NO se vuelve a ofrecer
    // (el cierre vive en el servidor) y se ve el expediente directo.
    await logOutRobust(page)
    await logInExpectingExpediente(page, email, password)
    await expect(
      page.getByRole("button", { name: "Registrar receta" }),
    ).toBeVisible()
    await expect(page.getByTestId("onboarding-wizard")).not.toBeVisible()
    await expect(page.getByTestId("consent-accept-button")).not.toBeVisible()
  })

  test("Escenario 10: omitir datos básicos, guardar solo Diabetes/Madre y completar la fecha y el sexo desde /perfil", async ({
    page,
  }) => {
    const { email, password } = await freshUserWithConsent(page)

    const wizard = page.getByTestId("onboarding-wizard")
    await expect(wizard).toBeVisible()
    const ahoraNo = page.getByRole("button", {
      name: "Ahora no, llévame a mi expediente",
    })

    // Paso 1 (datos básicos): conserva el "Ahora no" global; se omite entero.
    await expect(wizard.getByText("Datos básicos")).toBeVisible()
    await expect(ahoraNo).toBeVisible()
    await wizard.getByRole("button", { name: "Omitir este paso" }).click()

    // Paso 2 (antecedentes familiares): conserva el "Ahora no" global; marcar
    // Diabetes muestra los parentescos; se elige Madre.
    await expect(wizard.getByText("Antecedentes familiares")).toBeVisible()
    await expect(ahoraNo).toBeVisible()
    const madre = wizard.getByRole("checkbox", { name: "Madre", exact: true })
    await expect(madre).not.toBeVisible()
    await wizard.getByRole("checkbox", { name: "Diabetes" }).check()
    await madre.check()

    // Paso 3 (resumen): refleja lo capturado y guarda. El "Ahora no" global
    // NO está en el Resumen (feedback de Saúl Pérez: con todo ya capturado,
    // un botón de omitir confunde).
    await wizard.getByRole("button", { name: "Continuar" }).click()
    await expect(wizard.getByText("Resumen")).toBeVisible()
    await expect(ahoraNo).not.toBeVisible()
    await expect(wizard.getByText("Diabetes")).toBeVisible()
    await expect(wizard.getByText("Madre")).toBeVisible()
    await wizard.getByRole("button", { name: "Guardar perfil" }).click()
    await expect(wizard).not.toBeVisible()

    // En /perfil: el antecedente está, los básicos siguen vacíos.
    await page.goto("/perfil")
    await expect(
      page.getByRole("heading", { name: "Mi perfil médico" }),
    ).toBeVisible()
    const ahf = page.getByTestId("profile-family-history")
    await expect(ahf.getByText("Diabetes")).toBeVisible()
    await expect(ahf.getByText("Madre")).toBeVisible()
    const basics = page.getByTestId("profile-basic-data")
    await expect(basics.getByText("Sin registrar").first()).toBeVisible()

    // Desde /perfil se completan la fecha de nacimiento (15/03/1990) y el
    // sexo. El sexo es un Select de Radix (hallazgo G9): clic al combobox
    // "Sexo" y clic a la opción "Mujer".
    await basics.getByRole("button", { name: "Editar datos básicos" }).click()
    await page.getByLabel("Fecha de nacimiento").fill("1990-03-15")
    await page.getByRole("combobox", { name: "Sexo" }).click()
    await page.getByRole("option", { name: "Mujer" }).click()
    await page.getByRole("button", { name: "Guardar", exact: true }).click()

    // La fecha se muestra en es-MX con la edad derivada a la fecha actual, y
    // el sexo con el texto del spec ("Mujer", no "Femenino").
    await expect(basics.getByText("15/03/1990")).toBeVisible()
    const expectedAge = ageOn(new Date(1990, 2, 15), new Date())
    await expect(basics.getByText(`${expectedAge} años`)).toBeVisible()
    await expect(basics.getByText("Mujer")).toBeVisible()

    // (M31a) Con el onboarding COMPLETADO: cerrar sesión y volver a entrar no
    // re-ofrece el wizard y los datos capturados siguen en /perfil.
    await logOutRobust(page)
    await logInExpectingExpediente(page, email, password)
    await expect(page.getByTestId("onboarding-wizard")).not.toBeVisible()
    await page.goto("/perfil")
    const basicsAfter = page.getByTestId("profile-basic-data")
    await expect(basicsAfter.getByText("15/03/1990")).toBeVisible()
    await expect(basicsAfter.getByText("Mujer")).toBeVisible()
    const ahfAfter = page.getByTestId("profile-family-history")
    await expect(ahfAfter.getByText("Diabetes")).toBeVisible()
    await expect(ahfAfter.getByText("Madre")).toBeVisible()
  })

  test("Escenario 11: /perfil lista las 6 secciones adicionales vacías y ninguna ofrece formulario de captura", async ({
    page,
  }) => {
    // Nota (M29): el GIVEN del escenario 11 del spec pide "un antecedente
    // registrado"; aquí la cuenta omite el onboarding porque lo que se asierta
    // (las 6 secciones pendientes, sin captura) no depende de él. La
    // visibilidad de /perfil CON antecedentes registrados la cubren los
    // escenarios 10, 13 y el de dos antecedentes (G3/M30).
    // Cuenta con el onboarding ya cerrado (omitido).
    await freshUserWithConsent(page)
    await skipOnboardingToExpediente(page)

    // La navegación tiene la entrada "Mi perfil médico" y lleva a /perfil
    // (en móvil, tras abrir el menú colapsado).
    const perfilLink = page.getByRole("link", { name: "Mi perfil médico" })
    await revealInSidebar(page, perfilLink)
    await perfilLink.click()
    await page.waitForURL(/\/perfil/)
    await expect(
      page.getByRole("heading", { name: "Mi perfil médico" }),
    ).toBeVisible()

    const sections = page.getByTestId("profile-pending-sections")
    await expect(sections).toBeVisible()

    // Las seis secciones listadas, cada una como vacía.
    for (const name of PENDING_SECTIONS) {
      await expect(sections.getByText(name)).toBeVisible()
    }
    await expect(sections.getByText("Sin registros")).toHaveCount(6)

    // Sin captura: ni inputs ni botón de guardar dentro de las secciones.
    await expect(sections.locator("input, textarea, select")).toHaveCount(0)
    await expect(sections.getByRole("button", { name: /Guardar/ })).toHaveCount(
      0,
    )

    // (M27) Tampoco hay botones "Añadir"/"Agregar": el contrato es de solo
    // lectura, así que la aserción es directa (el bucle condicional anterior
    // no ejecutaba ninguna aserción al no existir botones).
    await expect(
      sections.getByRole("button", { name: /Añadir|Agregar/ }),
    ).toHaveCount(0)
  })

  test("Escenario 13 (feedback): agregar antecedentes desde /perfil tras omitir todo el onboarding", async ({
    page,
  }) => {
    // Cuenta que omitió TODO el onboarding ("Ahora no").
    await freshUserWithConsent(page)
    await skipOnboardingToExpediente(page)

    await page.goto("/perfil")
    await expect(
      page.getByRole("heading", { name: "Mi perfil médico" }),
    ).toBeVisible()

    // La sección de antecedentes ofrece "Editar antecedentes": el mismo
    // editor de condiciones/parentescos del wizard.
    const ahf = page.getByTestId("profile-family-history")
    await ahf.getByRole("button", { name: "Editar antecedentes" }).click()

    const diabetes = page.getByRole("checkbox", { name: "Diabetes" })
    await expect(diabetes).toBeVisible()
    await diabetes.check()
    await page.getByRole("checkbox", { name: "Madre", exact: true }).check()
    await page.getByRole("button", { name: "Guardar", exact: true }).click()

    // Guardar cierra el editor y el antecedente queda visible en la sección.
    await expect(
      page.getByRole("checkbox", { name: "Diabetes" }),
    ).not.toBeVisible()
    await expect(ahf.getByText("Diabetes")).toBeVisible()
    await expect(ahf.getByText("Madre")).toBeVisible()
  })

  test("Hallazgos G1 + M31b: lo marcado y luego omitido en el paso 2 no se guarda, y 'Registrar medición' captura un peso desde /perfil", async ({
    page,
  }) => {
    await freshUserWithConsent(page)

    const wizard = page.getByTestId("onboarding-wizard")
    await expect(wizard).toBeVisible()

    // Paso 1: se omite entero.
    await expect(wizard.getByText("Datos básicos")).toBeVisible()
    await wizard.getByRole("button", { name: "Omitir este paso" }).click()

    // Paso 2 (M31b): se marca Diabetes/Madre y DESPUÉS se pulsa "Omitir este
    // paso": lo marcado se descarta y no debe guardarse.
    await expect(wizard.getByText("Antecedentes familiares")).toBeVisible()
    await wizard.getByRole("checkbox", { name: "Diabetes" }).check()
    await wizard.getByRole("checkbox", { name: "Madre", exact: true }).check()
    await wizard.getByRole("button", { name: "Omitir este paso" }).click()

    // Resumen: nada capturado (ni básicos ni antecedentes).
    await expect(wizard.getByText("Resumen")).toBeVisible()
    await expect(wizard.getByText("Sin datos capturados")).toBeVisible()
    await expect(wizard.getByText("Sin antecedentes capturados")).toBeVisible()
    await wizard.getByRole("button", { name: "Guardar perfil" }).click()
    await expect(wizard).not.toBeVisible()

    // /perfil: la sección de antecedentes quedó vacía (M31b).
    await page.goto("/perfil")
    const ahf = page.getByTestId("profile-family-history")
    await expect(ahf.getByText("Sin registros")).toBeVisible()
    await expect(ahf.getByText("Diabetes")).toHaveCount(0)

    // (G1) "Registrar medición": primero un valor fuera de rango (500) muestra
    // el error inline y NO guarda; el diálogo sigue abierto.
    const basics = page.getByTestId("profile-basic-data")
    await basics.getByTestId("add-measurement").click()
    const dialog = page.getByTestId("measurement-dialog")
    await expect(dialog).toBeVisible()
    await expect(dialog.getByText("Registrar medición")).toBeVisible()
    await expect(dialog.getByText("Tipo de medición")).toBeVisible()
    const valor = dialog.getByRole("spinbutton", { name: /Peso \(kg\)/ })
    await valor.fill("500")
    await dialog.getByRole("button", { name: "Guardar", exact: true }).click()
    await expect(
      dialog.getByText("El peso debe estar entre 0.1 y 400 kg"),
    ).toBeVisible()
    await expect(dialog).toBeVisible()
    await expect(page.getByText("Medición registrada")).not.toBeVisible()

    // Con un valor válido (71) guarda: toast y el perfil muestra "71 kg" con
    // la fecha de hoy en dd/mm/aaaa.
    await valor.fill("71")
    await dialog.getByRole("button", { name: "Guardar", exact: true }).click()
    await expect(page.getByText("Medición registrada")).toBeVisible()
    await expect(dialog).not.toBeVisible()
    await expect(basics.getByText(`71 kg · ${todayMx()}`)).toBeVisible()
  })

  test("Hallazgos G3/M30 + M31c + G9: wizard con fecha, sexo y dos antecedentes; desde /perfil se edita uno y se desmarca el otro", async ({
    page,
  }) => {
    await freshUserWithConsent(page)

    const wizard = page.getByTestId("onboarding-wizard")
    await expect(wizard).toBeVisible()

    // Paso 1: fecha de nacimiento y sexo (Select de Radix, hallazgo G9).
    await expect(wizard.getByText("Datos básicos")).toBeVisible()
    await wizard.getByLabel("Fecha de nacimiento").fill("1988-07-30")
    await wizard.getByRole("combobox", { name: "Sexo" }).click()
    await page.getByRole("option", { name: "Mujer" }).click()
    await wizard.getByRole("button", { name: "Continuar" }).click()

    // Paso 2: DOS condiciones, cada parentesco dentro de su fieldset (role
    // group con el nombre de la condición).
    await expect(wizard.getByText("Antecedentes familiares")).toBeVisible()
    const diabetesWizard = wizard.getByRole("group", { name: "Diabetes" })
    await diabetesWizard.getByRole("checkbox", { name: "Diabetes" }).check()
    await diabetesWizard
      .getByRole("checkbox", { name: "Madre", exact: true })
      .check()
    const cancerWizard = wizard.getByRole("group", { name: "Cáncer" })
    await cancerWizard.getByRole("checkbox", { name: "Cáncer" }).check()
    await cancerWizard.getByRole("checkbox", { name: "Abuela materna" }).check()
    await wizard.getByRole("button", { name: "Continuar" }).click()

    // Resumen (M31c): la fecha aparece con la edad derivada a la fecha actual
    // "(N años)", el sexo con el texto del spec y los dos antecedentes.
    await expect(wizard.getByText("Resumen")).toBeVisible()
    const expectedAge = ageOn(new Date(1988, 6, 30), new Date())
    await expect(
      wizard.getByText(`30/07/1988 (${expectedAge} años)`),
    ).toBeVisible()
    await expect(wizard.getByText("Mujer")).toBeVisible()
    await expect(wizard.getByText("Diabetes")).toBeVisible()
    await expect(wizard.getByText("Madre", { exact: true })).toBeVisible()
    await expect(wizard.getByText("Cáncer")).toBeVisible()
    await expect(wizard.getByText("Abuela materna")).toBeVisible()
    await wizard.getByRole("button", { name: "Guardar perfil" }).click()
    await expect(wizard).not.toBeVisible()

    // /perfil refleja lo guardado.
    await page.goto("/perfil")
    const basics = page.getByTestId("profile-basic-data")
    await expect(basics.getByText("30/07/1988")).toBeVisible()
    await expect(basics.getByText(`${expectedAge} años`)).toBeVisible()
    await expect(basics.getByText("Mujer")).toBeVisible()
    const ahf = page.getByTestId("profile-family-history")
    await expect(ahf.getByText("Diabetes")).toBeVisible()
    await expect(ahf.getByText("Madre", { exact: true })).toBeVisible()
    await expect(ahf.getByText("Cáncer")).toBeVisible()
    await expect(ahf.getByText("Abuela materna")).toBeVisible()

    // (G3/M30) "Editar antecedentes": EDITAR Diabetes (añadir Padre → PUT) y
    // DESMARCAR Cáncer (→ DELETE) en la misma pasada.
    await ahf.getByRole("button", { name: "Editar antecedentes" }).click()
    const dialog = page.getByRole("dialog")
    const diabetesEdit = dialog.getByRole("group", { name: "Diabetes" })
    await expect(
      diabetesEdit.getByRole("checkbox", { name: "Madre", exact: true }),
    ).toBeChecked()
    await diabetesEdit
      .getByRole("checkbox", { name: "Padre", exact: true })
      .check()
    const cancerEdit = dialog.getByRole("group", { name: "Cáncer" })
    await cancerEdit.getByRole("checkbox", { name: "Cáncer" }).uncheck()
    await dialog.getByRole("button", { name: "Guardar", exact: true }).click()
    await expect(page.getByText("Antecedentes guardados")).toBeVisible()
    await expect(dialog).not.toBeVisible()

    // La sección refleja AMBOS cambios: Cáncer desaparece y Diabetes queda
    // con sus dos parentescos.
    await expect(ahf.getByText("Cáncer")).toHaveCount(0)
    await expect(ahf.getByText("Abuela materna")).toHaveCount(0)
    await expect(ahf.getByText("Diabetes")).toBeVisible()
    await expect(ahf.getByText("Madre", { exact: true })).toBeVisible()
    await expect(ahf.getByText("Padre", { exact: true })).toBeVisible()
  })
})
