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
// Fuentes: openspec/changes/perfil-habitos/design.md (C1) y
// openspec/changes/perfil-habitos-ajustes/design.md → Interface contract →
// Frontend, con los escenarios de specs/records/patient-profile/spec.md.
//
// Tarjeta: data-testid history-card-habits en /perfil, enlace a
//   /perfil/habitos; insignia "Sin llenar" o "Con datos".
// Pantalla /perfil/habitos: heading "Hábitos"; debajo de la introducción,
//   "Tus respuestas se guardan cuando tocas «Guardar»." Sin guardado
//   automático: nada sale (ningún PUT /profile/habits) hasta "Guardar".
// "Guardar" (exact): valida todo; con errores, foco al primero y no manda
//   nada; si no, UN PUT, avisa "Hábitos guardados" y vuelve a /perfil.
// "Cancelar" (exact): nunca manda nada ni abre el diálogo de salida; con
//   cambios sin guardar vuelve a /perfil con "Se descartaron los cambios";
//   sin cambios, solo vuelve.
// Mientras el PUT está en curso (D20): "Guardar" y "Cancelar" con
//   aria-disabled="true" (NO disabled nativo); clic o Enter no hacen nada y
//   el foco sigue en "Guardar", que dice "Guardando…" (R2-5). Las preguntas
//   tampoco cambian: chips con aria-disabled="true" que ignoran el clic y
//   números de solo lectura (R2-3). Salir entonces no pregunta, y al terminar
//   el PUT no hay aviso ni regreso a /perfil si la pantalla ya no está
//   abierta o el token cambió (R2-1, R2-2).
// "Seguir editando" devuelve el foco adonde estaba; si ese elemento ya no
//   existe (el menú lateral del celular se cerró), al título "Hábitos" (R2-4).
// Cambios sin guardar = lo que está en pantalla (incluido un número escrito
//   sin salir del campo) difiere de lo que había al abrir; elegir una opción
//   y volver a la de antes no cuenta.
// Salir dentro de la app (menú, enlace "‹ Mi perfil médico", atrás del
//   navegador) con cambios: diálogo "¿Salir sin guardar?" con "Los cambios que
//   hiciste en Hábitos se van a perder.", botones "Seguir editando" (con el
//   foco al abrir; deja la pantalla como estaba) y "Salir sin guardar" (sigue
//   a donde iba). Recargar o cerrar la pestaña con cambios: aviso
//   beforeunload del navegador; sin cambios, ninguno. Si la sesión terminó o
//   cambió (otro token en localStorage), ni diálogo ni beforeunload.
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
//   "¿Con qué frecuencia vapeas?" (solo con "Actual"): "Todos los días" ·
//     "Algunos días".
//   "¿Dónde?" (selección múltiple): "Casa" · "Trabajo o escuela" ·
//     "Otro lugar" · "No me expongo" (excluyente).
//   "Humo de leña": "Nunca" · "Antes" · "Actual".
// Números (label exacto):
//   alcohol: "¿A qué edad empezaste a tomar?" (con "Lo dejé" o "Actual",
//     ayuda "Sin contar probaditas."), "¿A qué edad dejaste de tomar?";
//   tabaco: "Cigarros al día", "¿A qué edad empezaste a fumar?",
//     "¿A qué edad dejaste de fumar?";
//   vapeador: "¿A qué edad empezaste a vapear?" ("Antes" o "Actual"),
//     "¿A qué edad dejaste de vapear?" ("Antes"),
//     "¿Cuántos días de los últimos 30?" ("Actual" + "Algunos días");
//   humo ajeno: "Días por semana";
//   leña ("Antes" o "Actual"): "¿A qué edad empezaste a exponerte?",
//     "¿Cuántas horas al día, en promedio?"; con "Antes",
//     "¿A qué edad dejaste de exponerte?". Ya no existe
//     "Años con humo de leña, aprox.".
// Errores en el cliente: el campo lleva aria-invalid="true" y su
//   aria-describedby apunta a un elemento con el mensaje exacto. Al salir del
//   campo el error aparece sin mover el foco; al tocar "Guardar" el foco va al
//   primer error. Mensajes: "La edad no puede ser mayor que tu edad actual";
//   "No puede ser mayor que la edad en que lo dejaste" (en la edad de inicio);
//   "Debe estar entre {min} y {max}" (escala del esquema generado);
//   "No puede ser mayor que la edad en que terminó" (leña); "Escribe solo el
//   número.". Al elegir una opción se borran solo los errores de las
//   preguntas que se ocultan; un campo que sigue a la vista conserva su marca.
//
// perfil-habitos-completitud (openspec/changes/perfil-habitos-completitud/
// design.md → Interface contract → Frontend; C-15…C-17):
// Introducción: "Contesta los hábitos que quieras. Si eliges una respuesta,
//   completa sus preguntas; si no recuerdas un dato del pasado, marca «No
//   recuerdo». «Nunca» también le sirve a tu médico. La app no califica tus
//   respuestas."
// "No recuerdo": un chip (botón con aria-pressed) debajo de cada número que
//   lo admite: las edades siempre; "Cigarros al día" y "¿Cuántas horas al
//   día, en promedio?" solo con "Antes". Nombre accesible
//   "No recuerdo: <label del número>". Marcarlo vacía el número y quita su
//   error; escribir en el número lo desmarca. Cuenta como cambio sin guardar
//   y, mientras guarda, aria-disabled="true" (D20). Se guarda "unknown".
// Obligatorias (al tocar "Guardar", no al salir del campo): lo que abre una
//   respuesta se contesta; si falta, "Contesta esta pregunta." o, donde admite
//   "No recuerdo", "Contesta esta pregunta o marca «No recuerdo».". El error
//   va junto a su pregunta (el número, o la descripción accesible del grupo
//   de chips), el foco al primero y no sale ningún PUT. Al ocultarse la
//   pregunta se va su error. Lo guardado a medias abre sin errores.
// C-17: con un error ya marcado en un número, cada cambio lo revisa y quita
//   mensaje y aria-invalid si el valor es válido o el campo quedó vacío;
//   mientras se escribe no aparece un error nuevo (los de formato siguen al
//   salir del campo, C-14).
// ---------------------------------------------------------------------------

const API = `${process.env.VITE_API_URL}/api/v1`
const HABITS_URL = /\/perfil\/habitos\/?$/
const PROFILE_URL = /\/perfil\/?$/

const ALCOHOL = "Alcohol"
const FREQUENCY = "¿Con qué frecuencia tomas?"
const DRINKS = "En un día que tomas, ¿cuántas bebidas?"
const SIX_OR_MORE = "¿Cada cuándo tomas 6 o más bebidas en una sola ocasión?"
const WEEKENDS = "Sobre todo fines de semana"
const ALCOHOL_START = "¿A qué edad empezaste a tomar?"
const ALCOHOL_QUIT_AGE = "¿A qué edad dejaste de tomar?"
const TOBACCO = "Tabaco"
const CIGARETTES = "Cigarros al día"
const TOBACCO_START = "¿A qué edad empezaste a fumar?"
const TOBACCO_QUIT = "¿A qué edad dejaste de fumar?"
const VAPING = "Vapeador o cigarro electrónico"
const VAPING_FREQUENCY = "¿Con qué frecuencia vapeas?"
const VAPING_START = "¿A qué edad empezaste a vapear?"
const VAPING_QUIT = "¿A qué edad dejaste de vapear?"
const VAPING_DAYS = "¿Cuántos días de los últimos 30?"
const WHERE = "¿Dónde?"
const DAYS = "Días por semana"
const WOOD = "Humo de leña"
const WOOD_START = "¿A qué edad empezaste a exponerte?"
const WOOD_QUIT = "¿A qué edad dejaste de exponerte?"
const WOOD_HOURS = "¿Cuántas horas al día, en promedio?"
/** Pregunta de la C1 que este cambio quita. */
const OLD_WOOD_YEARS = "Años con humo de leña, aprox."

const SAVE_HINT = "Tus respuestas se guardan cuando tocas «Guardar»."
const INTRO =
  "Contesta los hábitos que quieras. Si eliges una respuesta, completa sus preguntas; si no recuerdas un dato del pasado, marca «No recuerdo». «Nunca» también le sirve a tu médico. La app no califica tus respuestas."
/** Falta una pregunta que no admite "No recuerdo" (C-15). */
const MISSING = "Contesta esta pregunta."
/** Falta una pregunta que admite "No recuerdo" (C-15). */
const MISSING_OR_UNKNOWN = "Contesta esta pregunta o marca «No recuerdo»."
const LEAVE_TITLE = "¿Salir sin guardar?"
const LEAVE_TEXT = "Los cambios que hiciste en Hábitos se van a perder."

/** El botón "Guardar", que mientras guarda dice "Guardando…" (R2-5). */
const SAVE_BUTTON = /^Guardar$|Guardando…/

/** Margen para afirmar que NO salió un PUT (ni un aviso que no debe salir). */
const NO_PUT_WINDOW_MS = 1500

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

/**
 * Sin keep-alive: el backend cierra las conexiones inactivas a los 5 s y un
 * test que espera a la UI más que eso reusaría un socket a medio cerrar
 * ("socket hang up"). Con "Connection: close" cada llamada abre el suyo.
 */
const NO_KEEP_ALIVE = { Connection: "close" }

/** Cliente del API autenticado como ese paciente. */
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

async function emailOf(api: Api): Promise<string> {
  const res = await api.request.get(`${API}/users/me`, {
    headers: api.headers,
  })
  expect(res.ok()).toBeTruthy()
  return (await res.json()).email
}

/** Otro paciente con el consentimiento ya dado (por API): entra directo a la app. */
async function consentedPatient(request: APIRequestContext) {
  const user = { email: randomEmail(), password: randomPassword() }
  await createUser(user)
  const api = await apiSession(request, user.email, user.password)
  const text = await request.get(`${API}/consent/text`, {
    headers: api.headers,
  })
  const consent = await request.post(`${API}/consent/`, {
    headers: api.headers,
    data: { version: (await text.json()).version },
  })
  expect(consent.ok()).toBeTruthy()
  return { ...user, api }
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
 * Marca los avisos ya visibles para verificar después solo el NUEVO: el de un
 * guardado anterior puede seguir en pantalla (~4 s, y sonner lo pausa
 * mientras el puntero está encima) (review R4).
 */
async function markShownToasts(page: Page) {
  await page.locator("[data-sonner-toast]").evaluateAll((shown) => {
    for (const toast of shown) toast.setAttribute("data-seen", "")
  })
}

function newToast(page: Page, text: string): Locator {
  return page
    .locator("[data-sonner-toast]:not([data-seen])")
    .filter({ hasText: text })
}

/** "Guardar" con éxito: aviso "Hábitos guardados" y de vuelta en /perfil. */
async function saveOk(page: Page) {
  await markShownToasts(page)
  await page.getByRole("button", { name: "Guardar", exact: true }).click()
  await expect(newToast(page, "Hábitos guardados")).toBeVisible()
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
 * Error junto a su campo: aria-invalid y aria-describedby apunta a un
 * elemento con el mensaje exacto. `focused: true` (al tocar "Guardar") exige
 * el foco en el campo; `false` (al salir del campo) exige que el error NO se
 * haya llevado el foco de vuelta; `"any"` no mira el foco.
 */
async function expectFieldError(
  page: Page,
  field: Locator,
  message: string,
  { focused = true }: { focused?: boolean | "any" } = {},
) {
  await expect(field).toHaveAttribute("aria-invalid", "true")
  if (focused === true) await expect(field).toBeFocused()
  else if (focused === false) await expect(field).not.toBeFocused()
  await expect
    .poll(async () => {
      const describedBy = (await field.getAttribute("aria-describedby")) ?? ""
      const texts: string[] = []
      for (const id of describedBy.split(/\s+/).filter(Boolean)) {
        const el = page.locator(`[id="${id}"]`)
        if ((await el.count()) > 0) {
          texts.push(((await el.first().textContent()) ?? "").trim())
        }
      }
      return texts
    })
    .toContain(message)
}

/** El chip "No recuerdo" del número `label` (C-16). */
function dontRemember(page: Page, label: string): Locator {
  return page.getByRole("button", {
    name: `No recuerdo: ${label}`,
    exact: true,
  })
}

/** Ningún error a la vista junto a `field` con ese mensaje (C-17). */
async function expectNoFieldError(page: Page, field: Locator, message: string) {
  await expect(field).not.toHaveAttribute("aria-invalid", "true")
  await expect(page.getByText(message, { exact: true })).toHaveCount(0)
}

/**
 * Error de una pregunta de chips (C-15): el mensaje es parte de la
 * descripción accesible de su grupo (junto a la ayuda que ya tuviera).
 */
async function expectGroupError(page: Page, name: string, message: string) {
  const escaped = message.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  await expect(group(page, name)).toHaveAccessibleDescription(
    new RegExp(`(^|\\s)${escaped}(\\s|$)`),
  )
}

/** Que no salga ningún PUT /profile/habits en la ventana de espera. */
async function expectNoPut(page: Page, puts: unknown[]) {
  await page.waitForTimeout(NO_PUT_WINDOW_MS)
  expect(puts).toEqual([])
}

/** El diálogo de la app al salir con cambios sin guardar. */
function leaveDialog(page: Page): Locator {
  return page.getByRole("dialog", { name: LEAVE_TITLE })
}

/** Ningún diálogo de salida de la app a la vista. */
async function expectNoLeaveDialog(page: Page) {
  await expect(page.getByText(LEAVE_TITLE)).toHaveCount(0)
}

/**
 * El enlace "‹ Mi perfil médico" de la pantalla (no la entrada del menú, que
 * se llama exactamente "Mi perfil médico" y no lleva "‹").
 */
function backLink(page: Page): Locator {
  return page
    .getByRole("link", { name: /Mi perfil médico/ })
    .filter({ hasText: "‹" })
}

/**
 * Tipos de los diálogos del navegador (beforeunload, alert…) que la página
 * abre desde ahora; cada uno se acepta para que la navegación siga.
 */
function trackBrowserDialogs(page: Page): string[] {
  const types: string[] = []
  page.on("dialog", async (dialog) => {
    types.push(dialog.type())
    await dialog.accept()
  })
  return types
}

/** Cuerpos de cada PUT /profile/habits que la página manda desde ahora. */
function trackHabitPuts(page: Page): unknown[] {
  const bodies: unknown[] = []
  page.on("request", (req) => {
    if (
      req.method() === "PUT" &&
      new URL(req.url()).pathname.endsWith("/profile/habits")
    ) {
      let body: unknown = null
      try {
        body = req.postDataJSON()
      } catch {
        body = req.postData()
      }
      bodies.push(body)
    }
  })
  return bodies
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

/**
 * Vuelve a "Mi perfil médico" por la entrada de la navegación (exact: el
 * enlace "‹ Mi perfil médico" de la pantalla es otro camino), sin "Guardar".
 */
async function backToProfileViaMenu(page: Page) {
  const perfilLink = page.getByRole("link", {
    name: "Mi perfil médico",
    exact: true,
  })
  await revealInSidebar(page, perfilLink)
  await perfilLink.click()
  await page.waitForURL(PROFILE_URL)
}

/** Login por el formulario de /login ya abierto, sin recargar la página. */
async function inAppLogin(page: Page, email: string, password: string) {
  await page.getByTestId("email-input").fill(email)
  await page.getByTestId("password-input").fill(password)
  await page.getByRole("button", { name: "Iniciar sesión" }).click()
  await page.waitForURL((url) => new URL(url).pathname === "/")
}

/**
 * Retiene el primer PUT /profile/habits; los demás pasan. `releaseAndWait`
 * lo suelta y devuelve su respuesta (ese PUT termina en el servidor).
 */
async function holdFirstHabitsPut(page: Page) {
  let release = () => {}
  const held = new Promise<void>((resolve) => {
    release = resolve
  })
  let routed = 0
  await page.route("**/api/v1/profile/habits", async (route) => {
    if (route.request().method() === "PUT" && routed++ === 0) await held
    await route.continue()
  })
  return {
    async releaseAndWait() {
      const response = page.waitForResponse(
        (res) =>
          new URL(res.url()).pathname.endsWith("/profile/habits") &&
          res.request().method() === "PUT",
      )
      release()
      return response
    },
  }
}

/**
 * Retiene el primer PUT /profile/habits SIN mandarlo al servidor; los demás
 * pasan. `respondAndWait(status)` lo contesta con ese estado (servidor
 * simulado: un 500 o un 401 que la UI no puede provocar) y devuelve la
 * respuesta que vio la página.
 */
async function holdFirstHabitsPutToFulfill(page: Page) {
  let respond: (status: number) => void = () => {}
  const answer = new Promise<number>((resolve) => {
    respond = resolve
  })
  let routed = 0
  await page.route("**/api/v1/profile/habits", async (route) => {
    if (route.request().method() !== "PUT" || routed++ > 0) {
      await route.continue()
      return
    }
    const status = await answer
    await route.fulfill({
      status,
      headers: {
        "access-control-allow-origin": route.request().headers().origin ?? "*",
      },
      json: {
        detail:
          status === 401 ? "Could not validate credentials" : "Internal error",
      },
    })
  })
  return {
    async respondAndWait(status: number) {
      const response = page.waitForResponse(
        (res) =>
          new URL(res.url()).pathname.endsWith("/profile/habits") &&
          res.request().method() === "PUT",
      )
      respond(status)
      return response
    },
  }
}

/** Un aviso de error (toast.error de sonner) que no estaba ya a la vista. */
function newErrorToast(page: Page): Locator {
  return page.locator('[data-sonner-toast][data-type="error"]:not([data-seen])')
}

/** Veces que fila 31b repite la carrera del 401 (R4-1 fallaba ~30 %). */
const RACE_RUNS = 5

/** Errores de envío fuera de los campos (el pie del formulario). */
const formAlert = (page: Page) => page.locator("form").getByRole("alert")

test.describe("Perfil médico — hábitos (perfil-habitos, grupo 2)", () => {
  test("fila 1 (C-1) alcohol actual desde los 18 con las preguntas del AUDIT-C: con 'Guardar', tarjeta 'Con datos' y al reabrir ve 18 y siguen elegidas", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Actual").click()
    await expect(numberField(page, ALCOHOL_START)).toBeVisible()
    await expect(page.getByText("Sin contar probaditas.")).toBeVisible()
    await numberField(page, ALCOHOL_START).fill("18")
    await chip(page, FREQUENCY, "2 a 3 veces por semana").click()
    await chip(page, DRINKS, "3 o 4").click()
    await chip(page, SIX_OR_MORE, "Cada mes").click()
    await chip(page, WEEKENDS, "Sí").click()
    await saveOk(page)

    await expect(card(page)).toContainText("Con datos")

    await reopen(page)
    await expectPressed(chip(page, ALCOHOL, "Actual"), true)
    await expect(numberField(page, ALCOHOL_START)).toHaveValue("18")
    await expectPressed(chip(page, FREQUENCY, "2 a 3 veces por semana"), true)
    await expectPressed(chip(page, DRINKS, "3 o 4"), true)
    await expectPressed(chip(page, SIX_OR_MORE, "Cada mes"), true)
    await expectPressed(chip(page, WEEKENDS, "Sí"), true)
  })

  test("fila 2 (C-1, C-10) lo dejó, de los 17 a los 30: al reabrir 'Lo dejé' con 17 y 30 y ninguna pregunta del AUDIT-C", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Lo dejé").click()
    await expect(page.getByText("Sin contar probaditas.")).toBeVisible()
    await numberField(page, ALCOHOL_START).fill("17")
    await numberField(page, ALCOHOL_QUIT_AGE).fill("30")
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, ALCOHOL, "Lo dejé"), true)
    await expect(numberField(page, ALCOHOL_START)).toHaveValue("17")
    await expect(numberField(page, ALCOHOL_QUIT_AGE)).toHaveValue("30")
    await expect(page.getByRole("group", { name: FREQUENCY })).toHaveCount(0)
    await expect(page.getByRole("group", { name: DRINKS })).toHaveCount(0)
    await expect(page.getByRole("group", { name: SIX_OR_MORE })).toHaveCount(0)
    await expect(page.getByRole("group", { name: WEEKENDS })).toHaveCount(0)

    const saved = await getHabits(api)
    expect(saved.alcohol?.start_age).toBe(17)
    expect(saved.alcohol?.quit_age).toBe(30)
  })

  test("fila 3 (C-10) alcohol: empezó a los 30 y lo dejó a los 18: al salir del campo, error junto a la edad de inicio y nada guardado", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, {
      alcohol: { status: "quit", start_age: 17, quit_age: 30 },
    })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, ALCOHOL, "Lo dejé"), true)
    const puts = trackHabitPuts(page)

    const start = numberField(page, ALCOHOL_START)
    await expect(start).toHaveValue("17")
    await start.fill("30")
    await numberField(page, ALCOHOL_QUIT_AGE).fill("18")
    await numberField(page, ALCOHOL_QUIT_AGE).press("Tab")

    await expectFieldError(
      page,
      start,
      "No puede ser mayor que la edad en que lo dejaste",
      { focused: false },
    )
    const putsAtError = puts.length
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts.length).toBe(putsAtError)
    for (const body of puts) {
      expect(
        (body as { alcohol?: { quit_age?: unknown } })?.alcohol?.quit_age ??
          null,
      ).not.toBe(18)
    }
    await expect(page).toHaveURL(HABITS_URL)
    const saved = await getHabits(api)
    expect(saved.alcohol?.status).toBe("quit")
    expect(saved.alcohol?.start_age).toBe(17)
    expect(saved.alcohol?.quit_age).toBe(30)
  })

  test("fila 4 (C-1, C-2) una edad mayor que la actual: empezó a los 17 y lo dejó a los 40 con 36 años, error junto al campo con el foco y nada guardado", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Lo dejé").click()
    await numberField(page, ALCOHOL_START).fill("17")
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
    expect(saved.alcohol?.quit_age ?? null).toBeNull()
  })

  test("fila 5 (C-1) lo que no aplica se descarta: de 'Actual' con edad y AUDIT-C a 'Nunca', sin edad ni preguntas al reabrir ni en lo guardado", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, {
      alcohol: {
        status: "current",
        start_age: 18,
        frequency: "two_to_three_weekly",
        typical_drinks: "three_four",
        six_or_more: "monthly",
        mostly_weekends: true,
      },
    })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, ALCOHOL, "Actual"), true)
    await expect(numberField(page, ALCOHOL_START)).toHaveValue("18")
    await expectPressed(chip(page, FREQUENCY, "2 a 3 veces por semana"), true)

    await chip(page, ALCOHOL, "Nunca").click()
    await expect(numberField(page, ALCOHOL_START)).toHaveCount(0)
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, ALCOHOL, "Nunca"), true)
    await expect(numberField(page, ALCOHOL_START)).toHaveCount(0)
    await expect(page.getByRole("group", { name: FREQUENCY })).toHaveCount(0)
    await expect(page.getByRole("group", { name: DRINKS })).toHaveCount(0)
    await expect(page.getByRole("group", { name: SIX_OR_MORE })).toHaveCount(0)

    const saved = await getHabits(api)
    expect(saved.alcohol?.status).toBe("never")
    expect(saved.alcohol?.start_age ?? null).toBeNull()
    expect(saved.alcohol?.frequency ?? null).toBeNull()
    expect(saved.alcohol?.typical_drinks ?? null).toBeNull()
    expect(saved.alcohol?.six_or_more ?? null).toBeNull()
    expect(saved.alcohol?.mostly_weekends ?? null).toBeNull()
  })

  test("fila 6 (C-2) tabaco que dejó (10 al día, de 18 a 30) y vapeador actual desde los 30 'Todos los días': al reabrir ve esas respuestas", async ({
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
    await numberField(page, VAPING_START).fill("30")
    await expect(group(page, VAPING_FREQUENCY)).toBeVisible()
    await chip(page, VAPING_FREQUENCY, "Todos los días").click()
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, TOBACCO, "Antes"), true)
    await expect(numberField(page, CIGARETTES)).toHaveValue("10")
    await expect(numberField(page, TOBACCO_START)).toHaveValue("18")
    await expect(numberField(page, TOBACCO_QUIT)).toHaveValue("30")
    await expectPressed(chip(page, VAPING, "Actual"), true)
    await expect(numberField(page, VAPING_START)).toHaveValue("30")
    await expectPressed(chip(page, VAPING_FREQUENCY, "Todos los días"), true)
    await expect(numberField(page, VAPING_DAYS)).toHaveCount(0)

    const saved = await getHabits(api)
    expect(saved.vaping?.status).toBe("current")
    expect(saved.vaping?.start_age).toBe(30)
    expect(saved.vaping?.frequency).toBe("daily")
  })

  test("fila 7 (C-2) 10 al día, empezó a los 30 y lo dejó a los 18: error junto a la edad de inicio y nada guardado", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, TOBACCO, "Antes").click()
    await numberField(page, CIGARETTES).fill("10")
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
    expect(saved.tobacco?.quit_age ?? null).toBeNull()
  })

  test("fila 8 (C-11) vapeador actual algunos días: desde los 25, 12 de los últimos 30; al reabrir ve 'Actual', 25, 'Algunos días' y 12", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, VAPING, "Actual").click()
    await expect(numberField(page, VAPING_START)).toBeVisible()
    await expect(numberField(page, VAPING_QUIT)).toHaveCount(0)
    await expect(group(page, VAPING_FREQUENCY)).toBeVisible()
    await expect(numberField(page, VAPING_DAYS)).toHaveCount(0)

    await numberField(page, VAPING_START).fill("25")
    await chip(page, VAPING_FREQUENCY, "Algunos días").click()
    await expect(numberField(page, VAPING_DAYS)).toBeVisible()
    await numberField(page, VAPING_DAYS).fill("12")
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, VAPING, "Actual"), true)
    await expect(numberField(page, VAPING_START)).toHaveValue("25")
    await expectPressed(chip(page, VAPING_FREQUENCY, "Algunos días"), true)
    await expectPressed(chip(page, VAPING_FREQUENCY, "Todos los días"), false)
    await expect(numberField(page, VAPING_DAYS)).toHaveValue("12")

    const saved = await getHabits(api)
    expect(saved.vaping).toMatchObject({
      status: "current",
      start_age: 25,
      frequency: "some_days",
      days_last_30: 12,
    })
  })

  test("fila 9 (C-11) de 'Algunos días' a 'Todos los días' se va la pregunta de días; luego 'Antes' de 25 a 28, sin frecuencia ni días al reabrir", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await seedHabits(api, {
      vaping: {
        status: "current",
        start_age: 25,
        frequency: "some_days",
        days_last_30: 12,
      },
    })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, VAPING_FREQUENCY, "Algunos días"), true)
    await expect(numberField(page, VAPING_DAYS)).toHaveValue("12")

    await chip(page, VAPING_FREQUENCY, "Todos los días").click()
    await expect(numberField(page, VAPING_DAYS)).toHaveCount(0)

    await chip(page, VAPING, "Antes").click()
    await expect(
      page.getByRole("group", { name: VAPING_FREQUENCY }),
    ).toHaveCount(0)
    await numberField(page, VAPING_START).fill("25")
    await numberField(page, VAPING_QUIT).fill("28")
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, VAPING, "Antes"), true)
    await expect(numberField(page, VAPING_START)).toHaveValue("25")
    await expect(numberField(page, VAPING_QUIT)).toHaveValue("28")
    await expect(
      page.getByRole("group", { name: VAPING_FREQUENCY }),
    ).toHaveCount(0)
    await expect(numberField(page, VAPING_DAYS)).toHaveCount(0)

    const saved = await getHabits(api)
    expect(saved.vaping?.status).toBe("former")
    expect(saved.vaping?.start_age).toBe(25)
    expect(saved.vaping?.quit_age).toBe(28)
    expect(saved.vaping?.frequency ?? null).toBeNull()
    expect(saved.vaping?.days_last_30 ?? null).toBeNull()
  })

  test("fila 10 (C-3) humo ajeno en casa y trabajo con 2 días, y después 'No me expongo' apaga los lugares y oculta los días", async ({
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

  test("fila 11 (C-4, C-12) humo de leña de antes, de los 5 a los 20 con 3 horas al día: al reabrir lo ve, sin cálculo con esos datos", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, WOOD, "Antes").click()
    await expect(numberField(page, OLD_WOOD_YEARS)).toHaveCount(0)
    await numberField(page, WOOD_START).fill("5")
    await numberField(page, WOOD_QUIT).fill("20")
    await numberField(page, WOOD_HOURS).fill("3")
    await saveOk(page)

    await reopen(page)
    await expectPressed(chip(page, WOOD, "Antes"), true)
    await expect(numberField(page, WOOD_START)).toHaveValue("5")
    await expect(numberField(page, WOOD_QUIT)).toHaveValue("20")
    await expect(numberField(page, WOOD_HOURS)).toHaveValue("3")
    await expect(numberField(page, OLD_WOOD_YEARS)).toHaveCount(0)
    expect(await page.locator("body").innerText()).not.toMatch(
      /horas-año|riesgo|puntaje/i,
    )

    const saved = await getHabits(api)
    expect(saved.wood_smoke).toMatchObject({
      status: "former",
      start_age: 5,
      quit_age: 20,
      hours_per_day: 3,
    })
  })

  test("fila 12 contesta solo vapeador 'Nunca': tarjeta 'Con datos' y lo demás sigue sin contestar", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, VAPING, "Nunca").click()
    await expect(numberField(page, VAPING_START)).toHaveCount(0)
    await expect(
      page.getByRole("group", { name: VAPING_FREQUENCY }),
    ).toHaveCount(0)
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
    expect(saved.vaping?.status).toBe("never")
    expect(saved.vaping?.frequency ?? null).toBeNull()
    expect(saved.vaping?.days_last_30 ?? null).toBeNull()
    expect(saved.vaping?.start_age ?? null).toBeNull()
    expect(saved.vaping?.quit_age ?? null).toBeNull()
    expect(saved.alcohol ?? null).toBeNull()
    expect(saved.tobacco ?? null).toBeNull()
    expect(saved.secondhand_smoke ?? null).toBeNull()
    expect(saved.wood_smoke ?? null).toBeNull()
  })

  test("fila 15 (C-6; completitud fila 10) sin puntaje ni riesgo: tras guardar el caso extremo (alcohol actual desde los 15 con el AUDIT-C al máximo y 'No' en fines de semana, tabaco actual 20 al día desde 'No recuerdo', leña actual desde los 5, 8 horas), ni la pantalla ni 'Mi perfil médico' ni la respuesta dicen 'riesgo', 'puntaje', 'AUDIT' u 'horas-año'", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Actual").click()
    await numberField(page, ALCOHOL_START).fill("15")
    await chip(page, FREQUENCY, "4 o más veces por semana").click()
    await chip(page, DRINKS, "10 o más").click()
    await chip(page, SIX_OR_MORE, "A diario o casi").click()
    await chip(page, WEEKENDS, "No").click()
    await chip(page, TOBACCO, "Actual").click()
    await numberField(page, CIGARETTES).fill("20")
    await dontRemember(page, TOBACCO_START).click()
    await expectPressed(dontRemember(page, TOBACCO_START), true)
    await chip(page, WOOD, "Actual").click()
    await expect(numberField(page, WOOD_START)).toBeVisible()
    await numberField(page, WOOD_START).fill("5")
    await numberField(page, WOOD_HOURS).fill("8")
    await saveOk(page)

    const forbidden = /riesgo|puntaje|audit|horas-año/i
    await expect(card(page)).toContainText("Con datos")
    expect(await page.locator("body").innerText()).not.toMatch(forbidden)

    await reopen(page)
    await expectPressed(chip(page, ALCOHOL, "Actual"), true)
    await expect(numberField(page, ALCOHOL_START)).toHaveValue("15")
    await expectPressed(chip(page, DRINKS, "10 o más"), true)
    await expectPressed(chip(page, WEEKENDS, "No"), true)
    await expect(numberField(page, CIGARETTES)).toHaveValue("20")
    await expectPressed(dontRemember(page, TOBACCO_START), true)
    await expect(numberField(page, TOBACCO_START)).toHaveValue("")
    await expectPressed(chip(page, WOOD, "Actual"), true)
    await expect(numberField(page, WOOD_START)).toHaveValue("5")
    await expect(numberField(page, WOOD_HOURS)).toHaveValue("8")
    expect(await page.locator("body").innerText()).not.toMatch(forbidden)

    const saved = await getHabits(api)
    expect(saved.tobacco?.start_age).toBe("unknown")
    expect(JSON.stringify(saved)).not.toMatch(forbidden)
  })

  test("fila 16 (C-13) se guarda al tocar 'Guardar': el texto lo dice; tabaco 'Nunca' no manda nada hasta 'Guardar', que manda un PUT, avisa 'Hábitos guardados', tarjeta 'Con datos' y al reabrir ve 'Nunca'", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)
    await expect(page.getByText(SAVE_HINT, { exact: true })).toBeVisible()
    const puts = trackHabitPuts(page)

    await chip(page, TOBACCO, "Nunca").click()
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts).toEqual([])
    expect((await getHabits(api)).tobacco ?? null).toBeNull()

    await saveOk(page)
    expect(puts).toHaveLength(1)
    await expect(card(page)).toContainText("Con datos")

    await reopen(page)
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)
    expect((await getHabits(api)).tobacco?.status).toBe("never")
  })

  test("fila 17 (C-13) aviso al salir con cambios sin guardar: de 'Nunca' a 'Actual' con 12 sin salir del campo, '‹ Mi perfil médico' → '¿Salir sin guardar?'; 'Seguir editando' deja 'Actual' y 12; atrás del navegador → diálogo; 'Salir sin guardar' → /perfil, ningún PUT, sigue 'Nunca'", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, { tobacco: { status: "never" } })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)
    const puts = trackHabitPuts(page)

    await chip(page, TOBACCO, "Actual").click()
    await numberField(page, CIGARETTES).fill("12")
    await backLink(page).click()

    const dialog = leaveDialog(page)
    await expect(dialog).toBeVisible()
    await expect(dialog).toContainText(LEAVE_TEXT)
    await expect(
      dialog.getByRole("button", { name: "Seguir editando", exact: true }),
    ).toBeFocused()
    await expect(
      dialog.getByRole("button", { name: "Salir sin guardar", exact: true }),
    ).toBeVisible()

    await dialog
      .getByRole("button", { name: "Seguir editando", exact: true })
      .click()
    await expect(dialog).toHaveCount(0)
    await expect(page).toHaveURL(HABITS_URL)
    await expectPressed(chip(page, TOBACCO, "Actual"), true)
    await expect(numberField(page, CIGARETTES)).toHaveValue("12")

    // Atrás del navegador (la entrada anterior es /perfil).
    await page.evaluate(() => window.history.back())
    await expect(dialog).toBeVisible()
    await dialog
      .getByRole("button", { name: "Salir sin guardar", exact: true })
      .click()
    await page.waitForURL(PROFILE_URL)

    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts).toEqual([])
    const saved = await getHabits(api)
    expect(saved.tobacco?.status).toBe("never")
    expect(saved.tobacco?.cigarettes_per_day ?? null).toBeNull()
    await reopen(page)
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)
  })

  test("fila 17b (C-13) 'Seguir editando' devuelve el foco adonde estaba: clic en '‹ Mi perfil médico' → 'Seguir editando' deja el foco en ese enlace; con el foco en 'Cigarros al día', atrás del navegador → Escape deja /perfil/habitos y el foco en ese campo con 12", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, { tobacco: { status: "never" } })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)

    await chip(page, TOBACCO, "Actual").click()
    const cigarettes = numberField(page, CIGARETTES)
    await cigarettes.fill("12")
    await expect(cigarettes).toBeFocused()

    // 1. Clic en el enlace: el enlace tiene el foco justo antes del diálogo.
    // (En Chromium, de escritorio y móvil, el clic enfoca el enlace.)
    await backLink(page).click()
    const dialog = leaveDialog(page)
    const keepEditing = dialog.getByRole("button", {
      name: "Seguir editando",
      exact: true,
    })
    await expect(dialog).toBeVisible()
    await expect(keepEditing).toBeFocused()
    await keepEditing.click()
    await expect(dialog).toHaveCount(0)
    await expect(page).toHaveURL(HABITS_URL)
    // Suave: si falla, la parte 2 también se comprueba en la misma corrida.
    await expect.soft(backLink(page)).toBeFocused()

    // 2. Foco en 'Cigarros al día' (recién escrito) y atrás del navegador.
    await cigarettes.fill("12")
    await expect(cigarettes).toBeFocused()
    await page.goBack()
    await expect(dialog).toBeVisible()
    await expect(keepEditing).toBeFocused()
    await page.keyboard.press("Escape")
    await expect(dialog).toHaveCount(0)
    await expect(page).toHaveURL(HABITS_URL)
    await expect(cigarettes).toHaveValue("12")
    await expect(cigarettes).toBeFocused()
  })

  test("fila 18 (C-13) sin cambios no hay aviso: abrir y volver sin tocar → sin diálogo; elegir 'Actual' y volver a 'Nunca' → sin diálogo (y nada enviado)", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, { tobacco: { status: "never" } })
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)

    // Por el menú, sin tocar nada.
    await backToProfileViaMenu(page)
    await expectNoLeaveDialog(page)

    await reopen(page)
    await chip(page, TOBACCO, "Actual").click()
    await expectPressed(chip(page, TOBACCO, "Actual"), true)
    await chip(page, TOBACCO, "Nunca").click()
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)
    await backLink(page).click()
    await page.waitForURL(PROFILE_URL)
    await expectNoLeaveDialog(page)

    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts).toEqual([])
    expect((await getHabits(api)).tobacco?.status).toBe("never")
  })

  test("fila 19 (C-13) aviso del navegador al recargar: con un cambio, recargar → diálogo 'beforeunload'; sin cambios, ninguno", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)
    const dialogs = trackBrowserDialogs(page)

    // Sin cambios (con un clic real en la página, que Chrome exige para
    // mostrar el aviso): recargar no pregunta.
    await page.getByRole("heading", { name: "Hábitos", exact: true }).click()
    await page.reload()
    await expect(
      page.getByRole("button", { name: "Guardar", exact: true }),
    ).toBeVisible()
    expect(dialogs).toEqual([])

    // Con un cambio sin guardar: recargar pide el aviso del navegador.
    await chip(page, TOBACCO, "Nunca").click()
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)
    await page.reload()
    await expect(
      page.getByRole("button", { name: "Guardar", exact: true }),
    ).toBeVisible()
    expect(dialogs).toContain("beforeunload")
  })

  test("fila 20 (C-13, N1) sin aviso cuando la sesión cambió: con un cambio, otra pestaña cierra sesión → esta llega a /login sin diálogo de la app ni 'beforeunload', ningún PUT", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)
    const dialogs = trackBrowserDialogs(page)

    await chip(page, TOBACCO, "Nunca").click()
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)

    // Pestaña 2 del mismo navegador (comparte localStorage): cierra sesión.
    const other = await page.context().newPage()
    await other.goto("/perfil")
    const otherMenu = other.getByTestId("user-menu")
    await revealInSidebar(other, otherMenu)
    await otherMenu.click()
    await other.getByRole("menuitem", { name: "Cerrar sesión" }).click()
    await other.waitForURL(/\/login/)

    await expect(page).toHaveURL(/\/login/)
    await expectNoLeaveDialog(page)
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(dialogs).toEqual([])
    expect(puts).toEqual([])
    expect((await getHabits(api)).tobacco ?? null).toBeNull()
  })

  test("fila 21 (C-13, D20; R2-5) no disponibles mientras guarda: con el PUT retenido, 'Guardar' (que dice 'Guardando…') y 'Cancelar' con aria-disabled, el foco sigue en 'Guardar'; Enter y otro clic → un solo PUT; al soltarlo, /perfil", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)

    // El primer PUT se retiene hasta soltarlo; los demás pasan.
    let release = () => {}
    const held = new Promise<void>((resolve) => {
      release = resolve
    })
    let routed = 0
    await page.route("**/api/v1/profile/habits", async (route) => {
      if (route.request().method() === "PUT" && routed++ === 0) await held
      await route.continue()
    })

    // Mientras guarda, el botón "Guardar" dice "Guardando…" (R2-5): el
    // localizador acepta los dos nombres.
    const save = page.getByRole("button", { name: SAVE_BUTTON })
    const cancel = page.getByRole("button", { name: "Cancelar", exact: true })

    await chip(page, VAPING, "Nunca").click()
    await markShownToasts(page)
    await save.click()

    await expect(save).toHaveAccessibleName(/Guardando…/)
    await expect(save).toHaveAttribute("aria-disabled", "true")
    await expect(cancel).toHaveAttribute("aria-disabled", "true")
    // aria-disabled, no disabled nativo: no pierde el foco.
    await expect(save).not.toHaveAttribute("disabled")
    await expect(cancel).not.toHaveAttribute("disabled")
    await expect(save).toBeFocused()
    expect(puts).toHaveLength(1)

    // Mientras sigue en curso: Enter y otro clic en "Guardar", y "Cancelar",
    // no hacen nada.
    await page.keyboard.press("Enter")
    await expect(save).toBeFocused()
    await save.click({ force: true })
    await expect(save).toBeFocused()
    await cancel.click({ force: true })
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    await expect(page).toHaveURL(HABITS_URL)
    expect(puts).toHaveLength(1)

    release()
    await page.waitForURL(PROFILE_URL)
    await expect(newToast(page, "Hábitos guardados")).toBeVisible()
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts).toHaveLength(1)
    expect((await getHabits(api)).vaping?.status).toBe("never")
  })

  test("fila 22 (C-13) 'Cancelar' descarta: de tabaco 'Nunca' a 'Actual' con 5, 'Cancelar' → /perfil con 'Se descartaron los cambios', sin diálogo, ningún PUT y sigue 'Nunca'; sin cambios, 'Cancelar' vuelve sin ese aviso", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, { tobacco: { status: "never" } })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)
    const puts = trackHabitPuts(page)

    await chip(page, TOBACCO, "Actual").click()
    await numberField(page, CIGARETTES).fill("5")
    await markShownToasts(page)
    await page.getByRole("button", { name: "Cancelar", exact: true }).click()
    await page.waitForURL(PROFILE_URL)
    await expect(newToast(page, "Se descartaron los cambios")).toBeVisible()
    await expectNoLeaveDialog(page)

    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts).toEqual([])
    const saved = await getHabits(api)
    expect(saved.tobacco?.status).toBe("never")
    expect(saved.tobacco?.cigarettes_per_day ?? null).toBeNull()

    await reopen(page)
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)
    await expect(numberField(page, CIGARETTES)).toHaveCount(0)

    // Sin cambios: vuelve, sin el aviso.
    await markShownToasts(page)
    await page.getByRole("button", { name: "Cancelar", exact: true }).click()
    await page.waitForURL(PROFILE_URL)
    await expectNoLeaveDialog(page)
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    await expect(newToast(page, "Se descartaron los cambios")).toHaveCount(0)
    expect(puts).toEqual([])
  })

  test("fila 23 (C-14) errores al salir del campo, sin ningún PUT: 25 horas de leña ('Debe estar entre 1 y 24'), 40 en una edad con 36 años, inicio 30 y fin 18 en vapeador y en leña, y '12a' ('Escribe solo el número.')", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await seedHabits(api, {
      wood_smoke: { status: "current", start_age: 5, hours_per_day: 3 },
    })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, WOOD, "Actual"), true)
    // Con "Actual": edad de inicio y horas, sin edad de fin.
    await expect(numberField(page, WOOD_START)).toBeVisible()
    await expect(numberField(page, WOOD_QUIT)).toHaveCount(0)
    await expect(numberField(page, OLD_WOOD_YEARS)).toHaveCount(0)
    const puts = trackHabitPuts(page)

    // Fuera de escala.
    const hours = numberField(page, WOOD_HOURS)
    await hours.fill("25")
    await hours.press("Tab")
    await expectFieldError(page, hours, "Debe estar entre 1 y 24", {
      focused: false,
    })
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts).toEqual([])
    expect((await getHabits(api)).wood_smoke?.hours_per_day).toBe(3)

    // Una edad mayor que la actual (36).
    const woodStart = numberField(page, WOOD_START)
    await woodStart.fill("40")
    await woodStart.press("Tab")
    await expectFieldError(
      page,
      woodStart,
      "La edad no puede ser mayor que tu edad actual",
      { focused: false },
    )
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts).toEqual([])

    // Vapeador: empezó a los 30 y lo dejó a los 18.
    await chip(page, VAPING, "Antes").click()
    const vapingStart = numberField(page, VAPING_START)
    await vapingStart.fill("30")
    await numberField(page, VAPING_QUIT).fill("18")
    await numberField(page, VAPING_QUIT).press("Tab")
    await expectFieldError(
      page,
      vapingStart,
      "No puede ser mayor que la edad en que lo dejaste",
      { focused: false },
    )
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts).toEqual([])

    // Leña: empezó a los 30 y terminó a los 18.
    await chip(page, WOOD, "Antes").click()
    await woodStart.fill("30")
    await numberField(page, WOOD_QUIT).fill("18")
    await numberField(page, WOOD_QUIT).press("Tab")
    await expectFieldError(
      page,
      woodStart,
      "No puede ser mayor que la edad en que terminó",
      { focused: false },
    )
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts).toEqual([])

    // Algo que no es un número.
    await chip(page, TOBACCO, "Actual").click()
    const cigarettes = numberField(page, CIGARETTES)
    await cigarettes.fill("12a")
    await cigarettes.press("Tab")
    await expectFieldError(page, cigarettes, "Escribe solo el número.", {
      focused: false,
    })
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    expect(puts).toEqual([])

    const saved = await getHabits(api)
    expect(saved.wood_smoke?.status).toBe("current")
    expect(saved.vaping ?? null).toBeNull()
    expect(saved.tobacco ?? null).toBeNull()
  })

  test("fila 24 (C-14) la marca sigue mientras el campo está a la vista: tabaco 'Actual' con 101 cigarros y Tab → error; con 'Antes' el error y aria-invalid siguen junto a los cigarros", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, {
      tobacco: { status: "current", cigarettes_per_day: 12, start_age: 18 },
    })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, TOBACCO, "Actual"), true)

    const cigarettes = numberField(page, CIGARETTES)
    await cigarettes.fill("101")
    await cigarettes.press("Tab")
    await expectFieldError(page, cigarettes, "Debe estar entre 1 y 100", {
      focused: false,
    })

    await chip(page, TOBACCO, "Antes").click()
    await expectPressed(chip(page, TOBACCO, "Antes"), true)
    await expect(cigarettes).toBeVisible()
    await expect(cigarettes).toHaveValue("101")
    await expectFieldError(page, cigarettes, "Debe estar entre 1 y 100", {
      focused: false,
    })
  })

  test("fila 26 (C-13; R2-7) solo un número cambia: tabaco 'Actual' con 12 guardado, 20 en 'Cigarros al día' sin salir del campo ni tocar chips → '‹ Mi perfil médico' pregunta; 'Cancelar' avisa 'Se descartaron los cambios'; recargar pide 'beforeunload'", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, {
      tobacco: { status: "current", cigarettes_per_day: 12, start_age: 18 },
    })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, TOBACCO, "Actual"), true)
    const cigarettes = numberField(page, CIGARETTES)
    await expect(cigarettes).toHaveValue("12")

    // 1. "‹ Mi perfil médico" pregunta.
    await cigarettes.fill("20")
    await expect(cigarettes).toBeFocused()
    await backLink(page).click()
    const dialog = leaveDialog(page)
    await expect(dialog).toBeVisible()
    await dialog
      .getByRole("button", { name: "Salir sin guardar", exact: true })
      .click()
    await page.waitForURL(PROFILE_URL)

    // 2. "Cancelar" avisa que descartó.
    await reopen(page)
    await expect(cigarettes).toHaveValue("12")
    await cigarettes.fill("20")
    await expect(cigarettes).toBeFocused()
    await markShownToasts(page)
    await page.getByRole("button", { name: "Cancelar", exact: true }).click()
    await page.waitForURL(PROFILE_URL)
    await expect(newToast(page, "Se descartaron los cambios")).toBeVisible()

    // 3. Recargar pide el aviso del navegador.
    await reopen(page)
    await expect(cigarettes).toHaveValue("12")
    const dialogs = trackBrowserDialogs(page)
    await cigarettes.fill("20")
    await expect(cigarettes).toBeFocused()
    await page.reload()
    await expect(
      page.getByRole("button", { name: "Guardar", exact: true }),
    ).toBeVisible()
    expect(dialogs).toContain("beforeunload")
  })

  test("fila 27 (C-13; R2-1, R3-2) un guardado en camino no cruza de cuenta en la misma pestaña: A elige tabaco 'Actual' con 20 y 'Guardar' (PUT retenido); 'Cerrar sesión'; B entra por el formulario con su GET de hábitos demorado; al soltar el PUT de A, B no es llevado a /perfil ni ve 'Hábitos guardados'; con el GET de B todavía demorado, su tarjeta no dice 'Con datos' y su formulario no muestra 'Actual' ni 20; el GET de B sigue vacío", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    const b = await consentedPatient(request)
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)
    const hold = await holdFirstHabitsPut(page)

    // A: tabaco "Actual" con 20 y "Guardar", que queda en curso.
    await chip(page, TOBACCO, "Actual").click()
    await numberField(page, CIGARETTES).fill("20")
    await numberField(page, TOBACCO_START).fill("18")
    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    await expect.poll(() => puts.length).toBe(1)

    // A cierra sesión por el menú de usuario real.
    const userMenu = page.getByTestId("user-menu")
    await revealInSidebar(page, userMenu)
    await userMenu.click()
    await page.getByRole("menuitem", { name: "Cerrar sesión" }).click()
    await page.waitForURL(/\/login/)

    // Desde el login de B, cada GET de hábitos queda demorado hasta soltarlo
    // (los PUT siguen a la retención de arriba). Mientras está demorado, lo
    // único que la pantalla puede mostrar de "Hábitos" es lo que haya en su
    // caché: si escribiera ahí la respuesta del PUT de A, B la vería ahora.
    let releaseGet = () => {}
    const getHeld = new Promise<void>((resolve) => {
      releaseGet = resolve
    })
    let heldGets = 0
    await page.route("**/api/v1/profile/habits", async (route) => {
      if (route.request().method() !== "GET") {
        await route.fallback()
        return
      }
      heldGets++
      await getHeld
      await route.continue()
    })

    // B entra por el formulario de la misma pestaña.
    await inAppLogin(page, b.email, b.password)

    // Se suelta el PUT de A: termina, pero no le toca a B.
    await markShownToasts(page)
    const putResponse = await hold.releaseAndWait()
    expect(putResponse.status()).toBe(200)
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    await expect(page).not.toHaveURL(PROFILE_URL)
    await expect(page).not.toHaveURL(HABITS_URL)
    await expect(newToast(page, "Hábitos guardados")).toHaveCount(0)
    expect(puts).toHaveLength(1)

    // Con el GET de B todavía demorado, "Mi perfil médico" no dice "Con
    // datos" en la tarjeta "Hábitos": sin nada en la caché, la página espera
    // al GET; con la respuesta de A en la caché, saldría con "Con datos" (y
    // sin pedir nada). Por eso esta marca va antes de exigir el GET demorado.
    await backToProfileViaMenu(page)
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    await expect(card(page).filter({ hasText: "Con datos" })).toHaveCount(0)
    expect(heldGets).toBeGreaterThan(0)

    // Se suelta el GET de B: llegan sus hábitos, vacíos; ni la tarjeta ni el
    // formulario muestran lo de A.
    releaseGet()
    await expect(card(page)).toBeVisible()
    await expect(card(page)).not.toContainText("Con datos")
    await reopen(page)
    await expectPressed(chip(page, TOBACCO, "Actual"), false)
    await expect(numberField(page, CIGARETTES)).toHaveCount(0)
    expect((await getHabits(b.api)).tobacco ?? null).toBeNull()
  })

  test("fila 28 (C-13; R2-2, R2-3, R3-1, R3-4) mientras guarda no se cambia nada, y salir espera sin preguntar: con el PUT retenido, el chip 'Actual' de leña con aria-disabled, atenuado (opacidad < 1) y su clic no cambia nada; 'Cigarros al día' de solo lectura; el menú → 'Expediente': sin diálogo y la URL sigue en /perfil/habitos mientras el PUT está retenido; al soltarlo, /expediente con 'Hábitos guardados' y el GET trae lo guardado; reabrir 'Hábitos' muestra lo guardado", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)
    const hold = await holdFirstHabitsPut(page)

    await chip(page, TOBACCO, "Actual").click()
    const cigarettes = numberField(page, CIGARETTES)
    await cigarettes.fill("20")
    await numberField(page, TOBACCO_START).fill("18")
    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    await expect.poll(() => puts.length).toBe(1)

    // Las preguntas no aceptan cambios mientras guarda, y se ven atenuadas.
    const woodCurrent = chip(page, WOOD, "Actual")
    await expect(woodCurrent).toHaveAttribute("aria-disabled", "true")
    await expect
      .poll(() =>
        woodCurrent.evaluate((el) => Number(getComputedStyle(el).opacity)),
      )
      .toBeLessThan(1)
    await expectPressed(woodCurrent, false)
    await woodCurrent.click({ force: true })
    await page.waitForTimeout(300)
    await expectPressed(woodCurrent, false)
    await expect(numberField(page, WOOD_START)).toHaveCount(0)
    await expect(cigarettes).toBeVisible()
    await expect(cigarettes).not.toBeEditable()
    await expect(cigarettes).toHaveValue("20")

    // Al "Expediente" por la navegación de la app: sin pregunta, y la salida
    // espera al guardado (la URL no cambia mientras el PUT está retenido).
    const dialogs = trackBrowserDialogs(page)
    await markShownToasts(page)
    const expedienteLink = page.getByRole("link", {
      name: "Expediente",
      exact: true,
    })
    await revealInSidebar(page, expedienteLink)
    await expedienteLink.click()
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    await expectNoLeaveDialog(page)
    await expect(page).toHaveURL(HABITS_URL)

    // Al soltar el PUT: llega al "Expediente" (no a /perfil) con el aviso.
    const putResponse = await hold.releaseAndWait()
    expect(putResponse.status()).toBe(200)
    await page.waitForURL(/\/expediente/)
    await expect(newToast(page, "Hábitos guardados")).toBeVisible()
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    await expect(page).toHaveURL(/\/expediente/)
    await expectNoLeaveDialog(page)
    expect(dialogs).toEqual([])
    expect(puts).toHaveLength(1)
    const saved = await getHabits(api)
    expect(saved.tobacco?.status).toBe("current")
    expect(saved.tobacco?.cigarettes_per_day).toBe(20)
    expect(saved.wood_smoke ?? null).toBeNull()

    // Reabrir "Hábitos" desde la tarjeta (sin recargar) muestra lo guardado.
    await backToProfileViaMenu(page)
    await reopen(page)
    await expectPressed(chip(page, TOBACCO, "Actual"), true)
    await expect(numberField(page, CIGARETTES)).toHaveValue("20")
    await expectPressed(chip(page, WOOD, "Actual"), false)
  })

  test("fila 30 (C-13; R3-3) un rechazo al salir se queda a la vista: fecha de nacimiento cambiada por la API después de abrir; alcohol 'Lo dejé' con 40 → 'Guardar' (PUT retenido) → '‹ Mi perfil médico' → al soltar, 422: sigue en /perfil/habitos con 'La edad no puede ser mayor que tu edad actual' junto al campo; nada guardado", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)
    // Cargó sin fecha de nacimiento (como R9): solo el servidor rechaza 40
    // con 36 años.
    await setAge36(api)
    const puts = trackHabitPuts(page)
    const hold = await holdFirstHabitsPut(page)

    await chip(page, ALCOHOL, "Lo dejé").click()
    await numberField(page, ALCOHOL_START).fill("17")
    const quitAge = numberField(page, ALCOHOL_QUIT_AGE)
    await quitAge.fill("40")
    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    await expect.poll(() => puts.length).toBe(1)

    // Mientras guarda, intenta volver a "Mi perfil médico".
    await backLink(page).click()

    // El servidor lo rechaza: se queda en la pantalla con el error a la vista.
    const putResponse = await hold.releaseAndWait()
    expect(putResponse.status()).toBe(422)
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    await expect(page).toHaveURL(HABITS_URL)
    await expect(quitAge).toBeVisible()
    await expect(quitAge).toHaveValue("40")
    await expectFieldError(
      page,
      quitAge,
      "La edad no puede ser mayor que tu edad actual",
      { focused: "any" },
    )
    expect(puts).toHaveLength(1)
    const saved = await getHabits(api)
    expect(saved.alcohol ?? null).toBeNull()
  })

  test("fila 29 (C-13; R2-4) el foco vuelve al título si su elemento ya no existe: a 384 px, con un cambio, menú lateral → 'Mi perfil médico' → diálogo → 'Seguir editando' → foco en el título 'Hábitos'", async ({
    page,
    request,
  }) => {
    // El menú lateral del celular (s26-ultra): el mismo ancho en los dos
    // proyectos.
    await page.setViewportSize({ width: 384, height: 832 })
    await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, TOBACCO, "Nunca").click()
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)

    const perfilLink = page.getByRole("link", {
      name: "Mi perfil médico",
      exact: true,
    })
    await expect(perfilLink).toBeHidden()
    await page.getByRole("button", { name: /barra lateral/ }).click()
    await expect(perfilLink).toBeVisible()
    await perfilLink.click()

    const dialog = leaveDialog(page)
    await expect(dialog).toBeVisible()
    await dialog
      .getByRole("button", { name: "Seguir editando", exact: true })
      .click()
    await expect(dialog).toHaveCount(0)
    await expect(page).toHaveURL(HABITS_URL)
    await expectPressed(chip(page, TOBACCO, "Nunca"), true)
    await expect(
      page.getByRole("heading", { name: "Hábitos", exact: true }),
    ).toBeFocused()
  })

  test("fila 31a (C-13; R4-1, R4-3, R4-6) atrás del navegador mientras guarda y el guardado falla: tabaco 'Actual' con 20 → 'Guardar' (PUT retenido) → atrás del navegador → el PUT responde 500 → la URL vuelve a /perfil/habitos con el formulario y el aviso de error", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)
    const hold = await holdFirstHabitsPutToFulfill(page)

    await chip(page, TOBACCO, "Actual").click()
    const cigarettes = numberField(page, CIGARETTES)
    await cigarettes.fill("20")
    await numberField(page, TOBACCO_START).fill("18")
    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    await expect.poll(() => puts.length).toBe(1)

    // Atrás del navegador mientras el PUT sigue retenido: sin pregunta.
    const dialogs = trackBrowserDialogs(page)
    await markShownToasts(page)
    await page.goBack()
    await expectNoLeaveDialog(page)

    // El servidor falla: la salida se cancela y la pantalla sigue con el error.
    const putResponse = await hold.respondAndWait(500)
    expect(putResponse.status()).toBe(500)
    await expect(newErrorToast(page)).toBeVisible()
    await expect(page).toHaveURL(HABITS_URL)
    await expect(
      page.getByRole("heading", { name: "Hábitos", exact: true }),
    ).toBeVisible()
    await expectPressed(chip(page, TOBACCO, "Actual"), true)
    await expect(cigarettes).toHaveValue("20")
    await page.waitForTimeout(NO_PUT_WINDOW_MS)
    await expect(page).toHaveURL(HABITS_URL)
    await expect(
      page.getByRole("heading", { name: "Hábitos", exact: true }),
    ).toBeVisible()
    await expectNoLeaveDialog(page)
    expect(dialogs).toEqual([])
    expect(puts).toHaveLength(1)
  })

  test(`fila 31b (C-13; R4-1) atrás del navegador mientras guarda y la sesión terminó: el PUT responde 401 → llega a /login con recarga completa y sin token (${RACE_RUNS} intentos, cada uno en una página nueva)`, async ({
    context,
    request,
  }) => {
    test.setTimeout(150_000)
    for (let run = 1; run <= RACE_RUNS; run++) {
      await test.step(`intento ${run} de ${RACE_RUNS}`, async () => {
        const page = await context.newPage()
        const patient = await consentedPatient(request)
        await page.goto("/login")
        await inAppLogin(page, patient.email, patient.password)
        await openHabitsFromProfile(page)
        const puts = trackHabitPuts(page)
        const hold = await holdFirstHabitsPutToFulfill(page)

        await chip(page, TOBACCO, "Actual").click()
        await numberField(page, CIGARETTES).fill("20")
        await numberField(page, TOBACCO_START).fill("18")
        await page.getByRole("button", { name: "Guardar", exact: true }).click()
        await expect.poll(() => puts.length).toBe(1)

        // Marca del documento actual: una recarga completa la borra.
        await page.evaluate(() => {
          ;(window as unknown as Record<string, unknown>).__sameDocument = true
        })
        await page.goBack()

        // La sesión terminó durante la espera: manda el cierre de sesión.
        const putResponse = await hold.respondAndWait(401)
        expect(putResponse.status()).toBe(401)
        // Sondeo de la URL (no waitForURL): si la carga de /login se aborta,
        // el fallo dice dónde quedó la página.
        await expect(page).toHaveURL(/\/login/, { timeout: 10_000 })
        await expect
          .poll(() =>
            page.evaluate(
              () =>
                (window as unknown as Record<string, unknown>).__sameDocument ??
                null,
            ),
          )
          .toBeNull()
        await page.waitForTimeout(NO_PUT_WINDOW_MS)
        await expect(page).toHaveURL(/\/login/)
        await expect(page.getByTestId("email-input")).toBeVisible()
        expect(
          await page.evaluate(() => localStorage.getItem("access_token")),
        ).toBeNull()
        expect(puts).toHaveLength(1)
        await page.close()
      })
    }
  })

  test("fila 31c (C-13; R4-3) a 384 px, salir por el menú lateral mientras guarda y el guardado falla: 'Expediente' → el PUT responde 500 → el foco en el título 'Hábitos'", async ({
    page,
    request,
  }) => {
    // El menú lateral del celular (s26-ultra): el mismo ancho en los dos
    // proyectos.
    await page.setViewportSize({ width: 384, height: 832 })
    await freshPatient(page, request)
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)
    const hold = await holdFirstHabitsPutToFulfill(page)

    await chip(page, TOBACCO, "Actual").click()
    await numberField(page, CIGARETTES).fill("20")
    await numberField(page, TOBACCO_START).fill("18")
    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    await expect.poll(() => puts.length).toBe(1)

    // Sale por "Expediente" del menú lateral mientras el PUT está retenido.
    await markShownToasts(page)
    const expedienteLink = page.getByRole("link", {
      name: "Expediente",
      exact: true,
    })
    await expect(expedienteLink).toBeHidden()
    await page.getByRole("button", { name: /barra lateral/ }).click()
    await expect(expedienteLink).toBeVisible()
    await expedienteLink.click()
    await expectNoLeaveDialog(page)
    await expect(page).toHaveURL(HABITS_URL)

    // El servidor falla: la salida se cancela y el foco va al título.
    const putResponse = await hold.respondAndWait(500)
    expect(putResponse.status()).toBe(500)
    await expect(newErrorToast(page)).toBeVisible()
    await expect(page).toHaveURL(HABITS_URL)
    await expect(
      page.getByRole("heading", { name: "Hábitos", exact: true }),
    ).toBeFocused()
    expect(puts).toHaveLength(1)
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

  test("R1 otro paciente entra sin recargar tras 'Cerrar sesión': no ve ni guarda los hábitos del anterior, ni ve su correo (N2)", async ({
    page,
    request,
  }) => {
    const apiA = await freshPatient(page, request)
    await seedHabits(apiA, {
      tobacco: { status: "current", cigarettes_per_day: 20, start_age: 18 },
      vaping: { status: "current", start_age: 20, frequency: "daily" },
    })
    await openHabitsFromProfile(page)
    await expect(numberField(page, CIGARETTES)).toHaveValue("20")
    const aEmail = await emailOf(apiA)

    const b = await consentedPatient(request)
    const apiB = b.api

    // A cierra sesión desde el menú; B entra por el formulario sin recargar,
    // con su GET de hábitos retrasado 2 s y su /users/me detenido hasta mirar
    // el menú (lo que tarden no debe dejar ver nada de A: ni sus hábitos ni
    // su correo; revisión, ronda 2, N2).
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
    let releaseMe = () => {}
    const meHeld = new Promise<void>((resolve) => {
      releaseMe = resolve
    })
    await page.route("**/api/v1/users/me", async (route) => {
      await meHeld
      await route.continue()
    })
    await inAppLogin(page, b.email, b.password)

    const perfilLink = page.getByRole("link", { name: "Mi perfil médico" })
    await revealInSidebar(page, perfilLink)
    await expect(page.getByText(aEmail)).toHaveCount(0)
    releaseMe()
    await expect(userMenu).toContainText(b.email)
    await expect(page.getByText(aEmail)).toHaveCount(0)
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

  test("N1 (ronda 2) A cierra sesión y B entra en OTRA pestaña: la que tenía abiertos los hábitos de A ya no los muestra ni los puede guardar", async ({
    page,
    request,
  }) => {
    const apiA = await freshPatient(page, request)
    await seedHabits(apiA, {
      tobacco: { status: "current", cigarettes_per_day: 20, start_age: 18 },
      vaping: { status: "current", start_age: 20, frequency: "daily" },
    })
    await openHabitsFromProfile(page)
    await expect(numberField(page, CIGARETTES)).toHaveValue("20")
    const aEmail = await emailOf(apiA)
    const b = await consentedPatient(request)

    // Pestaña 2 del mismo navegador (comparte localStorage): A sale, B entra.
    const other = await page.context().newPage()
    await other.goto("/perfil")
    const otherMenu = other.getByTestId("user-menu")
    await revealInSidebar(other, otherMenu)
    await otherMenu.click()
    await other.getByRole("menuitem", { name: "Cerrar sesión" }).click()
    await other.waitForURL(/\/login/)
    await inAppLogin(other, b.email, b.password)

    // La pestaña 1 dejó el cuestionario de A: ni sus datos ni "Guardar".
    await expect(page).not.toHaveURL(HABITS_URL)
    await expect(numberField(page, CIGARETTES)).toHaveCount(0)
    await expect(
      page.getByRole("button", { name: "Guardar", exact: true }),
    ).toHaveCount(0)
    const userMenu = page.getByTestId("user-menu")
    await revealInSidebar(page, userMenu)
    await expect(userMenu).toContainText(b.email)
    await expect(page.getByText(aEmail)).toHaveCount(0)

    const saved = await getHabits(b.api)
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
    await numberField(page, ALCOHOL_START).fill("17")
    const quitAge = numberField(page, ALCOHOL_QUIT_AGE)
    await quitAge.fill("40")
    // Se espera el PUT de "Guardar", el que lleva el 40.
    const put = page.waitForResponse(
      (res) =>
        res.url().endsWith("/profile/habits") &&
        res.request().method() === "PUT" &&
        res.request().postDataJSON()?.alcohol?.quit_age === 40,
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
    expect(saved.alcohol?.quit_age ?? null).toBeNull()
  })

  test("R12 un error no sobrevive a su pregunta: de 'Antes' a 'Actual' se va el de 'empezó después de dejarlo'", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, TOBACCO, "Antes").click()
    await numberField(page, CIGARETTES).fill("10")
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

  test("R14 (C-15) 'Sobre todo fines de semana' con chips 'Sí' / 'No': tocar 'Sí' otra vez lo deja sin contestar, y 'Guardar' pide contestarla sin mandar nada", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Actual").click()
    await numberField(page, ALCOHOL_START).fill("18")
    await chip(page, FREQUENCY, "2 a 3 veces por semana").click()
    await chip(page, DRINKS, "3 o 4").click()
    await chip(page, SIX_OR_MORE, "Cada mes").click()
    await chip(page, WEEKENDS, "Sí").click()
    await saveOk(page)
    expect((await getHabits(api)).alcohol?.mostly_weekends).toBe(true)

    await reopen(page)
    await expectPressed(chip(page, WEEKENDS, "Sí"), true)
    await chip(page, WEEKENDS, "Sí").click()
    await expectPressed(chip(page, WEEKENDS, "Sí"), false)
    await expectPressed(chip(page, WEEKENDS, "No"), false)

    const puts = trackHabitPuts(page)
    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    await expectGroupError(page, WEEKENDS, MISSING)
    await expectNoPut(page, puts)
    await expect(page).toHaveURL(HABITS_URL)

    const saved = await getHabits(api)
    expect(saved.alcohol?.status).toBe("current")
    expect(saved.alcohol?.mostly_weekends).toBe(true)
  })

  test("N3 (ronda 2) 'Sobre todo fines de semana' en 'No' se guarda como false y al reabrir 'No' sigue elegido", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Actual").click()
    await numberField(page, ALCOHOL_START).fill("18")
    await chip(page, FREQUENCY, "2 a 3 veces por semana").click()
    await chip(page, DRINKS, "3 o 4").click()
    await chip(page, SIX_OR_MORE, "Cada mes").click()
    await chip(page, WEEKENDS, "No").click()
    await saveOk(page)
    expect((await getHabits(api)).alcohol?.mostly_weekends).toBe(false)

    await reopen(page)
    await expectPressed(chip(page, WEEKENDS, "No"), true)
    await expectPressed(chip(page, WEEKENDS, "Sí"), false)
  })

  test("R18 un 422 en una pregunta de chips va bajo SU grupo (servidor simulado: la UI no puede provocarlo)", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)
    // Completo (C-15): si faltara algo, la pantalla no mandaría el PUT.
    await chip(page, ALCOHOL, "Actual").click()
    await numberField(page, ALCOHOL_START).fill("18")
    await chip(page, FREQUENCY, "2 a 3 veces por semana").click()
    await chip(page, DRINKS, "3 o 4").click()
    await chip(page, SIX_OR_MORE, "Cada mes").click()
    await chip(page, WEEKENDS, "Sí").click()
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

test.describe("Perfil médico — hábitos completos (perfil-habitos-completitud, grupo 2)", () => {
  test("C-15 (completitud) la introducción pide completar lo que abre una respuesta y menciona «No recuerdo»", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await expect(page.getByText(INTRO, { exact: true })).toBeVisible()
    await expect(page.getByText(SAVE_HINT, { exact: true })).toBeVisible()
  })

  test("C-15 (completitud fila 2) falta la edad de inicio: alcohol 'Lo dejé' con solo 30 en la edad en que lo dejó → 'Guardar' → 'Contesta esta pregunta o marca «No recuerdo».' junto a la edad de inicio, con el foco ahí, y ningún PUT", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)

    await chip(page, ALCOHOL, "Lo dejé").click()
    const start = numberField(page, ALCOHOL_START)
    const quit = numberField(page, ALCOHOL_QUIT_AGE)
    // Pasar por la edad de inicio sin contestarla no regaña: lo que falta se
    // revisa al tocar "Guardar".
    await start.focus()
    await start.press("Tab")
    await quit.fill("30")
    await quit.press("Tab")
    await expectNoFieldError(page, start, MISSING_OR_UNKNOWN)

    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    await expectFieldError(page, start, MISSING_OR_UNKNOWN)
    await expect(quit).not.toHaveAttribute("aria-invalid", "true")
    await expectNoPut(page, puts)
    await expect(page).toHaveURL(HABITS_URL)
    expect((await getHabits(api)).alcohol ?? null).toBeNull()
  })

  // Fila 2 en pantalla, por cada fila de HABITS_REQUIRED (design.md, tabla de
  // obligatoriedad): con todas las demás contestadas, falta solo una. Los
  // lugares del humo ajeno no se alcanzan en pantalla (estar expuesto sale de
  // elegir un lugar), así que su fila solo prueba los días.
  type RequiredQuestion = {
    label: string
    kind: "number" | "group"
    message: string
    answer: (page: Page) => Promise<void>
  }
  const numberAnswer = (
    label: string,
    value: string,
    message: string,
  ): RequiredQuestion => ({
    label,
    kind: "number",
    message,
    answer: (page) => numberField(page, label).fill(value),
  })
  const chipAnswer = (label: string, option: string): RequiredQuestion => ({
    label,
    kind: "group",
    message: MISSING,
    answer: (page) => chip(page, label, option).click(),
  })
  const REQUIRED_ROWS: {
    title: string
    choose: (page: Page) => Promise<void>
    questions: RequiredQuestion[]
  }[] = [
    {
      title: "alcohol 'Lo dejé'",
      choose: (page) => chip(page, ALCOHOL, "Lo dejé").click(),
      questions: [
        numberAnswer(ALCOHOL_START, "18", MISSING_OR_UNKNOWN),
        numberAnswer(ALCOHOL_QUIT_AGE, "30", MISSING_OR_UNKNOWN),
      ],
    },
    {
      title: "alcohol 'Actual'",
      choose: (page) => chip(page, ALCOHOL, "Actual").click(),
      questions: [
        chipAnswer(FREQUENCY, "2 a 3 veces por semana"),
        chipAnswer(DRINKS, "3 o 4"),
        chipAnswer(SIX_OR_MORE, "Cada mes"),
        chipAnswer(WEEKENDS, "Sí"),
        numberAnswer(ALCOHOL_START, "18", MISSING_OR_UNKNOWN),
      ],
    },
    {
      title: "tabaco 'Antes'",
      choose: (page) => chip(page, TOBACCO, "Antes").click(),
      questions: [
        numberAnswer(CIGARETTES, "10", MISSING_OR_UNKNOWN),
        numberAnswer(TOBACCO_START, "18", MISSING_OR_UNKNOWN),
        numberAnswer(TOBACCO_QUIT, "30", MISSING_OR_UNKNOWN),
      ],
    },
    {
      title: "tabaco 'Actual'",
      choose: (page) => chip(page, TOBACCO, "Actual").click(),
      questions: [
        numberAnswer(CIGARETTES, "10", MISSING),
        numberAnswer(TOBACCO_START, "18", MISSING_OR_UNKNOWN),
      ],
    },
    {
      title: "vapeador 'Antes'",
      choose: (page) => chip(page, VAPING, "Antes").click(),
      questions: [
        numberAnswer(VAPING_START, "25", MISSING_OR_UNKNOWN),
        numberAnswer(VAPING_QUIT, "28", MISSING_OR_UNKNOWN),
      ],
    },
    {
      title: "vapeador 'Actual'",
      choose: (page) => chip(page, VAPING, "Actual").click(),
      questions: [
        chipAnswer(VAPING_FREQUENCY, "Todos los días"),
        numberAnswer(VAPING_START, "25", MISSING_OR_UNKNOWN),
      ],
    },
    {
      title: "vapeador 'Actual' 'Algunos días'",
      choose: async (page) => {
        await chip(page, VAPING, "Actual").click()
        await chip(page, VAPING_FREQUENCY, "Algunos días").click()
      },
      questions: [
        numberAnswer(VAPING_DAYS, "12", MISSING),
        numberAnswer(VAPING_START, "25", MISSING_OR_UNKNOWN),
      ],
    },
    {
      title: "humo ajeno en 'Casa'",
      choose: (page) => chip(page, WHERE, "Casa").click(),
      questions: [numberAnswer(DAYS, "2", MISSING)],
    },
    {
      title: "leña 'Antes'",
      choose: (page) => chip(page, WOOD, "Antes").click(),
      questions: [
        numberAnswer(WOOD_START, "5", MISSING_OR_UNKNOWN),
        numberAnswer(WOOD_QUIT, "20", MISSING_OR_UNKNOWN),
        numberAnswer(WOOD_HOURS, "3", MISSING_OR_UNKNOWN),
      ],
    },
    {
      title: "leña 'Actual'",
      choose: (page) => chip(page, WOOD, "Actual").click(),
      questions: [
        numberAnswer(WOOD_HOURS, "3", MISSING),
        numberAnswer(WOOD_START, "5", MISSING_OR_UNKNOWN),
      ],
    },
  ]
  for (const row of REQUIRED_ROWS) {
    test(`C-15 (completitud fila 2) cada pregunta que abre ${row.title}: con las demás contestadas y solo esa sin contestar, 'Guardar' pone su mensaje junto a ella, ningún otro, y ningún PUT`, async ({
      page,
      request,
    }) => {
      await freshPatient(page, request)
      const puts = trackHabitPuts(page)

      for (const missing of row.questions) {
        await openHabitsFromProfile(page)
        await row.choose(page)
        for (const question of row.questions) {
          if (question !== missing) await question.answer(page)
        }
        await page.getByRole("button", { name: "Guardar", exact: true }).click()

        if (missing.kind === "number") {
          await expectFieldError(
            page,
            numberField(page, missing.label),
            missing.message,
          )
        } else {
          await expectGroupError(page, missing.label, missing.message)
        }
        const other = missing.message === MISSING ? MISSING_OR_UNKNOWN : MISSING
        await expect(
          page.getByText(missing.message, { exact: true }),
        ).toHaveCount(1)
        await expect(page.getByText(other, { exact: true })).toHaveCount(0)
        await expect(page).toHaveURL(HABITS_URL)

        // Descarta y vuelve a abrir para la siguiente pregunta.
        await page
          .getByRole("button", { name: "Cancelar", exact: true })
          .click()
        await page.waitForURL(PROFILE_URL)
      }
      await expectNoPut(page, puts)
    })
  }

  test("C-15 (completitud fila 3) alcohol 'Actual' desde los 18 sin las preguntas de frecuencia: 'Guardar' → 'Contesta esta pregunta.' bajo las tres del AUDIT-C y 'Sobre todo fines de semana', ninguna ofrece 'No recuerdo', foco en la primera y ningún PUT; al cambiar a 'Nunca' se van esos errores y se guarda", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)
    const questions = [FREQUENCY, DRINKS, SIX_OR_MORE, WEEKENDS]

    await chip(page, ALCOHOL, "Actual").click()
    await numberField(page, ALCOHOL_START).fill("18")
    await page.getByRole("button", { name: "Guardar", exact: true }).click()

    for (const name of questions) {
      await expectGroupError(page, name, MISSING)
    }
    // En toda la pantalla, el único "No recuerdo" es el de la edad de inicio.
    await expect(
      page.getByRole("button", { name: /^No recuerdo/ }),
    ).toHaveCount(1)
    await expect(dontRemember(page, ALCOHOL_START)).toBeVisible()
    await expect(
      page.getByText(MISSING_OR_UNKNOWN, { exact: true }),
    ).toHaveCount(0)
    await expect(numberField(page, ALCOHOL_START)).not.toHaveAttribute(
      "aria-invalid",
      "true",
    )
    await expect(chip(page, FREQUENCY, "Una vez al mes o menos")).toBeFocused()
    await expectNoPut(page, puts)
    await expect(page).toHaveURL(HABITS_URL)
    expect((await getHabits(api)).alcohol ?? null).toBeNull()

    // Al ocultarse las preguntas se van sus errores.
    await chip(page, ALCOHOL, "Nunca").click()
    await expect(page.getByText(MISSING, { exact: true })).toHaveCount(0)
    await saveOk(page)
    expect((await getHabits(api)).alcohol?.status).toBe("never")
  })

  test("C-16 (completitud fila 4) no recuerda cuándo empezó: alcohol 'Lo dejé', 'No recuerdo' en la edad de inicio (vacía el 40 y quita su error) y 18 en la edad en que lo dejó → se guarda sin error; al reabrir, 'No recuerdo' marcado y 18", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, ALCOHOL, "Lo dejé").click()
    const start = numberField(page, ALCOHOL_START)
    const unknownStart = dontRemember(page, ALCOHOL_START)
    await expectPressed(unknownStart, false)
    const tooOld = "La edad no puede ser mayor que tu edad actual"
    await start.fill("40")
    await start.press("Tab")
    await expectFieldError(page, start, tooOld, { focused: false })

    await unknownStart.click()
    await expectPressed(unknownStart, true)
    await expect(start).toHaveValue("")
    await expectNoFieldError(page, start, tooOld)

    await numberField(page, ALCOHOL_QUIT_AGE).fill("18")
    await saveOk(page)

    expect((await getHabits(api)).alcohol).toMatchObject({
      status: "quit",
      start_age: "unknown",
      quit_age: 18,
    })

    await reopen(page)
    await expectPressed(chip(page, ALCOHOL, "Lo dejé"), true)
    await expectPressed(dontRemember(page, ALCOHOL_START), true)
    await expect(numberField(page, ALCOHOL_START)).toHaveValue("")
    await expect(numberField(page, ALCOHOL_QUIT_AGE)).toHaveValue("18")
    await expectPressed(dontRemember(page, ALCOHOL_QUIT_AGE), false)
  })

  test("C-16 (completitud fila 5) 'No recuerdo' solo en lo que pasó: tabaco 'Actual' → los cigarros no lo ofrecen y la edad de inicio sí; 'Antes' → cigarros, inicio y fin lo ofrecen; igual con las horas de leña; los días del vapeador y del humo ajeno nunca", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)

    await chip(page, TOBACCO, "Actual").click()
    await expect(numberField(page, CIGARETTES)).toBeVisible()
    await expect(dontRemember(page, TOBACCO_START)).toBeVisible()
    await expect(dontRemember(page, CIGARETTES)).toHaveCount(0)

    await chip(page, TOBACCO, "Antes").click()
    for (const label of [CIGARETTES, TOBACCO_START, TOBACCO_QUIT]) {
      await expect(dontRemember(page, label)).toBeVisible()
    }

    await chip(page, WOOD, "Actual").click()
    await expect(numberField(page, WOOD_HOURS)).toBeVisible()
    await expect(dontRemember(page, WOOD_START)).toBeVisible()
    await expect(dontRemember(page, WOOD_HOURS)).toHaveCount(0)

    await chip(page, WOOD, "Antes").click()
    for (const label of [WOOD_HOURS, WOOD_START, WOOD_QUIT]) {
      await expect(dontRemember(page, label)).toBeVisible()
    }

    await chip(page, VAPING, "Actual").click()
    await chip(page, VAPING_FREQUENCY, "Algunos días").click()
    await expect(numberField(page, VAPING_DAYS)).toBeVisible()
    await expect(dontRemember(page, VAPING_START)).toBeVisible()
    await expect(dontRemember(page, VAPING_DAYS)).toHaveCount(0)

    await chip(page, WHERE, "Casa").click()
    await expect(numberField(page, DAYS)).toBeVisible()
    await expect(dontRemember(page, DAYS)).toHaveCount(0)
  })

  test("C-16 (completitud fila 6) escribir un número quita 'No recuerdo': con 'No recuerdo' guardado en la edad de inicio del tabaco, escribir 16 lo desmarca; al guardar y reabrir ve 16", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, {
      tobacco: {
        status: "current",
        cigarettes_per_day: 10,
        start_age: "unknown",
      },
    })
    await openHabitsFromProfile(page)
    await expectPressed(chip(page, TOBACCO, "Actual"), true)
    const start = numberField(page, TOBACCO_START)
    const unknownStart = dontRemember(page, TOBACCO_START)
    await expectPressed(unknownStart, true)
    await expect(start).toHaveValue("")

    await start.pressSequentially("16")
    await expect(start).toHaveValue("16")
    await expectPressed(unknownStart, false)
    await saveOk(page)

    expect((await getHabits(api)).tobacco?.start_age).toBe(16)
    await reopen(page)
    await expect(numberField(page, TOBACCO_START)).toHaveValue("16")
    await expectPressed(dontRemember(page, TOBACCO_START), false)
  })

  test("C-15 (completitud fila 7) lo guardado a medias pide completar al guardar: alcohol 'Lo dejé' con solo 30 (servidor simulado en el GET: el PUT ya no deja guardarlo así) abre sin errores ni 'No recuerdo'; 'Guardar' → 'Contesta esta pregunta o marca «No recuerdo».' junto a la edad de inicio, ningún PUT y lo guardado no cambia", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await seedHabits(api, { tobacco: { status: "never" } })
    const before = await getHabits(api)
    // Una fila de antes de este cambio: el GET real con el alcohol a medias.
    await page.route("**/api/v1/profile/habits", async (route) => {
      if (route.request().method() !== "GET") return route.fallback()
      const response = await route.fetch()
      const body = await response.json()
      await route.fulfill({
        response,
        json: {
          ...body,
          alcohol: {
            status: "quit",
            start_age: null,
            quit_age: 30,
            frequency: null,
            typical_drinks: null,
            six_or_more: null,
            mostly_weekends: null,
          },
        },
      })
    })
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)

    await expectPressed(chip(page, ALCOHOL, "Lo dejé"), true)
    const start = numberField(page, ALCOHOL_START)
    await expect(start).toHaveValue("")
    await expect(numberField(page, ALCOHOL_QUIT_AGE)).toHaveValue("30")
    await expectPressed(dontRemember(page, ALCOHOL_START), false)
    await expect(page.locator('[aria-invalid="true"]')).toHaveCount(0)
    await expect(
      page.getByText(MISSING_OR_UNKNOWN, { exact: true }),
    ).toHaveCount(0)

    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    await expectFieldError(page, start, MISSING_OR_UNKNOWN)
    await expectNoPut(page, puts)
    await expect(page).toHaveURL(HABITS_URL)
    expect(await getHabits(api)).toEqual(before)
  })

  test("C-17 (completitud fila 11) el error se va al corregirlo: '12a' en la edad de inicio del alcohol y Tab → 'Escribe solo el número.'; de vuelta en el campo, borrar la 'a' deja 12 y, sin salir, se van el mensaje y aria-invalid; escribir '1a' en la edad en que lo dejó no marca nada hasta salir del campo", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)
    const notANumber = "Escribe solo el número."

    await chip(page, ALCOHOL, "Lo dejé").click()
    const start = numberField(page, ALCOHOL_START)
    await start.fill("12a")
    await start.press("Tab")
    await expectFieldError(page, start, notANumber, { focused: false })

    // Vuelve al campo y borra la "a", sin salir.
    await start.click()
    await start.press("End")
    await start.press("Backspace")
    await expect(start).toHaveValue("12")
    await expectNoFieldError(page, start, notANumber)
    await expect(start).toBeFocused()

    // Mientras escribe en un campo limpio no aparece un error nuevo.
    const quit = numberField(page, ALCOHOL_QUIT_AGE)
    await quit.pressSequentially("1a")
    await expect(quit).toHaveValue("1a")
    await page.waitForTimeout(300)
    await expect(quit).toBeFocused()
    await expectNoFieldError(page, quit, notANumber)
    await expect(
      page.getByText("No puede ser mayor que la edad en que lo dejaste", {
        exact: true,
      }),
    ).toHaveCount(0)

    // Al salir del campo, sí (C-14).
    await quit.press("Tab")
    await expectFieldError(page, quit, notANumber, { focused: false })
  })

  test("C-17 (completitud fila 11) la salida diferida no marca la pareja que se escribe: 12 en la edad de inicio del alcohol; con el botón apretado sobre la edad en que lo dejó (la salida de la de inicio queda pendiente) se escribe '1a' y se suelta → sin mensaje ni aria-invalid mientras sigue en el campo; con Tab, 'Escribe solo el número.'", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)
    const notANumber = "Escribe solo el número."

    await chip(page, ALCOHOL, "Lo dejé").click()
    const start = numberField(page, ALCOHOL_START)
    const quit = numberField(page, ALCOHOL_QUIT_AGE)
    await start.fill("12")
    await expect(start).toBeFocused()
    await quit.scrollIntoViewIfNeeded()
    await expect(start).toBeFocused()

    // Entrada real: el foco pasa al apretar el botón y la salida de la edad de
    // inicio se resuelve al soltarlo, ya con "1a" escrito en la otra.
    const box = await quit.boundingBox()
    if (!box) throw new Error("La edad en que lo dejó no está a la vista")
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2)
    await page.mouse.down()
    await expect(quit).toBeFocused()
    await page.keyboard.type("1a")
    await expect(quit).toHaveValue("1a")
    await page.mouse.up()
    await page.waitForTimeout(300)
    await expect(quit).toBeFocused()
    await expectNoFieldError(page, quit, notANumber)

    await quit.press("Tab")
    await expectFieldError(page, quit, notANumber, { focused: false })
  })

  test("C-17 (completitud fila 11) borrar todo también quita el error: 101 en 'Cigarros al día' y Tab → 'Debe estar entre 1 y 100'; al vaciar el campo, sin salir, se va; al salir sigue sin error hasta 'Guardar', que pide contestarla", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)
    const outOfScale = "Debe estar entre 1 y 100"

    await chip(page, TOBACCO, "Actual").click()
    const cigarettes = numberField(page, CIGARETTES)
    await cigarettes.fill("101")
    await cigarettes.press("Tab")
    await expectFieldError(page, cigarettes, outOfScale, { focused: false })

    await cigarettes.fill("")
    await expect(cigarettes).toHaveValue("")
    await expect(cigarettes).toBeFocused()
    await expectNoFieldError(page, cigarettes, outOfScale)

    await cigarettes.press("Tab")
    await page.waitForTimeout(300)
    await expect(cigarettes).not.toHaveAttribute("aria-invalid", "true")
    await expect(page.getByText(MISSING, { exact: true })).toHaveCount(0)

    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    await expectFieldError(page, cigarettes, MISSING)
    await expectNoPut(page, puts)
  })

  test("C-16 (completitud fila 12) accesibilidad de 'No recuerdo': con tabaco 'Antes', los tres chips visibles tienen nombres distintos; con el PUT retenido, aria-disabled='true' y su clic no cambia nada; al soltarlo se guarda «No recuerdo» en los cigarros", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setAge36(api)
    await openHabitsFromProfile(page)

    await chip(page, TOBACCO, "Antes").click()
    for (const label of [CIGARETTES, TOBACCO_START, TOBACCO_QUIT]) {
      await expect(dontRemember(page, label)).toHaveCount(1)
      await expect(dontRemember(page, label)).toBeVisible()
    }
    await expect(
      page.getByRole("button", { name: "No recuerdo", exact: true }),
    ).toHaveCount(0)

    const puts = trackHabitPuts(page)
    const hold = await holdFirstHabitsPut(page)
    await dontRemember(page, CIGARETTES).click()
    await numberField(page, TOBACCO_START).fill("18")
    await numberField(page, TOBACCO_QUIT).fill("30")
    await markShownToasts(page)
    await page.getByRole("button", { name: "Guardar", exact: true }).click()
    await expect.poll(() => puts.length).toBe(1)

    const unknownStart = dontRemember(page, TOBACCO_START)
    await expect(unknownStart).toHaveAttribute("aria-disabled", "true")
    await expect(dontRemember(page, CIGARETTES)).toHaveAttribute(
      "aria-disabled",
      "true",
    )
    await unknownStart.click({ force: true })
    await page.waitForTimeout(300)
    await expectPressed(unknownStart, false)
    await expect(numberField(page, TOBACCO_START)).toHaveValue("18")
    await expectPressed(dontRemember(page, CIGARETTES), true)

    const putResponse = await hold.releaseAndWait()
    expect(putResponse.status()).toBe(200)
    await page.waitForURL(PROFILE_URL)
    await expect(newToast(page, "Hábitos guardados")).toBeVisible()
    expect(puts).toHaveLength(1)
    expect((await getHabits(api)).tobacco).toMatchObject({
      status: "former",
      cigarettes_per_day: "unknown",
      start_age: 18,
      quit_age: 30,
    })
  })

  test("C-16 (completitud) marcar 'No recuerdo' es un cambio sin guardar: tabaco 'Antes' guardado desde los 18; marcar 'No recuerdo' en esa edad la vacía y '‹ Mi perfil médico' pregunta '¿Salir sin guardar?'; 'Salir sin guardar' deja los 18", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedHabits(api, {
      tobacco: {
        status: "former",
        cigarettes_per_day: 10,
        start_age: 18,
        quit_age: 30,
      },
    })
    await openHabitsFromProfile(page)
    const puts = trackHabitPuts(page)
    await expect(numberField(page, TOBACCO_START)).toHaveValue("18")

    await dontRemember(page, TOBACCO_START).click()
    await expectPressed(dontRemember(page, TOBACCO_START), true)
    await expect(numberField(page, TOBACCO_START)).toHaveValue("")

    await backLink(page).click()
    const dialog = leaveDialog(page)
    await expect(dialog).toBeVisible()
    await dialog
      .getByRole("button", { name: "Salir sin guardar", exact: true })
      .click()
    await page.waitForURL(PROFILE_URL)
    await expectNoPut(page, puts)
    expect((await getHabits(api)).tobacco?.start_age).toBe(18)
  })
})
