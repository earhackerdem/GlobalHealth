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
// Fuente: openspec/changes/perfil-eventos/design.md → Interface contract →
// Frontend, y los escenarios de specs/records/patient-profile/spec.md.
//
// URLs de sección: /perfil/pasadas, /perfil/cirugias, /perfil/fracturas,
//   /perfil/transfusiones.
//
// data-testid nuevos:
//   history-card-<section>   tarjeta en /perfil, <section> ∈ past · surgeries ·
//                            fractures · transfusions · chronic · habits. Texto
//                            de estado: "Sin llenar" · "Ninguna" ·
//                            "1 registro" · "N registros". Solo las 4 de
//                            eventos son enlaces (chronic y habits: sin enlace,
//                            sin inputs, sin "Agregar").
//   history-entries          lista de registros en la pantalla de sección
//                            (region nombrada por el encabezado; recibe el
//                            foco al guardar, cancelar, eliminar, marcar
//                            "ninguna" y "Deshacer")
//   history-entry            un elemento por registro, con su resumen
// data-testid reutilizados: consent-accept-button, onboarding-wizard,
//   profile-basic-data.
//
// Textos es-MX asertados como contrato (pantalla de sección):
//   Botones "Agregar", "Editar", "Eliminar"; por fila, el nombre accesible
//   lleva el título del registro: "Editar Apendicectomía", "Eliminar Radio"
//   (texto visible "Editar" / "Eliminar"). Confirmación en la misma
//   pantalla "Sí, eliminar" / "Cancelar": al abrirla el foco va a
//   "Sí, eliminar"; al cancelarla vuelve al "Eliminar <título>" de su fila.
//   Guardar el formulario con "Guardar" (exact, convención de
//   profile.spec.ts).
//   "No he tenido ninguna" ("Nunca me han transfundido" en transfusiones) y
//   "Deshacer"; estado de la sección "Ninguna" / "Sin llenar".
//   Aviso al quitar la marca: "Guardado. La sección ya no dice «ninguna»."
//   Registro vacío: "Llena al menos un dato".
//   Transfusiones: grupo de chips "Grupo sanguíneo" (role group con ese
//   nombre) con A+ A- B+ B- AB+ AB- O+ O- visibles y "No lo sé"; el nombre
//   accesible de cada chip es el hablado: "A positivo", "A negativo", …,
//   "O negativo", "No lo sé". El chip elegido lleva aria-pressed="true".
//   WhenField: campo "Edad que tenías" (alterna con "Año" vía el botón
//   "o el año, si lo sabes" / "o la edad que tenías"); chips
//   "Antes de la primaria", "En la primaria", "En la secundaria",
//   "En la prepa", "No recuerdo".
//   Resumen de "cuándo": "a los 7 años (≈1997)", "en la primaria
//   (≈1996–2001)", "en 2015"; sin fecha de nacimiento, sin el paréntesis.
//   Pista en el formulario: "Año aproximado: …"; no aparece si ese año cae
//   en el futuro. Un "cuándo" imposible que rechaza el servidor (p. ej.
//   "La edad no puede ser mayor que tu edad actual") sale junto al campo y
//   el foco va a ese campo (aria-invalid + aria-describedby).
//
// Campos del formulario (el contract no nombra sus labels; este spec los fija
// con el texto de los campos del spec, como labels accesibles):
//   Cajas de texto (role textbox, nombre que empieza así, sin distinguir
//   mayúsculas): "Nombre", "Motivo", "Hospital o lugar", "Médico",
//   "Detalle" (de la reacción), "Material implantado",
//   "Qué hueso o lesión".
//   Opciones (un combobox con ese label, o un group/radiogroup con ese
//   nombre cuyas opciones son radio o botones): "Condición" (Varicela, …),
//   "Tipo" (Cirugía / Hospitalización sin cirugía), "Lado" (Izquierdo / Derecho / …),
//   "Qué se transfundió" (Sangre, …), y las preguntas sí/no
//   "¿Requirió hospitalización?", "¿Reacción a la anestesia?",
//   "¿Requirió cirugía?", "¿Hubo reacción?" con opciones "Sí" / "No" /
//   "No sé". La opción elegida se reconoce por aria-checked / aria-pressed
//   / checked.
// ---------------------------------------------------------------------------

const API = `${process.env.VITE_API_URL}/api/v1`

type Api = {
  request: APIRequestContext
  headers: Record<string, string>
}

/**
 * Paciente nuevo: alta por API privada, login por UI, consentimiento aceptado
 * y onboarding omitido (como profile.spec.ts). Devuelve un cliente del API ya
 * autenticado para preparar datos (grupo 1 del cambio, ya existente).
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

  const login = await request.post(`${API}/login/access-token`, {
    form: { username: email, password },
  })
  expect(login.ok()).toBeTruthy()
  const { access_token } = await login.json()
  return { request, headers: { Authorization: `Bearer ${access_token}` } }
}

async function seedEntry(api: Api, body: Record<string, unknown>) {
  const res = await api.request.post(`${API}/profile/history`, {
    headers: api.headers,
    data: body,
  })
  expect(res.status()).toBe(201)
  return res.json()
}

async function seedNone(api: Api, section: string) {
  const res = await api.request.put(
    `${API}/profile/history/sections/${section}/none`,
    { headers: api.headers, data: { none: true } },
  )
  expect(res.ok()).toBeTruthy()
}

async function historyCount(api: Api): Promise<number> {
  const res = await api.request.get(`${API}/profile/history`, {
    headers: api.headers,
  })
  expect(res.ok()).toBeTruthy()
  return (await res.json()).count
}

/** Fecha de nacimiento desde "Editar datos básicos" en /perfil. */
async function setBirthDate(page: Page, iso: string, shown: string) {
  await page.goto("/perfil")
  const basics = page.getByTestId("profile-basic-data")
  await basics.getByRole("button", { name: "Editar datos básicos" }).click()
  await page.getByLabel("Fecha de nacimiento").fill(iso)
  await page.getByRole("button", { name: "Guardar", exact: true }).click()
  await expect(basics.getByText(shown)).toBeVisible()
}

async function openSection(page: Page, path: string) {
  await page.goto(path)
  await expect(
    page.getByRole("button", { name: "Agregar", exact: true }),
  ).toBeVisible()
}

async function startAdd(page: Page) {
  await page.getByRole("button", { name: "Agregar", exact: true }).click()
  await expect(
    page.getByRole("button", { name: "Guardar", exact: true }),
  ).toBeVisible()
}

async function save(page: Page) {
  await page.getByRole("button", { name: "Guardar", exact: true }).click()
}

function textbox(page: Page, name: RegExp): Locator {
  return page.getByRole("textbox", { name })
}

/** Opción `option` del campo `field`: combobox, radio o botón (chip). */
async function choiceFor(
  page: Page,
  field: RegExp,
  option: string,
): Promise<{ combo: Locator | null; option: Locator }> {
  const combo = page.getByRole("combobox", { name: field })
  if ((await combo.count()) > 0) {
    return {
      combo,
      option: page.getByRole("option", { name: option, exact: true }),
    }
  }
  const group = page
    .getByRole("radiogroup", { name: field })
    .or(page.getByRole("group", { name: field }))
  return {
    combo: null,
    option: group
      .getByRole("radio", { name: option, exact: true })
      .or(group.getByRole("button", { name: option, exact: true }))
      .first(),
  }
}

async function choose(page: Page, field: RegExp, option: string) {
  const c = await choiceFor(page, field, option)
  if (c.combo) await c.combo.click()
  await c.option.click()
}

async function expectChosen(page: Page, field: RegExp, option: string) {
  const c = await choiceFor(page, field, option)
  if (c.combo) {
    await expect(c.combo).toContainText(option)
    return
  }
  await expect
    .poll(() =>
      c.option.evaluate(
        (el) =>
          el.getAttribute("aria-checked") ??
          el.getAttribute("aria-pressed") ??
          String((el as HTMLInputElement).checked),
      ),
    )
    .toBe("true")
}

/** Chip del WhenField ("En la primaria", "No recuerdo", …). */
async function whenChip(page: Page, name: string) {
  await page
    .getByRole("radio", { name, exact: true })
    .or(page.getByRole("button", { name, exact: true }))
    .first()
    .click()
}

const entries = (page: Page) => page.getByTestId("history-entry")
const card = (page: Page, section: string) =>
  page.getByTestId(`history-card-${section}`)

test.describe("Perfil médico — historial por secciones (perfil-eventos, grupo 2)", () => {
  test("S01 estado de cada sección en su tarjeta", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedEntry(api, { section: "past", condition: "varicella" })
    await seedEntry(api, { section: "past", condition: "measles" })
    await seedNone(api, "transfusions")

    await page.goto("/perfil")
    await expect(
      page.getByRole("heading", { name: "Mi perfil médico" }),
    ).toBeVisible()

    await expect(
      card(page, "past").getByText("2 registros", { exact: true }),
    ).toBeVisible()
    await expect(card(page, "transfusions")).toContainText("Ninguna")
    await expect(card(page, "surgeries")).toContainText("Sin llenar")
    await expect(card(page, "fractures")).toContainText("Sin llenar")

    for (const section of ["chronic", "habits"]) {
      const c = card(page, section)
      await expect(c).toContainText("Sin llenar")
      await expect(c.locator("input, textarea, select")).toHaveCount(0)
      await expect(c.getByRole("link")).toHaveCount(0)
      await expect(
        c.getByRole("button", { name: /Agregar|Añadir/ }),
      ).toHaveCount(0)
      const isLink = await c.evaluate(
        (el) => el.closest("a") !== null || el.getAttribute("role") === "link",
      )
      expect(isLink).toBe(false)
    }
  })

  test("S02 la tarjeta de cirugías abre /perfil/cirugias con 'Agregar'", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await page.goto("/perfil")
    await card(page, "surgeries").click()
    await page.waitForURL(/\/perfil\/cirugias$/)
    await expect(page.getByTestId("history-entries")).toBeVisible()
    await expect(
      page.getByRole("button", { name: "Agregar", exact: true }),
    ).toBeVisible()
  })

  test("S03 enfermedad pasada del catálogo: Varicela en la primaria", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openSection(page, "/perfil/pasadas")
    await startAdd(page)
    await choose(page, /condición/i, "Varicela")
    await whenChip(page, "En la primaria")
    await choose(page, /hospitalizaci/i, "No")
    await save(page)

    await expect(entries(page)).toHaveCount(1)
    await expect(entries(page).first()).toContainText("Varicela")
    await expect(entries(page).first()).toContainText("en la primaria")
  })

  test("S04 enfermedad pasada 'Otra': Chikungunya aparece en la lista", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openSection(page, "/perfil/pasadas")
    await startAdd(page)
    await choose(page, /condición/i, "Otra")
    await textbox(page, /^¿cuál fue\?/i).fill("Chikungunya")
    await save(page)

    await expect(entries(page)).toHaveCount(1)
    await expect(
      entries(page).first().getByText("Chikungunya", { exact: true }),
    ).toBeVisible()
  })

  test("S05 cirugía con todos sus datos; al editar se ven tal cual", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openSection(page, "/perfil/cirugias")
    await startAdd(page)
    await choose(page, /tipo/i, "Cirugía")
    await textbox(page, /^nombre/i).fill("Apendicectomía")
    await page.getByLabel("Edad que tenías").fill("24")
    await textbox(page, /^motivo/i).fill("Apendicitis")
    await textbox(page, /^hospital/i).fill("Hospital General de Zona")
    await textbox(page, /^médico/i).fill("Dra. Ruiz")
    await choose(page, /anestesia/i, "Sí")
    await textbox(page, /^detalle/i).fill("Náusea fuerte")
    await save(page)

    await expect(entries(page)).toHaveCount(1)
    await expect(entries(page).first()).toContainText("Apendicectomía")

    await entries(page)
      .first()
      .getByRole("button", { name: "Editar Apendicectomía", exact: true })
      .click()
    await expect(textbox(page, /^nombre/i)).toHaveValue("Apendicectomía")
    await expectChosen(page, /tipo/i, "Cirugía")
    await expect(page.getByLabel("Edad que tenías")).toHaveValue("24")
    await expect(textbox(page, /^motivo/i)).toHaveValue("Apendicitis")
    await expect(textbox(page, /^hospital/i)).toHaveValue(
      "Hospital General de Zona",
    )
    await expect(textbox(page, /^médico/i)).toHaveValue("Dra. Ruiz")
    await expectChosen(page, /anestesia/i, "Sí")
    await expect(textbox(page, /^detalle/i)).toHaveValue("Náusea fuerte")
    await expect(textbox(page, /^material implantado/i)).toHaveValue("")
  })

  test("S06 fractura con lado e implante", async ({ page, request }) => {
    await freshPatient(page, request)
    await openSection(page, "/perfil/fracturas")
    await startAdd(page)
    await textbox(page, /^qué hueso o lesión/i).fill("Radio")
    await choose(page, /^lado/i, "Izquierdo")
    await page.getByLabel("Edad que tenías").fill("10")
    await choose(page, /requirió cirugía/i, "Sí")
    await textbox(page, /^material implantado/i).fill("Placa y tornillos")
    await save(page)

    await expect(entries(page)).toHaveCount(1)
    const entry = entries(page).first()
    await expect(entry).toContainText("Radio")
    await expect(entry).toContainText("izquierdo")
    await expect(entry).toContainText("Placa y tornillos")
  })

  test("S07 transfusión en 2015 por Parto", async ({ page, request }) => {
    await freshPatient(page, request)
    await openSection(page, "/perfil/transfusiones")
    await startAdd(page)
    await page.getByRole("button", { name: "o el año, si lo sabes" }).click()
    await page.getByLabel("Año", { exact: true }).fill("2015")
    await textbox(page, /^motivo/i).fill("Parto")
    await choose(page, /qué se transfundió/i, "Sangre")
    await choose(page, /hubo reacción/i, "No")
    await save(page)

    await expect(entries(page)).toHaveCount(1)
    await expect(entries(page).first()).toContainText("en 2015")
    await expect(entries(page).first()).toContainText("Parto")
  })

  test("S09 una transfusión sin datos no se guarda", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openSection(page, "/perfil/transfusiones")
    await startAdd(page)
    await save(page)

    await expect(page.getByText("Llena al menos un dato")).toBeVisible()

    // "Cancelar" vuelve a la lista con el foco en ella.
    await page.getByRole("button", { name: "Cancelar", exact: true }).click()
    await expect(page.getByTestId("history-entries")).toBeFocused()
    await expect(entries(page)).toHaveCount(0)
    expect(await historyCount(api)).toBe(0)
  })

  test("S10 editar el lado de una fractura y eliminarla con confirmación", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedEntry(api, { section: "fractures", what: "Radio", side: "left" })
    await openSection(page, "/perfil/fracturas")
    await expect(entries(page)).toHaveCount(1)

    const list = page.getByTestId("history-entries")
    await entries(page)
      .first()
      .getByRole("button", { name: "Editar Radio", exact: true })
      .click()
    await choose(page, /^lado/i, "Derecho")
    await save(page)
    await expect(entries(page).first()).toContainText("derecho")
    await expect(list).toBeFocused()

    // "Cancelar" conserva el registro; el foco va a "Sí, eliminar" al abrir
    // la confirmación y vuelve al "Eliminar" de la fila al cancelarla.
    const deleteRadio = entries(page)
      .first()
      .getByRole("button", { name: "Eliminar Radio", exact: true })
    const confirmYes = page.getByRole("button", {
      name: "Sí, eliminar",
      exact: true,
    })
    await deleteRadio.click()
    await expect(confirmYes).toBeFocused()
    await page.getByRole("button", { name: "Cancelar", exact: true }).click()
    await expect(deleteRadio).toBeFocused()
    await expect(entries(page)).toHaveCount(1)
    expect(await historyCount(api)).toBe(1)

    // "Sí, eliminar" lo quita de la sección y del almacenamiento.
    await deleteRadio.click()
    await confirmYes.click()
    await expect(entries(page)).toHaveCount(0)
    await expect(list).toBeFocused()
    expect(await historyCount(api)).toBe(0)
  })

  test("S11 edad con fecha de nacimiento: a los 7 años (≈1997)", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await setBirthDate(page, "1990-03-15", "15/03/1990")
    await openSection(page, "/perfil/cirugias")
    await startAdd(page)
    await textbox(page, /^nombre/i).fill("Amigdalectomía")
    await page.getByLabel("Edad que tenías").fill("7")
    await save(page)

    await expect(entries(page)).toHaveCount(1)
    await expect(entries(page).first()).toContainText("a los 7 años (≈1997)")
  })

  test("S12 etapa escolar con fecha de nacimiento: en la primaria (≈1996–2001)", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await setBirthDate(page, "1990-03-15", "15/03/1990")
    await openSection(page, "/perfil/pasadas")
    await startAdd(page)
    await choose(page, /condición/i, "Varicela")
    await whenChip(page, "En la primaria")
    await save(page)

    await expect(entries(page)).toHaveCount(1)
    await expect(entries(page).first()).toContainText(
      "en la primaria (≈1996–2001)",
    )
  })

  test("S13 sin fecha de nacimiento: a los 10 años sin año aproximado", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openSection(page, "/perfil/fracturas")
    await startAdd(page)
    await textbox(page, /^qué hueso o lesión/i).fill("Radio")
    await page.getByLabel("Edad que tenías").fill("10")
    await save(page)

    await expect(entries(page)).toHaveCount(1)
    await expect(entries(page).first()).toContainText("a los 10 años")
    await expect(entries(page).first()).not.toContainText("≈")
  })

  test("S13b edad imposible: sin año aproximado futuro, error junto a '¿Cuándo?' con el foco ahí", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setBirthDate(page, "1990-03-15", "15/03/1990")
    await openSection(page, "/perfil/fracturas")
    await startAdd(page)
    await textbox(page, /^qué hueso o lesión/i).fill("Radio")
    const age = page.getByLabel("Edad que tenías")

    // Una edad posible muestra la pista; una que cae en el futuro, no.
    await age.fill("10")
    await expect(page.getByText("Año aproximado: 2000")).toBeVisible()
    await age.fill("90")
    await expect(page.getByText(/Año aproximado/)).toHaveCount(0)

    // El servidor la rechaza: el mensaje queda junto al campo, que recibe
    // el foco y lo lleva como descripción.
    await save(page)
    await expect(age).toBeFocused()
    await expect(age).toHaveAttribute("aria-invalid", "true")
    await expect(age).toHaveAccessibleDescription(
      "La edad no puede ser mayor que tu edad actual",
    )
    expect(await historyCount(api)).toBe(0)
  })

  test("S14 el año se recalcula al corregir la fecha de nacimiento", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await setBirthDate(page, "1990-03-15", "15/03/1990")
    await seedEntry(api, {
      section: "surgeries",
      name: "Amigdalectomía",
      when: { kind: "age", value: 7 },
    })
    await openSection(page, "/perfil/cirugias")
    await expect(entries(page).first()).toContainText("a los 7 años (≈1997)")

    await setBirthDate(page, "1992-01-01", "01/01/1992")
    await openSection(page, "/perfil/cirugias")
    await expect(entries(page).first()).toContainText("a los 7 años (≈1999)")
  })

  test("S16 marcar 'No he tenido ninguna' en cirugías", async ({
    page,
    request,
  }) => {
    await freshPatient(page, request)
    await openSection(page, "/perfil/cirugias")
    await page.getByRole("button", { name: "No he tenido ninguna" }).click()
    await expect(page.getByText("Ninguna", { exact: true })).toBeVisible()
    await expect(page.getByTestId("history-entries")).toBeFocused()

    await page.goto("/perfil")
    await expect(card(page, "surgeries")).toContainText("Ninguna")
  })

  test("S18 agregar una transfusión quita «ninguna» y lo avisa", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedNone(api, "transfusions")
    await openSection(page, "/perfil/transfusiones")
    await expect(page.getByText("Ninguna", { exact: true })).toBeVisible()

    await startAdd(page)
    await textbox(page, /^motivo/i).fill("Parto")
    await save(page)
    await expect(
      page.getByText("Guardado. La sección ya no dice «ninguna»."),
    ).toBeVisible()
    await expect(entries(page)).toHaveCount(1)

    await page.goto("/perfil")
    await expect(
      card(page, "transfusions").getByText("1 registro", { exact: true }),
    ).toBeVisible()
    await expect(card(page, "transfusions")).not.toContainText("Ninguna")
  })

  test("S19 'Deshacer' devuelve cirugías a 'Sin llenar'", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await seedNone(api, "surgeries")
    await openSection(page, "/perfil/cirugias")
    await expect(page.getByText("Ninguna", { exact: true })).toBeVisible()

    await page.getByRole("button", { name: "Deshacer", exact: true }).click()
    await expect(page.getByText("Sin llenar", { exact: true })).toBeVisible()
    await expect(page.getByTestId("history-entries")).toBeFocused()

    await page.goto("/perfil")
    await expect(card(page, "surgeries")).toContainText("Sin llenar")
  })

  test("S20 grupo sanguíneo O+ corregido a 'No lo sé' persiste al recargar", async ({
    page,
    request,
  }) => {
    const api = await freshPatient(page, request)
    await openSection(page, "/perfil/transfusiones")
    const group = page.getByRole("group", { name: "Grupo sanguíneo" })
    const oPlus = group.getByRole("button", { name: "O positivo", exact: true })
    await expect(oPlus).toHaveText("O+")
    const unknown = group.getByRole("button", { name: "No lo sé", exact: true })

    await oPlus.click()
    await expect(oPlus).toHaveAttribute("aria-pressed", "true")
    await unknown.click()
    await expect(unknown).toHaveAttribute("aria-pressed", "true")

    // El perfil guarda "No lo sé" (blood_type "unknown") antes de recargar.
    await expect
      .poll(async () => {
        const res = await api.request.get(`${API}/profile`, {
          headers: api.headers,
        })
        return (await res.json()).blood_type
      })
      .toBe("unknown")

    await page.reload()
    const groupAfter = page.getByRole("group", { name: "Grupo sanguíneo" })
    await expect(
      groupAfter.getByRole("button", { name: "No lo sé", exact: true }),
    ).toHaveAttribute("aria-pressed", "true")
    await expect(
      groupAfter.getByRole("button", { name: "O positivo", exact: true }),
    ).not.toHaveAttribute("aria-pressed", "true")
  })
})
