import { expect, type Locator, type Page, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import { randomEmail, randomPassword } from "./utils/random"
import { logInUser } from "./utils/user"

test.use({ storageState: { cookies: [], origins: [] } })

// --- Helpers compartidos del spec -----------------------------------------

/**
 * Usuario fresco: alta por API privada, login por UI, acepta el consentimiento
 * (gate en "/") y navega a /expediente.
 */
async function freshUserOnExpediente(page: Page) {
  const email = randomEmail()
  const password = randomPassword()
  await createUser({ email, password })
  await logInUser(page, email, password)

  const consentButton = page.getByTestId("consent-accept-button")
  await expect(consentButton).toBeVisible()
  await consentButton.click()
  await expect(consentButton).not.toBeVisible()

  await page.goto("/expediente")
}

async function addDiagnosis(
  page: Page,
  {
    title = "Hipotiroidismo subclínico",
    date = "2026-09-30",
    professional = "Dra. Islas (endocrinología)",
    notes = "TSH 6.8; repetir perfil en 3 meses",
  } = {},
) {
  await page.getByRole("button", { name: "Agregar diagnóstico" }).click()
  await page.getByLabel("Diagnóstico").fill(title)
  await page.getByLabel("Fecha").fill(date)
  await page.getByLabel("Profesional").fill(professional)
  await page.getByLabel("Notas").fill(notes)
  await page.getByRole("button", { name: "Guardar" }).click()
}

type Medicine = { name: string; dose: string; frequency?: string }

/**
 * Rellena la fila de medicina `index` del diálogo de captura. Las filas llevan
 * los campos "Medicina", "Dosis e indicación" y "Frecuencia (opcional)"
 * (contrato: product/prototipos/receta-primero.html).
 */
async function fillMedicineRow(dialog: Locator, index: number, med: Medicine) {
  await dialog.getByLabel("Medicina", { exact: true }).nth(index).fill(med.name)
  await dialog.getByLabel("Dosis e indicación").nth(index).fill(med.dose)
  if (med.frequency !== undefined) {
    await dialog
      .getByLabel(/Frecuencia/)
      .nth(index)
      .fill(med.frequency)
  }
}

/**
 * Captura una receta con "Registrar receta" (modelo nuevo: medicinas[],
 * diagnóstico opcional, sin vigencia) y la guarda con "Guardar receta".
 * (Renombre del gate humano: el botón ya no se llama "A mano".)
 */
async function addPrescription(
  page: Page,
  {
    doctor = "Dra. Islas (endocrinología)",
    date = "2026-10-12",
    medicines = [
      {
        name: "Levotiroxina 50 µg",
        dose: "1 tableta en ayunas",
        frequency: "cada 8 h",
      },
      {
        name: "Omeprazol 20 mg",
        dose: "1 cápsula antes del desayuno por 14 días",
      },
    ] as Medicine[],
    diagnosis = "",
  } = {},
) {
  await page.getByRole("button", { name: "Registrar receta" }).click()
  const dialog = page.getByRole("dialog")
  await expect(dialog).toBeVisible()

  await dialog.getByLabel("Médico que la expide").fill(doctor)
  await dialog.getByLabel("Fecha de la receta").fill(date)
  for (let i = 0; i < medicines.length; i++) {
    if (i > 0) {
      await dialog
        .getByRole("button", { name: "+ Agregar otra medicina" })
        .click()
    }
    await fillMedicineRow(dialog, i, medicines[i])
  }
  if (diagnosis) {
    await dialog.getByLabel(/Diagnóstico/).fill(diagnosis)
  }
  await dialog.getByRole("button", { name: "Guardar receta" }).click()
}

/** La fila (role=row) del registro que contiene el texto dado. */
function recordRow(page: Page, recordText: string): Locator {
  return page.getByRole("row").filter({ hasText: recordText })
}

/**
 * Dispara una acción del menú o botones de un registro ("Editar registro",
 * "Eliminar registro"): abre el menú de acciones (botón accesible
 * "Abrir menú de acciones") DENTRO de la fila que contiene el texto del
 * registro y elige el menuitem por nombre.
 */
async function clickRecordAction(
  page: Page,
  recordText: string,
  action: string | RegExp,
) {
  const row = recordRow(page, recordText)
  await row.getByRole("button", { name: "Abrir menú de acciones" }).click()
  await page.getByRole("menuitem", { name: action }).click()
}

/**
 * Como clickRecordAction, pero acepta la acción como botón directo en la fila
 * (patrón del prototipo: "Archivar (tratamiento terminado)" es un botón de la
 * tarjeta) o como menuitem del menú de acciones de la fila.
 */
async function clickRecordActionFlexible(
  page: Page,
  recordText: string,
  action: string | RegExp,
) {
  const row = recordRow(page, recordText)
  const inline = row.getByRole("button", { name: action })
  if (
    await inline
      .first()
      .isVisible()
      .catch(() => false)
  ) {
    await inline.first().click()
    return
  }
  await clickRecordAction(page, recordText, action)
}

/**
 * Dispara una acción de un adjunto ("Descargar", "Eliminar adjunto"): el botón
 * se localiza DENTRO del elemento de lista que contiene el nombre del archivo.
 */
async function clickAttachmentAction(
  page: Page,
  fileName: string,
  action: string,
) {
  const item = page.locator("li").filter({ hasText: fileName })
  await item.getByRole("button", { name: action }).click()
}

/** Sube un archivo en la sección "Adjuntos" vía el input de archivo oculto. */
async function uploadAttachment(
  page: Page,
  file: { name: string; mimeType: string; buffer: Buffer },
) {
  await expect(page.getByText("Adjuntos")).toBeVisible()
  await page.locator('input[type="file"]').setInputFiles(file)
}

/** Abre el panel de adjuntos de un registro si la sección no está ya visible. */
async function openAttachmentsPanel(page: Page, recordText: string) {
  const section = page.getByText("Adjuntos")
  if (
    !(await section
      .first()
      .isVisible()
      .catch(() => false))
  ) {
    await page.getByText(recordText).click()
  }
  await expect(page.getByText("Adjuntos")).toBeVisible()
}

/** PNG 1x1 válido (magic bytes reales): el servidor valida por contenido. */
const PNG_1X1 = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
  "base64",
)

// --- Helpers del delta del gate humano (2026-10-18) -------------------------

/**
 * Simula el cambio de pestaña/pérdida de foco del navegador y ASEGURA que el
 * refetch real de la lista ocurre (hallazgo C1/T1: la versión anterior
 * despachaba visibilitychange en document — TanStack Query escucha en
 * window — y no esperaba el clamp de staleTime, así que los tests pasaban
 * aun con la regresión presente). Receta verificada:
 *  (a) esperar >1000 ms ANTES de disparar (useSuspenseQuery fuerza
 *      staleTime ≥ 1000 ms; si la query no está stale no hay refetch),
 *  (b) despachar visibilitychange en WINDOW,
 *  (c) asertar el refetch real esperando el GET de /api/v1/health-records.
 */
async function simulateTabSwitch(page: Page) {
  await page.waitForTimeout(1100)
  const refetch = page.waitForResponse(
    (response) =>
      response.request().method() === "GET" &&
      /\/api\/v1\/health-records\/?(\?|$)/.test(response.url()),
  )
  await page.evaluate(() => {
    window.dispatchEvent(new Event("visibilitychange"))
  })
  await refetch
}

/**
 * Abre el detalle (solo lectura) de un registro haciendo clic en su texto en
 * la lista. Contrato del delta: la consulta abre una vista de solo lectura
 * con el mismo layout del modal.
 */
async function openRecordDetail(
  page: Page,
  recordText: string,
): Promise<Locator> {
  await page.getByText(recordText).first().click()
  const detail = page.getByRole("dialog")
  await expect(detail).toBeVisible()
  return detail
}

/**
 * Llega al formulario EDITABLE de una receta por el camino deliberado del
 * delta: detalle solo lectura → botón "Editar" → confirmación ("Sí, editar")
 * → formulario con "Guardar receta".
 */
async function openPrescriptionEditForm(
  page: Page,
  recordText: string,
): Promise<Locator> {
  const detail = await openRecordDetail(page, recordText)
  await detail.getByRole("button", { name: "Editar", exact: true }).click()
  await page.getByRole("button", { name: "Sí, editar" }).click()
  const form = page
    .getByRole("dialog")
    .filter({ has: page.getByRole("button", { name: "Guardar receta" }) })
  await expect(form).toBeVisible()
  return form
}

/**
 * Escribe dos líneas en el campo de notas separadas por Enter (el Enter debe
 * insertar salto de línea, no enviar el formulario).
 */
async function typeTwoLineNotes(notes: Locator) {
  await notes.click()
  await notes.pressSequentially("No tomar alcohol")
  await notes.press("Enter")
  await notes.pressSequentially("Correr 1 hora 3 veces a la semana")
}

/**
 * El botón placeholder ("Dictar" / "Escanear") está visible, DESHABILITADO y
 * anuncia "Próximamente" de forma accesible (aria-label, title,
 * aria-describedby o texto propio).
 */
async function expectComingSoonPlaceholder(dialog: Locator, name: RegExp) {
  const button = dialog.getByRole("button", { name })
  await expect(button).toBeVisible()
  await expect(button).toBeDisabled()
  const announcesComingSoon = await button.evaluate((el) => {
    const direct =
      (el.getAttribute("aria-label") ?? "") + (el.getAttribute("title") ?? "")
    if (direct.includes("Próximamente")) return true
    const describedBy = el.getAttribute("aria-describedby")
    if (describedBy) {
      const described = describedBy
        .split(/\s+/)
        .map((id) => document.getElementById(id)?.textContent ?? "")
        .join(" ")
      if (described.includes("Próximamente")) return true
    }
    return el.textContent?.includes("Próximamente") ?? false
  })
  expect(announcesComingSoon).toBe(true)
}

// --- Escenarios ------------------------------------------------------------

test.describe("Expediente — receta a la mexicana", () => {
  test.beforeEach(async ({ page }) => {
    await freshUserOnExpediente(page)
  })

  test("AC1: capturar a mano una receta con 2 medicinas (una sin frecuencia) y sin diagnóstico la muestra en la lista", async ({
    page,
  }) => {
    await addPrescription(page, {
      doctor: "Dra. Islas (endocrinología)",
      date: "2026-10-12",
      medicines: [
        {
          name: "Levotiroxina 50 µg",
          dose: "1 tableta en ayunas",
          frequency: "cada 8 h",
        },
        {
          name: "Omeprazol 20 mg",
          dose: "1 cápsula antes del desayuno por 14 días",
        },
      ],
    })

    await expect(page.getByText("Receta guardada.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    const row = recordRow(page, "Levotiroxina 50 µg")
    await expect(row).toBeVisible()
    await expect(row.getByText("Omeprazol 20 mg")).toBeVisible()
    await expect(row.getByText("cada 8 h")).toBeVisible()
    await expect(row.getByText("Dra. Islas (endocrinología)")).toBeVisible()
    // Fecha en formato es-MX dd/mm/aaaa.
    await expect(row.getByText("12/10/2026")).toBeVisible()
  })

  test("AC2: una receta con diagnóstico opcional muestra el diagnóstico", async ({
    page,
  }) => {
    await addPrescription(page, {
      doctor: "Dr. Ramos (medicina general)",
      date: "2026-10-05",
      medicines: [
        {
          name: "Amoxicilina 500 mg",
          dose: "1 cápsula hasta terminarlas",
          frequency: "cada 12 h",
        },
      ],
      diagnosis: "faringitis",
    })

    await expect(page.getByText("Receta guardada.")).toBeVisible()
    const row = recordRow(page, "Amoxicilina 500 mg")
    await expect(row).toBeVisible()
    await expect(row.getByText(/faringitis/)).toBeVisible()
  })

  test("AC3: guardar sin ninguna medicina avisa en es-MX y no crea la receta", async ({
    page,
  }) => {
    await page.getByRole("button", { name: "Registrar receta" }).click()
    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await dialog.getByLabel("Médico que la expide").fill("Dr. Sin Medicinas")
    await dialog.getByLabel("Fecha de la receta").fill("2026-10-12")
    // Ninguna medicina capturada.
    await dialog.getByRole("button", { name: "Guardar receta" }).click()

    await expect(page.getByText("Agrega al menos una medicina.")).toBeVisible()
    // El diálogo sigue abierto: nada se guardó.
    await expect(dialog).toBeVisible()

    await dialog.getByRole("button", { name: "Cancelar" }).click()
    await expect(dialog).not.toBeVisible()
    await expect(page.getByText("Dr. Sin Medicinas")).not.toBeVisible()
  })

  test("AC4: corregir una receta — cambiar frecuencia, quitar una medicina y agregar otra", async ({
    page,
  }) => {
    await addPrescription(page, {
      medicines: [
        {
          name: "Levotiroxina 50 µg",
          dose: "1 tableta en ayunas",
          frequency: "cada 24 h",
        },
        {
          name: "Omeprazol 20 mg",
          dose: "1 cápsula antes del desayuno por 14 días",
        },
      ],
    })
    await expect(page.getByText("Receta guardada.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    await clickRecordAction(page, "Levotiroxina 50 µg", "Editar registro")
    // Editar desde el menú ⋯ pasa por la MISMA confirmación que el camino
    // del detalle (hallazgo C7).
    await page.getByRole("button", { name: "Sí, editar" }).click()
    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    // Cambiar la frecuencia de la Levotiroxina (fila 0).
    await dialog
      .getByLabel(/Frecuencia/)
      .nth(0)
      .fill("cada 24 h, lunes a sábado")
    // Quitar el Omeprazol (fila 1).
    await dialog.getByRole("button", { name: "Quitar medicina" }).nth(1).click()
    // Agregar el Ibuprofeno como nueva fila.
    await dialog
      .getByRole("button", { name: "+ Agregar otra medicina" })
      .click()
    await fillMedicineRow(dialog, 1, {
      name: "Ibuprofeno 400 mg",
      dose: "1 tableta por 5 días",
      frequency: "cada 8 h",
    })
    await dialog.getByRole("button", { name: "Guardar receta" }).click()
    await expect(dialog).not.toBeVisible()

    const row = recordRow(page, "Levotiroxina 50 µg")
    await expect(row.getByText("cada 24 h, lunes a sábado")).toBeVisible()
    await expect(row.getByText("Ibuprofeno 400 mg")).toBeVisible()
    await expect(page.getByText("Omeprazol 20 mg")).not.toBeVisible()
  })

  test("AC5: archivar una receta la mueve a 'Archivadas' y desarchivar la devuelve a activas", async ({
    page,
  }) => {
    await addPrescription(page, {
      medicines: [
        {
          name: "Paracetamol 500 mg",
          dose: "1 tableta por 3 días",
          frequency: "cada 8 h",
        },
      ],
    })
    await expect(page.getByText("Receta guardada.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    await expect(
      page.getByRole("heading", { name: "Archivadas" }),
    ).not.toBeVisible()

    await clickRecordActionFlexible(
      page,
      "Paracetamol 500 mg",
      "Archivar (tratamiento terminado)",
    )

    // Aparece la sección "Archivadas" y la receta queda marcada como archivada.
    await expect(
      page.getByRole("heading", { name: "Archivadas" }),
    ).toBeVisible()
    const row = recordRow(page, "Paracetamol 500 mg")
    await expect(row).toBeVisible()
    await expect(row.getByText(/Archivada/)).toBeVisible()
    // Ya no ofrece archivarla de nuevo: salió de las activas.
    await expect(
      row.getByRole("button", { name: "Archivar (tratamiento terminado)" }),
    ).not.toBeVisible()

    // Desarchivar la devuelve a activas sin pérdida de datos.
    await clickRecordActionFlexible(page, "Paracetamol 500 mg", /Desarchivar/)
    await expect(
      page.getByRole("heading", { name: "Archivadas" }),
    ).not.toBeVisible()
    const activeRow = recordRow(page, "Paracetamol 500 mg")
    await expect(activeRow).toBeVisible()
    await expect(activeRow.getByText("cada 8 h")).toBeVisible()
    await expect(activeRow.getByText(/Archivada/)).not.toBeVisible()
  })

  test("AC6: un diagnóstico suelto nace con estado 'sin confirmar'", async ({
    page,
  }) => {
    await addDiagnosis(page)

    await expect(page.getByText("Diagnóstico registrado.")).toBeVisible()
    const row = recordRow(page, "Hipotiroidismo subclínico")
    await expect(row).toBeVisible()
    await expect(row.getByText("sin confirmar")).toBeVisible()
  })

  test("AC7: adjuntar la foto de la receta y verla listada (AC-4)", async ({
    page,
  }) => {
    await addPrescription(page, {
      medicines: [
        {
          name: "Levotiroxina 50 µg",
          dose: "1 tableta en ayunas",
          frequency: "cada 24 h",
        },
      ],
    })
    await expect(page.getByText("Receta guardada.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    await openAttachmentsPanel(page, "Levotiroxina 50 µg")

    await uploadAttachment(page, {
      name: "receta-dra-islas.png",
      mimeType: "image/png",
      buffer: PNG_1X1,
    })

    await expect(page.getByText("Adjunto agregado.")).toBeVisible()
    await expect(page.getByText("receta-dra-islas.png")).toBeVisible()
  })

  test("adjuntos: un PDF en un diagnóstico se adjunta y se descarga", async ({
    page,
  }) => {
    await addDiagnosis(page)
    await expect(page.getByText("Diagnóstico registrado.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    await openAttachmentsPanel(page, "Hipotiroidismo subclínico")

    const pdfBuffer = Buffer.from(
      "%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n",
    )
    await uploadAttachment(page, {
      name: "perfil-tiroideo.pdf",
      mimeType: "application/pdf",
      buffer: pdfBuffer,
    })

    await expect(page.getByText("Adjunto agregado.")).toBeVisible()
    await expect(page.getByText("perfil-tiroideo.pdf")).toBeVisible()

    const downloadPromise = page.waitForEvent("download")
    await clickAttachmentAction(page, "perfil-tiroideo.pdf", "Descargar")
    const download = await downloadPromise
    expect(download.suggestedFilename()).toBe("perfil-tiroideo.pdf")
  })

  test("adjuntos: un archivo que no es PDF/JPEG/PNG se rechaza y no se lista", async ({
    page,
  }) => {
    await addDiagnosis(page)
    await expect(page.getByText("Diagnóstico registrado.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    await openAttachmentsPanel(page, "Hipotiroidismo subclínico")

    // Bytes de ejecutable (MZ…) con mimeType de PDF: el servidor rechaza por
    // magic bytes, no por extensión ni por content-type declarado.
    const exeBuffer = Buffer.from(
      "MZ\x90\x00\x03\x00\x00\x00programa",
      "latin1",
    )
    await uploadAttachment(page, {
      name: "reporte.exe",
      mimeType: "application/pdf",
      buffer: exeBuffer,
    })

    await expect(
      page.getByText("Tipo de archivo no permitido (solo PDF, JPEG o PNG)"),
    ).toBeVisible()
    await expect(page.getByText("reporte.exe")).not.toBeVisible()
  })

  // Recuperado de main (hallazgo T5): el rewrite del spec lo había tirado.
  test("eliminar un registro pide confirmación y lo quita de la lista", async ({
    page,
  }) => {
    await addDiagnosis(page)
    await expect(page.getByText("Diagnóstico registrado.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    await clickRecordAction(
      page,
      "Hipotiroidismo subclínico",
      "Eliminar registro",
    )

    await expect(
      page.getByText(
        "¿Seguro que quieres eliminar este registro? Se eliminarán también sus adjuntos.",
      ),
    ).toBeVisible()
    await page.getByRole("button", { name: "Eliminar", exact: true }).click()

    await expect(page.getByText("Registro eliminado.")).toBeVisible()
    await expect(page.getByText("Hipotiroidismo subclínico")).not.toBeVisible()
  })

  // --- Delta del gate humano (2026-10-18): protección del trabajo y los datos

  test("D1: el modal sobrevive al cambio de pestaña — captura", async ({
    page,
  }) => {
    // Lista ya cargada: una receta existente provoca el refetch al foco.
    await addPrescription(page, {
      medicines: [
        {
          name: "Paracetamol 500 mg",
          dose: "1 tableta por 3 días",
          frequency: "cada 8 h",
        },
      ],
    })
    await expect(page.getByText("Receta guardada.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    await page.getByRole("button", { name: "Registrar receta" }).click()
    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()
    await dialog.getByLabel("Médico que la expide").fill("Dra. Foco Perdido")
    await fillMedicineRow(dialog, 0, {
      name: "Ibuprofeno 400 mg",
      dose: "1 tableta por 5 días",
    })

    await simulateTabSwitch(page)

    // El modal sigue abierto con todo lo escrito intacto.
    await expect(dialog).toBeVisible()
    await expect(dialog.getByLabel("Médico que la expide")).toHaveValue(
      "Dra. Foco Perdido",
    )
    await expect(
      dialog.getByLabel("Medicina", { exact: true }).nth(0),
    ).toHaveValue("Ibuprofeno 400 mg")
  })

  test("D1: el modal sobrevive al cambio de pestaña — edición", async ({
    page,
  }) => {
    await addPrescription(page, {
      medicines: [
        {
          name: "Levotiroxina 50 µg",
          dose: "1 tableta en ayunas",
          frequency: "cada 24 h",
        },
      ],
    })
    await expect(page.getByText("Receta guardada.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    const form = await openPrescriptionEditForm(page, "Levotiroxina 50 µg")
    await form
      .getByLabel(/Frecuencia/)
      .nth(0)
      .fill("cada 24 h, lunes a sábado")

    await simulateTabSwitch(page)

    // El caso reportado por Saúl Pérez: la edición no se pierde.
    await expect(form).toBeVisible()
    await expect(form.getByLabel(/Frecuencia/).nth(0)).toHaveValue(
      "cada 24 h, lunes a sábado",
    )
  })

  test("D2: notas multilínea con Enter", async ({ page }) => {
    // --- Receta -------------------------------------------------------------
    await page.getByRole("button", { name: "Registrar receta" }).click()
    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()
    await dialog
      .getByLabel("Médico que la expide")
      .fill("Dra. Islas (endocrinología)")
    await dialog.getByLabel("Fecha de la receta").fill("2026-10-12")
    await fillMedicineRow(dialog, 0, {
      name: "Metformina 850 mg",
      dose: "1 tableta con la cena",
    })
    await typeTwoLineNotes(dialog.getByLabel(/Notas/))

    // El Enter NO envió el formulario.
    await expect(dialog).toBeVisible()
    await expect(page.getByText("Receta guardada.")).not.toBeVisible()

    await dialog.getByRole("button", { name: "Guardar receta" }).click()
    await expect(page.getByText("Receta guardada.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    // Al consultar el detalle, las dos líneas se ven como líneas separadas.
    const detail = await openRecordDetail(page, "Metformina 850 mg")
    const recetaNotes = await detail
      .getByText(/No tomar alcohol/)
      .first()
      .innerText()
    expect(recetaNotes).toMatch(
      /No tomar alcohol\s*\n\s*Correr 1 hora 3 veces a la semana/,
    )
    await page.keyboard.press("Escape")
    await expect(page.getByRole("dialog")).not.toBeVisible()

    // --- Diagnóstico ----------------------------------------------------------
    await page.getByRole("button", { name: "Agregar diagnóstico" }).click()
    const dxDialog = page.getByRole("dialog")
    await expect(dxDialog).toBeVisible()
    await dxDialog.getByLabel("Diagnóstico").fill("Faringitis aguda")
    await dxDialog.getByLabel("Fecha").fill("2026-10-01")
    await dxDialog
      .getByLabel("Profesional")
      .fill("Dr. Ramos (medicina general)")
    await typeTwoLineNotes(dxDialog.getByLabel("Notas"))

    await expect(dxDialog).toBeVisible()
    await expect(page.getByText("Diagnóstico registrado.")).not.toBeVisible()

    await dxDialog.getByRole("button", { name: "Guardar" }).click()
    await expect(page.getByText("Diagnóstico registrado.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    await openRecordDetail(page, "Faringitis aguda")
    const dxNotes = await page
      .getByRole("dialog")
      .getByText(/No tomar alcohol/)
      .first()
      .innerText()
    expect(dxNotes).toMatch(
      /No tomar alcohol\s*\n\s*Correr 1 hora 3 veces a la semana/,
    )
  })

  test("D3: detalle solo lectura + Editar con confirmación", async ({
    page,
  }) => {
    await addPrescription(page, {
      doctor: "Dra. Islas (endocrinología)",
      date: "2026-10-12",
      medicines: [
        {
          name: "Levotiroxina 50 µg",
          dose: "1 tableta en ayunas",
          frequency: "cada 24 h",
        },
      ],
      diagnosis: "Hipotiroidismo subclínico",
    })
    await expect(page.getByText("Receta guardada.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    // El clic NO debe pedir subir archivo (comportamiento viejo reportado).
    let fileChooserOpened = false
    page.on("filechooser", () => {
      fileChooserOpened = true
    })

    const detail = await openRecordDetail(page, "Levotiroxina 50 µg")

    // Datos completos en solo lectura.
    await expect(detail.getByText("Dra. Islas (endocrinología)")).toBeVisible()
    await expect(detail.getByText("12/10/2026")).toBeVisible()
    await expect(detail.getByText("Levotiroxina 50 µg")).toBeVisible()
    await expect(detail.getByText("1 tableta en ayunas")).toBeVisible()
    await expect(detail.getByText("cada 24 h")).toBeVisible()
    await expect(detail.getByText(/Hipotiroidismo subclínico/)).toBeVisible()

    // No es el formulario editable y no pidió subir archivo. La aserción del
    // filechooser deja pasar un margen determinista para que un chooser
    // tardío (la regresión original) la haga fallar (hallazgo C2, parte test).
    await expect(detail.getByText("Consulta de solo lectura.")).toBeVisible()
    await expect(
      detail.getByRole("button", { name: "Guardar receta" }),
    ).not.toBeVisible()
    await page.waitForTimeout(500)
    expect(fileChooserOpened).toBe(false)

    // Editar es deliberado: botón "Editar" + confirmación previa.
    await detail.getByRole("button", { name: "Editar", exact: true }).click()
    const confirm = page.getByRole("button", { name: "Sí, editar" })
    await expect(confirm).toBeVisible()
    // Antes de confirmar todavía no hay formulario editable.
    await expect(
      page.getByRole("button", { name: "Guardar receta" }),
    ).not.toBeVisible()

    await confirm.click()
    const form = page
      .getByRole("dialog")
      .filter({ has: page.getByRole("button", { name: "Guardar receta" }) })
    await expect(form).toBeVisible()
    await expect(form.getByLabel("Médico que la expide")).toHaveValue(
      "Dra. Islas (endocrinología)",
    )
  })

  test("D4: crear receta con adjunto opcional", async ({ page }) => {
    // Con adjunto: el control vive DENTRO del formulario de creación.
    await page.getByRole("button", { name: "Registrar receta" }).click()
    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()
    await dialog
      .getByLabel("Médico que la expide")
      .fill("Dra. Islas (endocrinología)")
    await dialog.getByLabel("Fecha de la receta").fill("2026-10-12")
    await fillMedicineRow(dialog, 0, {
      name: "Metformina 850 mg",
      dose: "1 tableta con la cena",
    })
    await dialog.locator('input[type="file"]').setInputFiles({
      name: "receta-dra-islas.png",
      mimeType: "image/png",
      buffer: PNG_1X1,
    })
    await dialog.getByRole("button", { name: "Guardar receta" }).click()

    await expect(page.getByText("Receta guardada.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()
    await expect(recordRow(page, "Metformina 850 mg")).toBeVisible()

    // El adjunto aparece listado en el detalle de la receta.
    const detail = await openRecordDetail(page, "Metformina 850 mg")
    await expect(detail.getByText("receta-dra-islas.png")).toBeVisible()
    await page.keyboard.press("Escape")
    await expect(page.getByRole("dialog")).not.toBeVisible()

    // Sin adjunto: la receta se guarda igual.
    await addPrescription(page, {
      doctor: "Dr. Ramos (medicina general)",
      date: "2026-10-05",
      medicines: [{ name: "Loratadina 10 mg", dose: "1 tableta al día" }],
    })
    await expect(recordRow(page, "Loratadina 10 mg")).toBeVisible()
  })

  test("renombre: 'Registrar receta' abre el modal con 'Dictar' y 'Escanear' deshabilitados como 'Próximamente'", async ({
    page,
  }) => {
    // El botón viejo "A mano" ya no existe.
    await expect(page.getByRole("button", { name: "A mano" })).not.toBeVisible()

    await page.getByRole("button", { name: "Registrar receta" }).click()
    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    // Placeholders de la escalera de captura: visibles y deshabilitados.
    await expectComingSoonPlaceholder(dialog, /Dictar/)
    await expectComingSoonPlaceholder(dialog, /Escanear/)

    // El formulario manual sigue siendo utilizable en el mismo modal.
    await expect(dialog.getByLabel("Médico que la expide")).toBeVisible()
  })
})
