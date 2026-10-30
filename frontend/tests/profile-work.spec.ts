import {
  type APIRequestContext,
  expect,
  type Locator,
  type Page,
  test,
} from "@playwright/test"
import { createUser } from "./utils/privateApi"
import { randomEmail, randomPassword } from "./utils/random"
import { logInUser } from "./utils/user"

test.use({ storageState: { cookies: [], origins: [] } })

// --- Contrato de UI que este spec fija (el implementer lo lee de aquí) -------
//
// Fuente: openspec/changes/perfil-trabajo/design.md → Interface contract
// (escenarios T-1…T-6 de la spec delta y filas 1-8 del test plan).
//
// API: GET/PUT /api/v1/profile/work con Work { status, occupation (≤200),
//   longest_job (≤200), exposures ("dust"|"chemicals"|"loud_noise")[],
//   no_exposures, shift ("day"|"night"|"rotating") }. El servidor recorta,
//   descarta lo que solo aplica a "employed" con otra situación y las
//   exposiciones con no_exposures.
// Tarjeta data-testid="profile-basic-data" de /perfil:
//   botón "Editar trabajo" → diálogo (role dialog) "Tu trabajo" con la
//   descripción "El médico lo pregunta porque lo que haces todo el día
//   también es salud.".
//   Fila con la etiqueta "Trabajo" (texto exacto) y su valor: ocupación (o
//   la etiqueta de la situación sin ocupación) · turno en minúsculas ·
//   "antes: " + trabajo de más años tal cual · "expuesto a " + exposiciones
//   en minúsculas unidas por ", "; separadas por " · ". Sin datos:
//   "Sin registrar".
// Diálogo (chips = botones con aria-pressed dentro de grupos con nombre
//   accesible, D18; los de una sola opción se quitan al tocarlos otra vez):
//   grupo "Hoy…": Trabajo · Busco trabajo · Jubilado o pensionado · Hogar ·
//     Estudio · No puedo trabajar por mi salud.
//   Solo con "Trabajo": texto "¿A qué te dedicas?" (máx. 200); grupo
//     "En tu trabajo te expones a…": Polvo · Químicos o solventes ·
//     Ruido fuerte, más el chip "Nada de esto" que las excluye; grupo
//     "Turno": De día · De noche · Rotativo.
//   Siempre: texto "El trabajo que más años has tenido, si es otro"
//     (máx. 200).
//   Botones "Cancelar" y "Guardar". Mientras el PUT está en curso, "Guardar"
//   y los chips no están disponibles (disabled o aria-disabled="true", D20).
//   Al guardar, el diálogo se cierra y la tarjeta muestra el nuevo resumen.
// Sin veredicto (C-6/NFR-008): ni "riesgo", ni "puntaje", ni "peligro".
// ---------------------------------------------------------------------------

const API = `${process.env.VITE_API_URL}/api/v1`

const DIALOG_TITLE = "Tu trabajo"
const DIALOG_DESCRIPTION =
  "El médico lo pregunta porque lo que haces todo el día también es salud."
const ROW_LABEL = "Trabajo"
const EMPTY = "Sin registrar"

const STATUS = "Hoy…"
const EXPOSURES = "En tu trabajo te expones a…"
const SHIFT = "Turno"
const NONE_OF_THESE = "Nada de esto"
const OCCUPATION = "¿A qué te dedicas?"
const LONGEST_JOB = "El trabajo que más años has tenido, si es otro"

const STATUS_OPTIONS = [
  "Trabajo",
  "Busco trabajo",
  "Jubilado o pensionado",
  "Hogar",
  "Estudio",
  "No puedo trabajar por mi salud",
]
const EXPOSURE_OPTIONS = ["Polvo", "Químicos o solventes", "Ruido fuerte"]
const SHIFT_OPTIONS = ["De día", "De noche", "Rotativo"]

/** "Guardar"; mientras guarda puede decir "Guardando…". */
const SAVE_BUTTON = /^Guardar$|^Guardando/

const FORBIDDEN = /riesgo|puntaje|peligro/i

type Api = {
  request: APIRequestContext
  headers: Record<string, string>
}

/**
 * Sin keep-alive: el backend cierra las conexiones inactivas a los 5 s y un
 * test que espera a la UI más que eso reusaría un socket a medio cerrar
 * ("socket hang up"). Con "Connection: close" cada llamada abre el suyo.
 */
const NO_KEEP_ALIVE = { Connection: "close" }

async function apiSession(
  request: APIRequestContext,
  email: string,
  password: string,
): Promise<Api> {
  const login = await request.post(`${API}/login/access-token`, {
    headers: NO_KEEP_ALIVE,
    form: { username: email, password },
  })
  expect(login.ok()).toBeTruthy()
  const { access_token } = await login.json()
  return {
    request,
    headers: { ...NO_KEEP_ALIVE, Authorization: `Bearer ${access_token}` },
  }
}

/**
 * Paciente nuevo: alta por API privada, login por UI, consentimiento aceptado
 * y onboarding omitido (como profile-habits.spec.ts). Devuelve un cliente del
 * API ya autenticado para preparar datos.
 */
async function freshPatient(
  page: Page,
  request: APIRequestContext,
): Promise<Api> {
  const email = randomEmail()
  const password = randomPassword()
  await createUser({ email, password })
  await logInUser(page, email, password)

  const consentButton = page.getByTestId("consent-accept-button")
  await expect(consentButton).toBeVisible()
  await consentButton.click()
  await expect(consentButton).not.toBeVisible()

  const wizard = page.getByTestId("onboarding-wizard")
  await expect(wizard).toBeVisible()
  await page
    .getByRole("button", { name: "Ahora no, llévame a mi expediente" })
    .click()
  await page.waitForURL(/\/expediente/)

  return apiSession(request, email, password)
}

async function seedWork(api: Api, body: Record<string, unknown>) {
  const res = await api.request.put(`${API}/profile/work`, {
    headers: api.headers,
    data: body,
  })
  expect(res.status(), await res.text()).toBe(200)
}

const basics = (page: Page) => page.getByTestId("profile-basic-data")

const workDialog = (page: Page) =>
  page.getByRole("dialog", { name: DIALOG_TITLE })

async function openProfile(page: Page) {
  await page.goto("/perfil")
  await expect(
    page.getByRole("heading", { name: "Mi perfil médico" }),
  ).toBeVisible()
  await expect(basics(page)).toBeVisible()
}

/** Abre «Editar trabajo» desde la tarjeta de datos básicos. */
async function openWorkDialog(page: Page): Promise<Locator> {
  await basics(page)
    .getByRole("button", { name: "Editar trabajo", exact: true })
    .click()
  const dialog = workDialog(page)
  await expect(dialog).toBeVisible()
  return dialog
}

/** «Guardar» con éxito: sale un PUT /profile/work y el diálogo se cierra. */
async function save(page: Page, dialog: Locator) {
  const put = page.waitForResponse(
    (res) =>
      new URL(res.url()).pathname.endsWith("/profile/work") &&
      res.request().method() === "PUT",
  )
  await dialog.getByRole("button", { name: "Guardar", exact: true }).click()
  expect((await put).status()).toBe(200)
  await expect(dialog).toHaveCount(0)
}

function group(dialog: Locator, name: string): Locator {
  return dialog.getByRole("group", { name, exact: true })
}

function chip(dialog: Locator, groupName: string, option: string): Locator {
  return group(dialog, groupName).getByRole("button", {
    name: option,
    exact: true,
  })
}

/** El chip excluyente «Nada de esto» (puede ir dentro o fuera del grupo). */
function noneChip(dialog: Locator): Locator {
  return dialog.getByRole("button", { name: NONE_OF_THESE, exact: true })
}

function textField(dialog: Locator, label: string): Locator {
  return dialog.getByLabel(label, { exact: true })
}

async function expectPressed(locator: Locator, pressed: boolean) {
  await expect(locator).toHaveAttribute("aria-pressed", String(pressed))
}

/** No disponible: `disabled` nativo o aria-disabled="true" (D20). */
async function expectUnavailable(locator: Locator) {
  await expect
    .poll(() =>
      locator.evaluate(
        (el) =>
          (el as HTMLButtonElement).disabled === true ||
          el.getAttribute("aria-disabled") === "true",
      ),
    )
    .toBe(true)
}

/**
 * El valor de la fila «Trabajo» de la tarjeta: sube desde la etiqueta (texto
 * exacto "Trabajo") hasta el primer ancestro que contiene algo más que ella
 * (la fila) y devuelve ese texto sin la etiqueta, con los espacios
 * normalizados. No asume dt/dd, div o span.
 */
async function workRowValue(page: Page): Promise<string> {
  const label = basics(page).getByText(ROW_LABEL, { exact: true })
  if ((await label.count()) !== 1) return `<${await label.count()} etiquetas>`
  return label.evaluate((el, labelText) => {
    const norm = (s: string | null) => (s ?? "").replace(/\s+/g, " ").trim()
    let row: Element = el
    while (row.parentElement && norm(row.textContent) === labelText) {
      row = row.parentElement
    }
    const full = norm(row.textContent)
    return full.startsWith(labelText)
      ? full.slice(labelText.length).trim()
      : full
  }, ROW_LABEL)
}

async function expectWorkRow(page: Page, value: string) {
  await expect.poll(() => workRowValue(page)).toBe(value)
}

/**
 * Retiene el primer PUT /profile/work; `releaseAndWait` lo suelta y devuelve
 * su respuesta.
 */
async function holdFirstWorkPut(page: Page) {
  let release = () => {}
  const held = new Promise<void>((resolve) => {
    release = resolve
  })
  let routed = 0
  await page.route("**/api/v1/profile/work", async (route) => {
    if (route.request().method() === "PUT" && routed++ === 0) await held
    await route.continue()
  })
  return {
    async releaseAndWait() {
      const response = page.waitForResponse(
        (res) =>
          new URL(res.url()).pathname.endsWith("/profile/work") &&
          res.request().method() === "PUT",
      )
      release()
      return response
    },
  }
}

test.describe("Perfil médico — trabajo (perfil-trabajo)", () => {
  test("T-1 guardar el trabajo y verlo en la tarjeta: Trabajo, «Chofer de transporte», Ruido fuerte y Rotativo → «Chofer de transporte · rotativo · expuesto a ruido fuerte» y al reabrir las mismas respuestas", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openProfile(page)

    const dialog = await openWorkDialog(page)
    await expect(dialog).toContainText(DIALOG_DESCRIPTION)
    await chip(dialog, STATUS, "Trabajo").click()
    await expectPressed(chip(dialog, STATUS, "Trabajo"), true)
    await textField(dialog, OCCUPATION).fill("Chofer de transporte")
    await chip(dialog, EXPOSURES, "Ruido fuerte").click()
    await chip(dialog, SHIFT, "Rotativo").click()
    await save(page, dialog)

    await expectWorkRow(
      page,
      "Chofer de transporte · rotativo · expuesto a ruido fuerte",
    )

    const again = await openWorkDialog(page)
    await expectPressed(chip(again, STATUS, "Trabajo"), true)
    await expect(textField(again, OCCUPATION)).toHaveValue(
      "Chofer de transporte",
    )
    await expectPressed(chip(again, EXPOSURES, "Ruido fuerte"), true)
    await expectPressed(chip(again, EXPOSURES, "Polvo"), false)
    await expectPressed(chip(again, EXPOSURES, "Químicos o solventes"), false)
    await expectPressed(noneChip(again), false)
    await expectPressed(chip(again, SHIFT, "Rotativo"), true)
    await expectPressed(chip(again, SHIFT, "De día"), false)
    await expectPressed(chip(again, SHIFT, "De noche"), false)
    await expect(textField(again, LONGEST_JOB)).toHaveValue("")
  })

  test("T-2 todo es opcional: guardar sin contestar cierra el diálogo y la fila «Trabajo» dice «Sin registrar»", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openProfile(page)
    await expectWorkRow(page, EMPTY)

    const dialog = await openWorkDialog(page)
    for (const option of STATUS_OPTIONS) {
      await expectPressed(chip(dialog, STATUS, option), false)
    }
    await save(page, dialog)

    await expectWorkRow(page, EMPTY)
  })

  test("T-3 «Nada de esto» excluye las exposiciones: Polvo y luego Nada de esto apaga Polvo; luego Químicos o solventes apaga Nada de esto", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openProfile(page)

    const dialog = await openWorkDialog(page)
    await chip(dialog, STATUS, "Trabajo").click()

    await chip(dialog, EXPOSURES, "Polvo").click()
    await expectPressed(chip(dialog, EXPOSURES, "Polvo"), true)

    await noneChip(dialog).click()
    await expectPressed(noneChip(dialog), true)
    await expectPressed(chip(dialog, EXPOSURES, "Polvo"), false)

    await chip(dialog, EXPOSURES, "Químicos o solventes").click()
    await expectPressed(chip(dialog, EXPOSURES, "Químicos o solventes"), true)
    await expectPressed(noneChip(dialog), false)
    await expectPressed(chip(dialog, EXPOSURES, "Polvo"), false)
  })

  test("T-4 el detalle solo aplica con «Trabajo»: con Jubilado o pensionado no se ven ocupación, exposiciones ni turno; «Minero» como trabajo de más años → «Jubilado o pensionado · antes: Minero»", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openProfile(page)

    const dialog = await openWorkDialog(page)
    await chip(dialog, STATUS, "Jubilado o pensionado").click()
    await expectPressed(chip(dialog, STATUS, "Jubilado o pensionado"), true)

    await expect(textField(dialog, OCCUPATION)).toHaveCount(0)
    await expect(group(dialog, EXPOSURES)).toHaveCount(0)
    await expect(noneChip(dialog)).toHaveCount(0)
    await expect(group(dialog, SHIFT)).toHaveCount(0)

    await textField(dialog, LONGEST_JOB).fill("Minero")
    await save(page, dialog)

    await expectWorkRow(page, "Jubilado o pensionado · antes: Minero")
  })

  test("T-6 cambiar de situación borra lo del trabajo: de Trabajo («Chofer de transporte», Ruido fuerte, Rotativo, «Taxista») a Busco trabajo → «Busco trabajo · antes: Taxista»; al reabrir y elegir Trabajo, ocupación vacía y sin turno ni exposición", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedWork(api, {
      status: "employed",
      occupation: "Chofer de transporte",
      longest_job: "Taxista",
      exposures: ["loud_noise"],
      no_exposures: false,
      shift: "rotating",
    })
    await openProfile(page)
    await expectWorkRow(
      page,
      "Chofer de transporte · rotativo · antes: Taxista · expuesto a ruido fuerte",
    )

    const dialog = await openWorkDialog(page)
    await expectPressed(chip(dialog, STATUS, "Trabajo"), true)
    await chip(dialog, STATUS, "Busco trabajo").click()
    await expectPressed(chip(dialog, STATUS, "Busco trabajo"), true)
    await expectPressed(chip(dialog, STATUS, "Trabajo"), false)
    await save(page, dialog)

    await expectWorkRow(page, "Busco trabajo · antes: Taxista")

    const again = await openWorkDialog(page)
    await expectPressed(chip(again, STATUS, "Busco trabajo"), true)
    await expect(textField(again, LONGEST_JOB)).toHaveValue("Taxista")
    await chip(again, STATUS, "Trabajo").click()
    await expect(textField(again, OCCUPATION)).toHaveValue("")
    for (const option of EXPOSURE_OPTIONS) {
      await expectPressed(chip(again, EXPOSURES, option), false)
    }
    await expectPressed(noneChip(again), false)
    for (const option of SHIFT_OPTIONS) {
      await expectPressed(chip(again, SHIFT, option), false)
    }
  })

  test("largo: los campos de texto no aceptan más de 200 caracteres (escribir 205 deja 200)", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openProfile(page)

    const dialog = await openWorkDialog(page)
    await chip(dialog, STATUS, "Trabajo").click()

    const typed = "a".repeat(205)
    for (const label of [OCCUPATION, LONGEST_JOB]) {
      const field = textField(dialog, label)
      await field.click()
      await field.pressSequentially(typed)
      await expect(field).toHaveValue("a".repeat(200))
    }
  })

  test("accesibilidad, D20 y sin veredicto: cada grupo de chips tiene nombre; con el PUT retenido «Guardar» y los chips no están disponibles; ni el diálogo ni la tarjeta dicen «riesgo», «puntaje» o «peligro»; en s26-ultra el diálogo no se desborda", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openProfile(page)

    const dialog = await openWorkDialog(page)
    // Al abrir, el foco queda dentro del diálogo (no en un elemento concreto).
    await expect
      .poll(() => dialog.evaluate((el) => el.contains(document.activeElement)))
      .toBe(true)
    await expect(group(dialog, STATUS)).toBeVisible()
    await chip(dialog, STATUS, "Trabajo").click()
    await expect(group(dialog, EXPOSURES)).toBeVisible()
    await expect(group(dialog, SHIFT)).toBeVisible()

    // Cada chip del diálogo vive dentro de un grupo con nombre accesible.
    const groups = dialog.getByRole("group")
    const groupCount = await groups.count()
    expect(groupCount).toBeGreaterThanOrEqual(3)
    for (let i = 0; i < groupCount; i++) {
      await expect(groups.nth(i)).toHaveAccessibleName(/\S/)
    }
    for (const option of STATUS_OPTIONS) {
      await expect(chip(dialog, STATUS, option)).toBeVisible()
    }
    for (const option of EXPOSURE_OPTIONS) {
      await expect(chip(dialog, EXPOSURES, option)).toBeVisible()
    }
    for (const option of SHIFT_OPTIONS) {
      await expect(chip(dialog, SHIFT, option)).toBeVisible()
    }

    // Respuesta completa para que el diálogo y la tarjeta muestren todo.
    await textField(dialog, OCCUPATION).fill("Soldador")
    for (const option of EXPOSURE_OPTIONS) {
      await chip(dialog, EXPOSURES, option).click()
    }
    await chip(dialog, SHIFT, "De noche").click()
    await textField(dialog, LONGEST_JOB).fill("Minero")
    expect(await dialog.innerText()).not.toMatch(FORBIDDEN)

    if (test.info().project.name === "s26-ultra") {
      const box = await dialog.boundingBox()
      expect(box).not.toBeNull()
      const viewport = page.viewportSize()
      expect(viewport).not.toBeNull()
      if (box && viewport) {
        expect(box.x).toBeGreaterThanOrEqual(0)
        expect(box.x + box.width).toBeLessThanOrEqual(viewport.width)
      }
      const overflow = await dialog.evaluate(
        (el) => el.scrollWidth - el.clientWidth,
      )
      expect(overflow).toBeLessThanOrEqual(0)
      const pageOverflow = await page.evaluate(
        () =>
          document.documentElement.scrollWidth -
          document.documentElement.clientWidth,
      )
      expect(pageOverflow).toBeLessThanOrEqual(0)
    }

    // D20: con el PUT retenido, «Guardar» y los chips no están disponibles.
    const hold = await holdFirstWorkPut(page)
    await dialog.getByRole("button", { name: "Guardar", exact: true }).click()
    await expectUnavailable(dialog.getByRole("button", { name: SAVE_BUTTON }))
    for (const option of STATUS_OPTIONS) {
      await expectUnavailable(chip(dialog, STATUS, option))
    }
    for (const option of EXPOSURE_OPTIONS) {
      await expectUnavailable(chip(dialog, EXPOSURES, option))
    }
    await expectUnavailable(noneChip(dialog))
    for (const option of SHIFT_OPTIONS) {
      await expectUnavailable(chip(dialog, SHIFT, option))
    }
    // La X de cerrar («Cerrar») tampoco está disponible: ausente o
    // aria-disabled="true".
    const closeX = dialog.getByRole("button", { name: "Cerrar", exact: true })
    await expect
      .poll(
        async () =>
          (await closeX.count()) === 0 ||
          (await closeX.getAttribute("aria-disabled")) === "true",
      )
      .toBe(true)

    const response = await hold.releaseAndWait()
    expect(response.status()).toBe(200)
    await expect(dialog).toHaveCount(0)

    await expectWorkRow(
      page,
      "Soldador · de noche · antes: Minero · expuesto a polvo, químicos o solventes, ruido fuerte",
    )
    expect(await basics(page).innerText()).not.toMatch(FORBIDDEN)

    if (test.info().project.name === "s26-ultra") {
      // Una ocupación de 200 caracteres sin espacios no desborda la página.
      const again = await openWorkDialog(page)
      await textField(again, OCCUPATION).fill("a".repeat(200))
      await save(page, again)
      await expect
        .poll(() => workRowValue(page))
        .toMatch(new RegExp(`^${"a".repeat(200)} · `))
      const pageOverflow = await page.evaluate(
        () =>
          document.documentElement.scrollWidth -
          document.documentElement.clientWidth,
      )
      expect(pageOverflow).toBeLessThanOrEqual(0)
    }
  })
})
