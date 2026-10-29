import {
  type APIRequestContext,
  expect,
  type Locator,
  type Page,
  test,
} from "@playwright/test"
import { createUser } from "./utils/privateApi"
import { randomEmail, randomPassword } from "./utils/random"

test.use({ storageState: { cookies: [], origins: [] } })

// --- Contrato que este spec fija (paleta-azul-clinico) ------------------------
//
// Fuente: openspec/changes/paleta-azul-clinico/design.md → Interface contract,
// con los escenarios P-1, P-2, P-5, P-3 y P-6 de
// openspec/changes/paleta-azul-clinico/specs/ux/visual-accessibility/spec.md
// (P-4, daltonismo emulado, es manual: validation.md).
//
// Pantalla: /perfil/habitos, con una cuenta creada por API.
// Tema: localStorage["vite-ui-theme"] = "light" | "dark" antes de cargar; en
//   oscuro <html> lleva la clase "dark".
// Medición: getComputedStyle, normalizado a sRGB pintándolo en un canvas 1×1;
//   fondo efectivo = primer background-color con alfa > 0 del elemento o de
//   sus ancestros (si es translúcido, se compone sobre el de debajo); contraste
//   WCAG 2.2 (L1 + 0.05) / (L2 + 0.05).
// Umbrales: texto ≥ 4.5 contra su fondo efectivo; bordes de controles ≥ 3
//   contra el fondo efectivo del padre del control.
// Exactos: fondo de «Guardar» rgb(0, 94, 184) en claro y rgb(90, 169, 240) en
//   oscuro; casilla «Caminar» 20 × 20 px (±0.5); etiqueta «Caminar» peso 400;
//   legend «¿Qué ejercicio haces?» peso ≥ 600.
// ---------------------------------------------------------------------------

const API = `${process.env.VITE_API_URL}/api/v1`
const HABITS_PATH = "/perfil/habitos"
const THEME_KEY = "vite-ui-theme"

const EXERCISE = "¿Qué ejercicio haces?"
const WALKING = "Caminar"
const RUNNING = "Correr"
const ACTIVE_TRAVEL =
  "¿Caminas o vas en bici al menos 10 minutos seguidos para ir a algún lado?"
const INTRO_START = /^Contesta los hábitos que quieras/
const MISSING = "Contesta esta pregunta."

const TEXT_MIN = 4.5
const BORDER_MIN = 3
const BRAND_LIGHT = "rgb(0, 94, 184)"
const BRAND_DARK = "rgb(90, 169, 240)"

type Theme = "light" | "dark"

/** Sin keep-alive: el backend cierra conexiones inactivas (ver profile-habits). */
const NO_KEEP_ALIVE = { Connection: "close" }

/**
 * Paciente nuevo con el consentimiento dado por API; devuelve su token.
 * Correos @example.com (D19).
 */
async function consentedPatientToken(
  request: APIRequestContext,
): Promise<string> {
  const email = randomEmail()
  const password = randomPassword()
  await createUser({ email, password })
  const login = await request.post(`${API}/login/access-token`, {
    headers: NO_KEEP_ALIVE,
    form: { username: email, password },
  })
  expect(login.ok()).toBeTruthy()
  const { access_token } = await login.json()
  const headers = { ...NO_KEEP_ALIVE, Authorization: `Bearer ${access_token}` }
  const text = await request.get(`${API}/consent/text`, { headers })
  expect(text.ok()).toBeTruthy()
  const consent = await request.post(`${API}/consent/`, {
    headers,
    data: { version: (await text.json()).version },
  })
  expect(consent.ok()).toBeTruthy()
  return access_token
}

/**
 * Sesión por localStorage y tema elegido antes de cargar. El tema solo se
 * escribe si no hay uno, para poder cambiarlo después con `switchTheme`.
 */
async function openHabits(
  page: Page,
  request: APIRequestContext,
  theme: Theme,
) {
  const token = await consentedPatientToken(request)
  await page.addInitScript(
    ([t, key, th]) => {
      localStorage.setItem("access_token", t)
      if (!localStorage.getItem(key)) localStorage.setItem(key, th)
    },
    [token, THEME_KEY, theme],
  )
  await page.goto(HABITS_PATH)
  await expectHabitsScreen(page)
}

/** Cambia el tema y recarga (sin cambios en el formulario: no hay beforeunload). */
async function switchTheme(page: Page, theme: Theme) {
  await page.evaluate(
    ([key, th]) => localStorage.setItem(key, th),
    [THEME_KEY, theme],
  )
  await page.reload()
  await expectHabitsScreen(page)
}

async function expectHabitsScreen(page: Page) {
  await expect(
    page.getByRole("heading", { name: "Hábitos", exact: true }),
  ).toBeVisible()
  await expect(saveButton(page)).toBeVisible()
}

async function expectTheme(page: Page, theme: Theme) {
  const html = page.locator("html")
  if (theme === "dark") await expect(html).toHaveClass(/(^|\s)dark(\s|$)/)
  else await expect(html).not.toHaveClass(/(^|\s)dark(\s|$)/)
}

function saveButton(page: Page): Locator {
  return page.getByRole("button", { name: "Guardar", exact: true })
}

function group(page: Page, name: string): Locator {
  return page.getByRole("group", { name, exact: true }).first()
}

function exerciseBox(page: Page, option: string): Locator {
  return group(page, EXERCISE).getByRole("checkbox", {
    name: option,
    exact: true,
  })
}

function chip(page: Page, groupName: string, option: string): Locator {
  return group(page, groupName)
    .getByRole("button", { name: option, exact: true })
    .first()
}

/** "Días por semana: Caminar" (spinbutton o textbox, por su label). */
function walkingDays(page: Page): Locator {
  return page.getByLabel(`Días por semana: ${WALKING}`, { exact: true })
}

/** El elemento de aria-describedby de `field` que dice `message`. */
async function describedMessage(
  page: Page,
  field: Locator,
  message: string,
): Promise<Locator> {
  await expect(field).toHaveAttribute("aria-describedby", /\S/)
  let found: Locator | null = null
  await expect
    .poll(async () => {
      const ids = ((await field.getAttribute("aria-describedby")) ?? "")
        .split(/\s+/)
        .filter(Boolean)
      for (const id of ids) {
        const el = page.locator(`[id="${id}"]`)
        if (
          (await el.count()) > 0 &&
          ((await el.first().textContent()) ?? "").trim() === message
        ) {
          found = el.first()
          return true
        }
      }
      return false
    })
    .toBe(true)
  return found as unknown as Locator
}

/** Marca «Caminar» y elige «No» en el grupo de chips de traslado activo. */
async function walkingAndNoChip(page: Page) {
  await exerciseBox(page, WALKING).click()
  await expect(exerciseBox(page, WALKING)).toBeChecked()
  await expect(walkingDays(page)).toBeVisible()
  await chip(page, ACTIVE_TRAVEL, "No").click()
  await expect(chip(page, ACTIVE_TRAVEL, "No")).toHaveAttribute(
    "aria-pressed",
    "true",
  )
  await expect(chip(page, ACTIVE_TRAVEL, "Sí")).toHaveAttribute(
    "aria-pressed",
    "false",
  )
}

/** Sin foco ni puntero encima de nada, y las transiciones de color terminadas. */
async function settle(page: Page) {
  await page.evaluate(() => {
    const active = document.activeElement as HTMLElement | null
    active?.blur()
  })
  await page.mouse.move(0, 0)
  await page.evaluate(async () => {
    await Promise.all(
      document
        .getAnimations()
        .filter((a) => a.constructor.name === "CSSTransition")
        .map((a) => a.finished.catch(() => undefined)),
    )
  })
}

type Measure = { fg: string; bg: string; ratio: number }

/**
 * Mide en el navegador. `text`: color del texto contra el fondo efectivo del
 * elemento. `border`: border-top-color del control contra el fondo efectivo
 * de su padre. `background`: el background-color del elemento, normalizado.
 */
async function measure(
  locator: Locator,
  kind: "text" | "border" | "background",
): Promise<Measure> {
  await expect(locator).toBeVisible()
  return locator.evaluate((el, k) => {
    type RGBA = [number, number, number, number]
    const canvas = document.createElement("canvas")
    canvas.width = 1
    canvas.height = 1
    const ctx = canvas.getContext("2d", {
      willReadFrequently: true,
    }) as CanvasRenderingContext2D
    const toRgba = (css: string): RGBA => {
      ctx.clearRect(0, 0, 1, 1)
      ctx.fillStyle = "rgba(0, 0, 0, 0)"
      ctx.fillStyle = css
      ctx.fillRect(0, 0, 1, 1)
      const d = ctx.getImageData(0, 0, 1, 1).data
      return [d[0], d[1], d[2], d[3]]
    }
    const over = (top: RGBA, under: RGBA): RGBA => {
      const a = top[3] / 255
      return [
        Math.round(top[0] * a + under[0] * (1 - a)),
        Math.round(top[1] * a + under[1] * (1 - a)),
        Math.round(top[2] * a + under[2] * (1 - a)),
        255,
      ]
    }
    const effectiveBg = (start: Element | null): RGBA => {
      let node: Element | null = start
      while (node) {
        const c = toRgba(getComputedStyle(node).backgroundColor)
        if (c[3] > 0) {
          if (c[3] >= 255) return c
          return over(c, effectiveBg(node.parentElement))
        }
        node = node.parentElement
      }
      return [255, 255, 255, 255]
    }
    const lum = (c: RGBA) => {
      const ch = (v: number) => {
        const s = v / 255
        return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4
      }
      return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])
    }
    const contrast = (a: RGBA, b: RGBA) => {
      const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x)
      return (hi + 0.05) / (lo + 0.05)
    }
    const fmt = (c: RGBA) =>
      c[3] >= 255
        ? `rgb(${c[0]}, ${c[1]}, ${c[2]})`
        : `rgba(${c[0]}, ${c[1]}, ${c[2]}, ${(c[3] / 255).toFixed(3)})`

    const style = getComputedStyle(el)
    if (k === "background") {
      const bg = toRgba(style.backgroundColor)
      return { fg: "", bg: fmt(bg), ratio: 0 }
    }
    const bg = k === "text" ? effectiveBg(el) : effectiveBg(el.parentElement)
    const raw = toRgba(k === "text" ? style.color : style.borderTopColor)
    const fg = over(raw, bg)
    return {
      fg: fmt(fg),
      bg: fmt(bg),
      ratio: Math.round(contrast(fg, bg) * 100) / 100,
    }
  }, kind)
}

async function expectTextContrast(label: string, locator: Locator) {
  const m = await measure(locator, "text")
  expect
    .soft(m.ratio, `${label}: texto ${m.fg} sobre ${m.bg} = ${m.ratio}:1`)
    .toBeGreaterThanOrEqual(TEXT_MIN)
}

async function expectBorderContrast(label: string, locator: Locator) {
  const m = await measure(locator, "border")
  expect
    .soft(m.ratio, `${label}: borde ${m.fg} sobre ${m.bg} = ${m.ratio}:1`)
    .toBeGreaterThanOrEqual(BORDER_MIN)
}

async function expectSaveBackground(page: Page, expected: string) {
  await settle(page)
  const m = await measure(saveButton(page), "background")
  expect.soft(m.bg, `fondo de «Guardar»`).toBe(expected)
}

/** P-2: bordes con «Caminar» marcada (antes de guardar: sin estado de error). */
async function checkControlBorders(page: Page) {
  await expect(exerciseBox(page, RUNNING)).not.toBeChecked()
  await settle(page)
  await expectBorderContrast("«Días por semana: Caminar»", walkingDays(page))
  await expectBorderContrast(
    "casilla «Correr» sin marcar",
    exerciseBox(page, RUNNING),
  )
  await expectBorderContrast(
    "chip «Sí» sin elegir",
    chip(page, ACTIVE_TRAVEL, "Sí"),
  )
}

/** P-1: textos tras pulsar «Guardar» sin los días de «Caminar». */
async function checkTexts(page: Page) {
  await saveButton(page).click()
  const error = await describedMessage(page, walkingDays(page), MISSING)
  await expect(error).toBeVisible()
  await settle(page)
  await expectTextContrast(
    "título «Hábitos»",
    page.getByRole("heading", { name: "Hábitos", exact: true }),
  )
  await expectTextContrast(
    "introducción (texto secundario)",
    page.getByText(INTRO_START).first(),
  )
  await expectTextContrast("texto de «Guardar»", saveButton(page))
  await expectTextContrast("chip elegido «No»", chip(page, ACTIVE_TRAVEL, "No"))
  await expectTextContrast(`«${MISSING}»`, error)
}

test.describe("Accesibilidad visual: paleta B · Azul clínico (paleta-azul-clinico)", () => {
  test("P-1 texto legible en claro", async ({ page, request }) => {
    await openHabits(page, request, "light")
    await expectTheme(page, "light")
    await walkingAndNoChip(page)
    await checkTexts(page)
  })

  test("P-2 controles visibles en claro", async ({ page, request }) => {
    await openHabits(page, request, "light")
    await expectTheme(page, "light")
    await walkingAndNoChip(page)
    await checkControlBorders(page)
  })

  test("P-5 en oscuro se cumplen los mismos umbrales y «Guardar» es #5aa9f0 (en claro #005eb8)", async ({
    page,
    request,
  }) => {
    // Claro: la marca de D22.
    await openHabits(page, request, "light")
    await expectTheme(page, "light")
    await expectSaveBackground(page, BRAND_LIGHT)

    // Oscuro: la marca de D22, P-2 y P-1.
    await switchTheme(page, "dark")
    await expectTheme(page, "dark")
    await expectSaveBackground(page, BRAND_DARK)
    await walkingAndNoChip(page)
    await checkControlBorders(page)
    await checkTexts(page)
  })

  test("P-3 el error no es solo color", async ({ page, request }) => {
    await openHabits(page, request, "light")
    await exerciseBox(page, WALKING).click()
    await expect(exerciseBox(page, WALKING)).toBeChecked()
    await expect(walkingDays(page)).toHaveValue("")
    await saveButton(page).click()
    await expect(walkingDays(page)).toHaveAttribute("aria-invalid", "true")
    const error = await describedMessage(page, walkingDays(page), MISSING)
    await expect(error).toBeVisible()
    await expect(error).toHaveText(MISSING)
  })

  test("P-6 casillas y jerarquía", async ({ page, request }) => {
    await openHabits(page, request, "light")
    const box = exerciseBox(page, WALKING)
    await expect(box).toBeVisible()
    await box.scrollIntoViewIfNeeded()

    const size = await box.boundingBox()
    expect(size, "caja de la casilla «Caminar»").not.toBeNull()
    expect
      .soft(Math.abs((size?.width ?? 0) - 20), `ancho ${size?.width} px`)
      .toBeLessThanOrEqual(0.5)
    expect
      .soft(Math.abs((size?.height ?? 0) - 20), `alto ${size?.height} px`)
      .toBeLessThanOrEqual(0.5)

    // La etiqueta visible de la casilla: su <label>, o lo que la nombra.
    const labelWeight = await box.evaluate((el) => {
      const labelled = el as HTMLButtonElement | HTMLInputElement
      let label: Element | null = labelled.labels?.[0] ?? null
      if (!label) {
        const ids = (el.getAttribute("aria-labelledby") ?? "")
          .split(/\s+/)
          .filter(Boolean)
        label = ids.length ? document.getElementById(ids[0]) : null
      }
      if (!label) label = el.closest("label")
      if (!label) return null
      return {
        text: (label.textContent ?? "").trim(),
        weight: Number(getComputedStyle(label).fontWeight),
      }
    })
    expect(labelWeight, "la casilla «Caminar» tiene etiqueta").not.toBeNull()
    expect(labelWeight?.text).toBe(WALKING)
    expect.soft(labelWeight?.weight, "peso de la etiqueta «Caminar»").toBe(400)

    const legend = group(page, EXERCISE)
      .locator("legend")
      .filter({ hasText: EXERCISE })
      .first()
    await expect(legend).toBeVisible()
    const legendWeight = await legend.evaluate((el) =>
      Number(getComputedStyle(el).fontWeight),
    )
    expect
      .soft(legendWeight, `peso de «${EXERCISE}»`)
      .toBeGreaterThanOrEqual(600)
  })
})
