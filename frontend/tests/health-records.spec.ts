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
    await dialog.getByLabel(/Frecuencia/).nth(index).fill(med.frequency)
  }
}

/**
 * Captura una receta "A mano" (modelo nuevo: medicinas[], diagnóstico
 * opcional, sin vigencia) y la guarda con "Guardar receta".
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
  await page.getByRole("button", { name: "A mano" }).click()
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
    await page.getByRole("button", { name: "A mano" }).click()
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
    await dialog.getByRole("button", { name: "+ Agregar otra medicina" }).click()
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
})
