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
// Fuente: openspec/changes/perfil-habitos/design.md → Interface contract →
// Frontend, y los escenarios de specs/records/patient-profile/spec.md.
//
// Tarjeta: data-testid history-card-habits en /perfil, enlace a
//   /perfil/habitos; insignia "Sin llenar" o "Con datos".
// Pantalla /perfil/habitos: heading "Hábitos"; "Guardar" (exact) hace el PUT,
//   avisa "Hábitos guardados" y vuelve a /perfil.
// Grupos (role "group" = fieldset, nombre exacto = su aria-label); cada chip
//   es un botón con aria-pressed. Los chips de estado de un bloque van ANTES
//   (en el DOM) que sus preguntas anidadas:
//   "Alcohol": "Nunca" · "Lo dejé" · "Actual".
//   "¿Con qué frecuencia tomas?": "2 a 3 veces por semana",
//     "4 o más veces por semana", …
//   "En un día que tomas, ¿cuántas bebidas?": "3 o 4", "10 o más", …
//   "¿Cada cuándo tomas 6 o más bebidas en una sola ocasión?": "Cada mes",
//     "A diario o casi", …
//   "Sobre todo fines de semana": "Sí" · "No" (tocar el elegido lo quita).
//   "Tabaco": "Nunca" · "Antes" · "Actual".
//   "Vapeador o cigarro electrónico": "Nunca" · "Antes" · "Actual".
//   "¿Dónde?" (selección múltiple): "Casa" · "Trabajo o escuela" ·
//     "Otro lugar" · "No me expongo" (excluyente).
//   "Humo de leña": "Nunca" · "Antes" · "Actual".
// Números (label exacto): "¿A qué edad dejaste de tomar?", "Cigarros al día",
//   "¿A qué edad empezaste a fumar?", "¿A qué edad dejaste de fumar?",
//   "Días por semana", "Años con humo de leña, aprox.".
// Errores en el cliente: el campo lleva aria-invalid="true", recibe el foco y
//   su aria-describedby apunta a un elemento con el mensaje exacto:
//   "La edad no puede ser mayor que tu edad actual";
//   "No puede ser mayor que la edad en que lo dejaste" (en la edad de inicio).
// ---------------------------------------------------------------------------

const API = `${process.env.VITE_API_URL}/api/v1`
const HABITS_URL = /\/perfil\/habitos\/?$/
const PROFILE_URL = /\/perfil\/?$/

const ALCOHOL = "Alcohol"
const FREQUENCY = "¿Con qué frecuencia tomas?"
const DRINKS = "En un día que tomas, ¿cuántas bebidas?"
const SIX_OR_MORE = "¿Cada cuándo tomas 6 o más bebidas en una sola ocasión?"
const WEEKENDS = "Sobre todo fines de semana"
const ALCOHOL_QUIT_AGE = "¿A qué edad dejaste de tomar?"
const TOBACCO = "Tabaco"
const CIGARETTES = "Cigarros al día"
const TOBACCO_START = "¿A qué edad empezaste a fumar?"
const TOBACCO_QUIT = "¿A qué edad dejaste de fumar?"
const VAPING = "Vapeador o cigarro electrónico"
const WHERE = "¿Dónde?"
const DAYS = "Días por semana"
const WOOD = "Humo de leña"
const WOOD_YEARS = "Años con humo de leña, aprox."

type Api = {
  request: APIRequestContext
  headers: Record<string, string>
}

/**
 * Paciente nuevo: alta por API privada, login por UI, consentimiento aceptado
 * y onboarding omitido (como profile-history.spec.ts). Devuelve un cliente del
 * API ya autenticado para preparar y comprobar datos.
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

/** Cliente del API autenticado como ese paciente. */
async function apiSession(
  request: APIRequestContext,
  email: string,
  password: string,
): Promise<Api> {
  const login = await request.post(`${API}/login/access-token`, {
    form: { username: email, password },
  })
  expect(login.ok()).toBeTruthy()
  const { access_token } = await login.json()
  return { request, headers: { Authorization: `Bearer ${access_token}` } }
}

/**
 * Fecha de nacimiento para que el paciente tenga exactamente `years` años hoy
 * en America/Mexico_City (el "hoy" del servidor y de mexicoCityTodayIso), sin
 * depender de la fecha real del run.
 */
function birthDateForAgeToday(years: number): string {
  const [y, m, d] = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Mexico_City",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  })
    .format(new Date())
    .split("-")
  const day = m === "02" && d === "29" ? "28" : d
  return `${Number(y) - years}-${m}-${day}`
}

/** Paciente de 36 años hoy (el "nacido el 15/03/1990" de los escenarios). */
async function setAge36(api: Api) {
  const res = await api.request.put(`${API}/profile`, {
    headers: api.headers,
    data: { birth_date: birthDateForAgeToday(36) },
  })
  expect(res.ok()).toBeTruthy()
}

async function seedHabits(api: Api, body: Record<string, unknown>) {
  const res = await api.request.put(`${API}/profile/habits`, {
    headers: api.headers,
    data: body,
  })
  expect(res.status(), await res.text()).toBe(200)
}

async function getHabits(api: Api) {
  const res = await api.request.get(`${API}/profile/habits`, {
    headers: api.headers,
  })
  expect(res.ok()).toBeTruthy()
  return res.json()
}

const card = (page: Page) => page.getByTestId("history-card-habits")

/** Abre el cuestionario desde la tarjeta "Hábitos" de "Mi perfil médico". */
async function openHabitsFromProfile(page: Page) {
  await page.goto("/perfil")
  await card(page).click()
  await page.waitForURL(HABITS_URL)
  await expect(
    page.getByRole("heading", { name: "Hábitos", exact: true }),
  ).toBeVisible()
  await expect(
    page.getByRole("button", { name: "Guardar", exact: true }),
  ).toBeVisible()
}

/** Reabre la pantalla tras guardar (ya en /perfil). */
async function reopen(page: Page) {
  await card(page).click()
  await page.waitForURL(HABITS_URL)
  await expect(
    page.getByRole("button", { name: "Guardar", exact: true }),
  ).toBeVisible()
}

/**
 * "Guardar" con éxito: aviso "Hábitos guardados" y de vuelta en /perfil. El
 * aviso de un guardado anterior puede seguir en pantalla (~4 s, y sonner lo
 * pausa mientras el puntero está encima): los que ya hay se marcan antes de
 * guardar y se verifica solo el NUEVO (review R4).
 */
async function saveOk(page: Page) {
  const toasts = page.locator("[data-sonner-toast]")
  await toasts.evaluateAll((shown) => {
    for (const toast of shown) toast.setAttribute("data-seen", "")
  })
  await page.getByRole("button", { name: "Guardar", exact: true }).click()
  await expect(
    page
      .locator("[data-sonner-toast]:not([data-seen])")
      .filter({ hasText: "Hábitos guardados" }),
  ).toBeVisible()
  await page.waitForURL(PROFILE_URL)
}

function group(page: Page, name: string): Locator {
  return page.getByRole("group", { name, exact: true }).first()
}

/** Chip `option` del grupo `groupName` (el primero en el DOM: el de estado). */
function chip(page: Page, groupName: string, option: string): Locator {
  return group(page, groupName)
    .getByRole("button", { name: option, exact: true })
    .first()
}

function numberField(page: Page, label: string): Locator {
  return page.getByLabel(label, { exact: true })
}

async function expectPressed(locator: Locator, pressed: boolean) {
  await expect(locator).toHaveAttribute("aria-pressed", String(pressed))
}

/**
 * Error junto a su campo: aria-invalid, foco, y aria-describedby apunta a un
 * elemento con el mensaje exacto.
 */
async function expectFieldError(page: Page, field: Locator, message: string) {
  await expect(field).toHaveAttribute("aria-invalid", "true")
  await expect(field).toBeFocused()
  const describedBy = (await field.getAttribute("aria-describedby")) ?? ""
  const ids = describedBy.split(/\s+/).filter(Boolean)
  expect(ids.length).toBeGreaterThan(0)
  const texts: string[] = []
  for (const id of ids) {
    const el = page.locator(`[id="${id}"]`)
    if ((await el.count()) > 0) {
      texts.push(((await el.first().textContent()) ?? "").trim())
    }
  }
  expect(texts).toContain(message)
}

/**
 * En móvil (s26-ultra) la navegación y el menú de usuario viven detrás del
 * trigger del sidebar (como profile.spec.ts): lo abre solo si `target` no está
 * ya visible.
 */
async function revealInSidebar(page: Page, target: Locator) {
  if (await target.isVisible().catch(() => false)) return
  await page.getByRole("button", { name: /barra lateral/ }).click()
  await expect(target).toBeVisible()
}

/** Login por el formulario de /login ya abierto, sin recargar la página. */
async function inAppLogin(page: Page, email: string, password: string) {
  await page.getByTestId("email-input").fill(email)
  await page.getByTestId("password-input").fill(password)
  await page.getByRole("button", { name: "Iniciar sesión" }).click()
  await page.waitForURL((url) => new URL(url).pathname === "/")
}

/** Errores de envío fuera de los campos (el pie del formulario). */
const formAlert = (page: Page) => page.locator("form").getByRole("alert")

test.describe("Perfil médico — hábitos (perfil-habitos, grupo 2)", () => {
  test("fila 1 (C-1) alcohol actual con las preguntas del AUDIT-C: tarjeta 'Con datos' y al reabrir siguen elegidas", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Actual").click()
    await chip(page, FREQUENCY, "2 a 3 veces por semana").click()
    await chip(page, DRINKS, "3 o 4").click()
    await chip(page, SIX_OR_MORE, "Cada mes").click()
    await chip(page, WEEKENDS, "Sí").click()
    await saveOk(page)

    await expect(card(page)).toContainText("Con datos")

    await reopen(page)
    await expectPressed(chip(page, ALCOHOL, "Actual"), true)
    await expectPressed(chip(page, FREQUENCY, "2 a 3 veces por semana"), true)
    await expectPressed(chip(page, DRINKS, "3 o 4"), true)
    await expectPressed(chip(page, SIX_OR_MORE, "Cada mes"), true)
    await expectPressed(chip(page, WEEKENDS, "Sí"), true)
  })

  test("fila 2 (C-1) lo dejó a los 30: al reabrir 'Lo dejé' con 30 y ninguna pregunta del AUDIT-C", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Lo dejé").click()
    await numberField(page, ALCOHOL_QUIT_AGE).fill("30")
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, ALCOHOL, "Lo dejé"), true)
    await expect(numberField(page, ALCOHOL_QUIT_AGE)).toHaveValue("30")
    await expect(page.getByRole("group", { name: FREQUENCY })).toHaveCount(0)
    await expect(page.getByRole("group", { name: DRINKS })).toHaveCount(0)
    await expect(page.getByRole("group", { name: SIX_OR_MORE })).toHaveCount(0)
    await expect(page.getByRole("group", { name: WEEKENDS })).toHaveCount(0)
  })

  test("fila 3 (C-1, C-2) una edad mayor que la actual: 40 con 36 años, error junto al campo con el foco y nada guardado", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Lo dejé").click()
    const quitAge = numberField(page, ALCOHOL_QUIT_AGE)
    await quitAge.fill("40")
    await page.getByRole("button", { name: "Guardar", exact: true }).click()

    await expectFieldError(
      page,
      quitAge,
      "La edad no puede ser mayor que tu edad actual",
    )
    await expect(page).toHaveURL(HABITS_URL)
    const saved = await getHabits(api)
    expect(saved.alcohol ?? null).toBeNull()
  })

  test("fila 4 (C-1) lo que no aplica se descarta: de 'Actual' con AUDIT-C a 'Nunca', sin preguntas al reabrir ni en lo guardado", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, {
      alcohol: {
        status: "current",
        frequency: "two_to_three_weekly",
        typical_drinks: "three_four",
        six_or_more: "monthly",
      },
    })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, ALCOHOL, "Actual"), true)
    await expectPressed(chip(page, FREQUENCY, "2 a 3 veces por semana"), true)

    await chip(page, ALCOHOL, "Nunca").click()
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, ALCOHOL, "Nunca"), true)
    await expect(page.getByRole("group", { name: FREQUENCY })).toHaveCount(0)
    await expect(page.getByRole("group", { name: DRINKS })).toHaveCount(0)
    await expect(page.getByRole("group", { name: SIX_OR_MORE })).toHaveCount(0)

    const saved = await getHabits(api)
    expect(saved.alcohol?.status).toBe("never")
    expect(saved.alcohol?.frequency ?? null).toBeNull()
    expect(saved.alcohol?.typical_drinks ?? null).toBeNull()
    expect(saved.alcohol?.six_or_more ?? null).toBeNull()
    expect(saved.alcohol?.mostly_weekends ?? null).toBeNull()
  })

  test("fila 5 (C-2) tabaco que dejó (10 al día, de 18 a 30) y vapeador actual: al reabrir ve esas respuestas", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, TOBACCO, "Antes").click()
    await numberField(page, CIGARETTES).fill("10")
    await numberField(page, TOBACCO_START).fill("18")
    await numberField(page, TOBACCO_QUIT).fill("30")
    await chip(page, VAPING, "Actual").click()
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, TOBACCO, "Antes"), true)
    await expect(numberField(page, CIGARETTES)).toHaveValue("10")
    await expect(numberField(page, TOBACCO_START)).toHaveValue("18")
    await expect(numberField(page, TOBACCO_QUIT)).toHaveValue("30")
    await expectPressed(chip(page, VAPING, "Actual"), true)
  })

  test("fila 6 (C-2) empezó a los 30 y lo dejó a los 18: error junto a la edad de inicio y nada guardado", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, TOBACCO, "Antes").click()
    const start = numberField(page, TOBACCO_START)
    await start.fill("30")
    await numberField(page, TOBACCO_QUIT).fill("18")
    await page.getByRole("button", { name: "Guardar", exact: true }).click()

    await expectFieldError(
      page,
      start,
      "No puede ser mayor que la edad en que lo dejaste",
    )
    await expect(page).toHaveURL(HABITS_URL)
    const saved = await getHabits(api)
    expect(saved.tobacco ?? null).toBeNull()
  })

  test("fila 7 (C-3) humo ajeno en casa y trabajo con 2 días, y después 'No me expongo' apaga los lugares y oculta los días", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, WHERE, "Casa").click()
    await chip(page, WHERE, "Trabajo o escuela").click()
    await numberField(page, DAYS).fill("2")
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, WHERE, "Casa"), true)
    await expectPressed(chip(page, WHERE, "Trabajo o escuela"), true)
    await expectPressed(chip(page, WHERE, "Otro lugar"), false)
    await expectPressed(chip(page, WHERE, "No me expongo"), false)
    await expect(numberField(page, DAYS)).toHaveValue("2")

    await chip(page, WHERE, "No me expongo").click()
    await expectPressed(chip(page, WHERE, "No me expongo"), true)
    await expectPressed(chip(page, WHERE, "Casa"), false)
    await expectPressed(chip(page, WHERE, "Trabajo o escuela"), false)
    await expect(numberField(page, DAYS)).toHaveCount(0)
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, WHERE, "No me expongo"), true)
    await expectPressed(chip(page, WHERE, "Casa"), false)
    await expectPressed(chip(page, WHERE, "Trabajo o escuela"), false)
    await expectPressed(chip(page, WHERE, "Otro lugar"), false)
    await expect(numberField(page, DAYS)).toHaveCount(0)

    const saved = await getHabits(api)
    expect(saved.secondhand_smoke?.exposed).toBe(false)
    expect(saved.secondhand_smoke?.places ?? []).toEqual([])
    expect(saved.secondhand_smoke?.days_per_week ?? null).toBeNull()
  })

  test("fila 8 (C-4) humo de leña de antes con 12 años: al reabrir ve 'Antes' con 12", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, WOOD, "Antes").click()
    await numberField(page, WOOD_YEARS).fill("12")
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, WOOD, "Antes"), true)
    await expect(numberField(page, WOOD_YEARS)).toHaveValue("12")
  })

  test("fila 9 contesta solo vapeador 'Nunca': tarjeta 'Con datos' y lo demás sigue sin contestar", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, VAPING, "Nunca").click()
    await saveOk(page)

    await expect(card(page)).toContainText("Con datos")

    await reopen(page)
    await expectPressed(chip(page, VAPING, "Nunca"), true)
    for (const option of ["Nunca", "Lo dejé", "Actual"]) {
      await expectPressed(chip(page, ALCOHOL, option), false)
    }
    for (const option of ["Nunca", "Antes", "Actual"]) {
      await expectPressed(chip(page, TOBACCO, option), false)
      await expectPressed(chip(page, WOOD, option), false)
    }
    for (const option of [
      "Casa",
      "Trabajo o escuela",
      "Otro lugar",
      "No me expongo",
    ]) {
      await expectPressed(chip(page, WHERE, option), false)
    }

    const saved = await getHabits(api)
    expect(saved.vaping).toBe("never")
    expect(saved.alcohol ?? null).toBeNull()
    expect(saved.tobacco ?? null).toBeNull()
    expect(saved.secondhand_smoke ?? null).toBeNull()
    expect(saved.wood_smoke ?? null).toBeNull()
  })

  test("fila 11 (C-6) sin puntaje ni riesgo: tras guardar el caso extremo, ni la pantalla ni 'Mi perfil médico' ni la respuesta dicen 'riesgo', 'puntaje' o 'AUDIT'", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Actual").click()
    await chip(page, FREQUENCY, "4 o más veces por semana").click()
    await chip(page, DRINKS, "10 o más").click()
    await chip(page, SIX_OR_MORE, "A diario o casi").click()
    await chip(page, TOBACCO, "Actual").click()
    await numberField(page, CIGARETTES).fill("20")
    await saveOk(page)

    const forbidden = /riesgo|puntaje|audit/i
    await expect(card(page)).toContainText("Con datos")
    expect(await page.locator("body").innerText()).not.toMatch(forbidden)

    await reopen(page)
    await expectPressed(chip(page, ALCOHOL, "Actual"), true)
    await expectPressed(chip(page, DRINKS, "10 o más"), true)
    await expect(numberField(page, CIGARETTES)).toHaveValue("20")
    expect(await page.locator("body").innerText()).not.toMatch(forbidden)

    const saved = await getHabits(api)
    expect(JSON.stringify(saved)).not.toMatch(forbidden)
  })

  test("fila 14 la tarjeta 'Hábitos' abre /perfil/habitos con el cuestionario y 'Guardar'", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await page.goto("/perfil")
    await expect(card(page)).toContainText("Hábitos")
    await card(page).click()
    await page.waitForURL(HABITS_URL)
    await expect(
      page.getByRole("heading", { name: "Hábitos", exact: true }),
    ).toBeVisible()
    await expect(group(page, ALCOHOL)).toBeVisible()
    await expect(group(page, TOBACCO)).toBeVisible()
    await expect(group(page, WHERE)).toBeVisible()
    await expect(group(page, WOOD)).toBeVisible()
    await expect(
      page.getByRole("button", { name: "Guardar", exact: true }),
    ).toBeVisible()
  })

  test("R1 otro paciente entra sin recargar tras 'Cerrar sesión': no ve ni guarda los hábitos del anterior", async ({
    page,
    request,
  }) => {
    const apiA = await freshPatient(page, request)
    await seedHabits(apiA, {
      tobacco: { status: "current", cigarettes_per_day: 20 },
      vaping: "current",
    })
    await openHabitsFromProfile(page)
    await expect(numberField(page, CIGARETTES)).toHaveValue("20")

    // B ya dio su consentimiento (por API) y entra directo a la app.
    const b = { email: randomEmail(), password: randomPassword() }
    await createUser(b)
    const apiB = await apiSession(request, b.email, b.password)
    const text = await request.get(`${API}/consent/text`, {
      headers: apiB.headers,
    })
    const consent = await request.post(`${API}/consent/`, {
      headers: apiB.headers,
      data: { version: (await text.json()).version },
    })
    expect(consent.ok()).toBeTruthy()

    // A cierra sesión desde el menú; B entra por el formulario sin recargar,
    // con su GET de hábitos retrasado 2 s (lo que tarde no debe dejar ver los
    // de A).
    const userMenu = page.getByTestId("user-menu")
    await revealInSidebar(page, userMenu)
    await userMenu.click()
    await page.getByRole("menuitem", { name: "Cerrar sesión" }).click()
    await page.waitForURL(/\/login/)
    await page.route("**/api/v1/profile/habits", async (route) => {
      if (route.request().method() === "GET") {
        await new Promise((resolve) => setTimeout(resolve, 2000))
      }
      await route.continue()
    })
    await inAppLogin(page, b.email, b.password)

    const perfilLink = page.getByRole("link", { name: "Mi perfil médico" })
    await revealInSidebar(page, perfilLink)
    await perfilLink.click()
    await page.waitForURL(PROFILE_URL)
    await reopen(page)
    await expectPressed(chip(page, TOBACCO, "Actual"), false)
    await expectPressed(chip(page, VAPING, "Actual"), false)
    await expect(numberField(page, CIGARETTES)).toHaveCount(0)

    await saveOk(page)
    const saved = await getHabits(apiB)
    expect(saved.tobacco ?? null).toBeNull()
    expect(saved.vaping ?? null).toBeNull()
  })

  test("R9 un 422 del servidor va junto a SU campo: la fecha de nacimiento llegó después de abrir el cuestionario", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)
    // Cargó sin fecha de nacimiento: el cliente no puede comparar la edad y
    // solo el servidor rechaza 40 con 36 años.
    await setAge36(api)

    await chip(page, ALCOHOL, "Lo dejé").click()
    const quitAge = numberField(page, ALCOHOL_QUIT_AGE)
    await quitAge.fill("40")
    const put = page.waitForResponse(
      (res) =>
        res.url().endsWith("/profile/habits") &&
        res.request().method() === "PUT",
    )
    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    expect((await put).status()).toBe(422)

    await expectFieldError(
      page,
      quitAge,
      "La edad no puede ser mayor que tu edad actual",
    )
    await expect(formAlert(page)).toHaveCount(0)
    await expect(page).toHaveURL(HABITS_URL)
    const saved = await getHabits(api)
    expect(saved.alcohol ?? null).toBeNull()
  })

  test("R10b 'Cancelar' vuelve a /perfil sin guardar: lo guardado sigue igual", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, { vaping: "never" })
    await openHabitsFromProfile(page)
    const puts: string[] = []
    page.on("request", (req) => {
      if (req.method() === "PUT" && req.url().endsWith("/profile/habits")) {
        puts.push(req.url())
      }
    })

    await chip(page, VAPING, "Actual").click()
    await expectPressed(chip(page, VAPING, "Actual"), true)
    await page.getByRole("button", { name: "Cancelar", exact: true }).click()
    await page.waitForURL(PROFILE_URL)

    expect(puts).toEqual([])
    const saved = await getHabits(api)
    expect(saved.vaping).toBe("never")
  })

  test("R12 un error no sobrevive a su pregunta: de 'Antes' a 'Actual' se va el de 'empezó después de dejarlo'", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, TOBACCO, "Antes").click()
    const start = numberField(page, TOBACCO_START)
    await start.fill("30")
    await numberField(page, TOBACCO_QUIT).fill("18")
    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    const message = "No puede ser mayor que la edad en que lo dejaste"
    await expectFieldError(page, start, message)

    await chip(page, TOBACCO, "Actual").click()
    await expect(numberField(page, TOBACCO_QUIT)).toHaveCount(0)
    await expect(start).not.toHaveAttribute("aria-invalid", "true")
    await expect(page.getByText(message)).toHaveCount(0)
  })

  test("R13 las ayudas de 'Humo de tabaco de otras personas' y 'Humo de leña' describen sus grupos", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await expect(group(page, WHERE)).toHaveAccessibleDescription(
      "Estar cerca de quien fuma, aunque tú no fumes.",
    )
    await expect(group(page, WOOD)).toHaveAccessibleDescription(
      "Cocinar o calentar la casa con leña o carbón.",
    )
  })

  test("R14 'Sobre todo fines de semana' con chips 'Sí' / 'No': tocar 'Sí' otra vez lo deja sin contestar", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Actual").click()
    await chip(page, WEEKENDS, "Sí").click()
    await saveOk(page)
    expect((await getHabits(api)).alcohol?.mostly_weekends).toBe(true)

    await reopen(page)
    await expectPressed(chip(page, WEEKENDS, "Sí"), true)
    await chip(page, WEEKENDS, "Sí").click()
    await expectPressed(chip(page, WEEKENDS, "Sí"), false)
    await expectPressed(chip(page, WEEKENDS, "No"), false)
    await saveOk(page)

    const saved = await getHabits(api)
    expect(saved.alcohol?.status).toBe("current")
    expect(saved.alcohol?.mostly_weekends ?? null).toBeNull()
  })

  test("R18 un 422 en una pregunta de chips va bajo SU grupo (servidor simulado: la UI no puede provocarlo)", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)
    await chip(page, ALCOHOL, "Actual").click()
    await chip(page, FREQUENCY, "2 a 3 veces por semana").click()
    await page.route("**/api/v1/profile/habits", async (route) => {
      if (route.request().method() !== "PUT") return route.continue()
      await route.fulfill({
        status: 422,
        headers: {
          "access-control-allow-origin":
            route.request().headers().origin ?? "*",
        },
        json: {
          detail: [
            {
              loc: ["body", "alcohol", "frequency"],
              msg: "Elige una frecuencia de la lista",
              type: "literal_error",
            },
            {
              loc: ["body", "alcohol", "mostly_weekends"],
              msg: "Elige «Sí» o «No»",
              type: "bool_type",
            },
          ],
        },
      })
    })
    await page.getByRole("button", { name: "Guardar", exact: true }).click()

    await expect(group(page, FREQUENCY)).toHaveAttribute("data-invalid", "true")
    await expect(group(page, FREQUENCY)).toHaveAccessibleDescription(
      "Elige una frecuencia de la lista",
    )
    await expect(group(page, WEEKENDS)).toHaveAccessibleDescription(
      "Elige «Sí» o «No»",
    )
    await expect(chip(page, FREQUENCY, "Una vez al mes o menos")).toBeFocused()
    await expect(group(page, ALCOHOL)).not.toHaveAttribute("data-invalid")
    await expect(formAlert(page)).toHaveCount(0)
    await expect(page).toHaveURL(HABITS_URL)
  })
})
