import { expect, type Page, test } from "@playwright/test"
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
//     "Ahora no, llévame a mi expediente"; avanzar "Continuar";
//     cierre "Guardar perfil".
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
    await logOutUser(page)
    await logInExpectingExpediente(page, email, password)
    await expect(
      page.getByRole("button", { name: "Registrar receta" }),
    ).toBeVisible()
    await expect(page.getByTestId("onboarding-wizard")).not.toBeVisible()
    await expect(page.getByTestId("consent-accept-button")).not.toBeVisible()
  })

  test("Escenario 10: omitir datos básicos, guardar solo Diabetes/Madre y completar la fecha de nacimiento desde /perfil", async ({
    page,
  }) => {
    await freshUserWithConsent(page)

    const wizard = page.getByTestId("onboarding-wizard")
    await expect(wizard).toBeVisible()

    // Paso 1 (datos básicos): se omite entero.
    await expect(wizard.getByText("Datos básicos")).toBeVisible()
    await wizard.getByRole("button", { name: "Omitir este paso" }).click()

    // Paso 2 (antecedentes familiares): marcar Diabetes muestra los
    // parentescos; se elige Madre.
    await expect(wizard.getByText("Antecedentes familiares")).toBeVisible()
    const madre = wizard.getByRole("checkbox", { name: "Madre", exact: true })
    await expect(madre).not.toBeVisible()
    await wizard.getByRole("checkbox", { name: "Diabetes" }).check()
    await madre.check()

    // Paso 3 (resumen): refleja lo capturado y guarda.
    await wizard.getByRole("button", { name: "Continuar" }).click()
    await expect(wizard.getByText("Resumen")).toBeVisible()
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

    // Desde /perfil se completa la fecha de nacimiento (15/03/1990).
    await basics.getByRole("button", { name: "Editar datos básicos" }).click()
    await page.getByLabel("Fecha de nacimiento").fill("1990-03-15")
    await page.getByRole("button", { name: "Guardar", exact: true }).click()

    // La fecha se muestra en es-MX con la edad derivada a la fecha actual.
    await expect(basics.getByText("15/03/1990")).toBeVisible()
    const expectedAge = ageOn(new Date(1990, 2, 15), new Date())
    await expect(basics.getByText(`${expectedAge} años`)).toBeVisible()
  })

  test("Escenario 11: /perfil lista las 6 secciones adicionales vacías y ninguna ofrece formulario de captura", async ({
    page,
  }) => {
    // Cuenta con el onboarding ya cerrado (omitido).
    await freshUserWithConsent(page)
    await skipOnboardingToExpediente(page)

    // La navegación tiene la entrada "Mi perfil médico" y lleva a /perfil.
    await page.getByRole("link", { name: "Mi perfil médico" }).click()
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
    await expect(
      sections.getByRole("button", { name: /Guardar/ }),
    ).toHaveCount(0)

    // Si existe un botón "Añadir"/"Agregar" meramente informativo, hacer clic
    // NO debe abrir captura (ningún formulario con campos aparece).
    const addButtons = sections.getByRole("button", {
      name: /Añadir|Agregar/,
    })
    const addCount = await addButtons.count()
    for (let i = 0; i < addCount; i++) {
      await addButtons.nth(i).click()
      const dialog = page.getByRole("dialog")
      if (await dialog.isVisible().catch(() => false)) {
        await expect(dialog.locator("input, textarea, select")).toHaveCount(0)
        await expect(
          dialog.getByRole("button", { name: /Guardar/ }),
        ).toHaveCount(0)
        await page.keyboard.press("Escape")
        await expect(dialog).not.toBeVisible()
      }
      await expect(sections.locator("input, textarea, select")).toHaveCount(0)
    }
  })
})
