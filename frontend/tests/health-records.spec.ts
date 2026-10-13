import { expect, type Page, test } from "@playwright/test"
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

async function addPrescription(
  page: Page,
  {
    medication = "Levotiroxina 50 µg",
    date = "2026-10-01",
    dosage = "1 tableta en ayunas cada 24 h",
    validFrom = "2026-10-01",
    validUntil = "2026-12-30",
  } = {},
) {
  await page.getByRole("button", { name: "Agregar receta" }).click()
  await page.getByLabel("Medicamento").fill(medication)
  await page.getByLabel("Fecha").fill(date)
  await page.getByLabel("Dosis").fill(dosage)
  await page.getByLabel("Inicio de vigencia").fill(validFrom)
  await page.getByLabel("Fin de vigencia").fill(validUntil)
  await page.getByRole("button", { name: "Guardar" }).click()
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
  action: string,
) {
  const row = page.getByRole("row").filter({ hasText: recordText })
  await row.getByRole("button", { name: "Abrir menú de acciones" }).click()
  await page.getByRole("menuitem", { name: action }).click()
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

// --- Escenarios ------------------------------------------------------------

test.describe("Expediente — registros clínicos", () => {
  test.beforeEach(async ({ page }) => {
    await freshUserOnExpediente(page)
  })

  test("AC1: agregar un diagnóstico lo registra y lo muestra en la lista", async ({
    page,
  }) => {
    await expect(
      page.getByRole("heading", { name: "Expediente" }),
    ).toBeVisible()
    await expect(
      page.getByText("Registra tus diagnósticos, recetas y resultados"),
    ).toBeVisible()
    await expect(page.getByText("Aún no tienes registros.")).toBeVisible()

    await addDiagnosis(page)

    await expect(page.getByText("Diagnóstico registrado.")).toBeVisible()
    await expect(page.getByText("Hipotiroidismo subclínico")).toBeVisible()
    await expect(
      page.getByText("Diagnóstico", { exact: true }).first(),
    ).toBeVisible()
  })

  test("AC2: agregar una receta la registra y la muestra en la lista", async ({
    page,
  }) => {
    await addPrescription(page)

    await expect(page.getByText("Receta registrada.")).toBeVisible()
    await expect(page.getByText("Levotiroxina 50 µg")).toBeVisible()
    await expect(
      page.getByText("Receta", { exact: true }).first(),
    ).toBeVisible()
  })

  test("AC3: corregir la dosis de una receta persiste el cambio", async ({
    page,
  }) => {
    await addPrescription(page)
    await expect(page.getByText("Receta registrada.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    const newDosage = "1 tableta en ayunas cada 24 h, lunes a sábado"
    await clickRecordAction(page, "Levotiroxina 50 µg", "Editar registro")
    await page.getByLabel("Dosis").fill(newDosage)
    await page.getByRole("button", { name: "Guardar" }).click()

    await expect(page.getByText("Registro actualizado.")).toBeVisible()
    await expect(page.getByRole("dialog")).not.toBeVisible()

    // Reabrir el registro: la dosis nueva es la que quedó guardada.
    await clickRecordAction(page, "Levotiroxina 50 µg", "Editar registro")
    await expect(page.getByLabel("Dosis")).toHaveValue(newDosage)
  })

  test("AC4: eliminar un registro pide confirmación y lo quita de la lista", async ({
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

  test("AC5: adjuntar un PDF a un diagnóstico y descargarlo", async ({
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

  test("AC6: un archivo que no es PDF/JPEG/PNG se rechaza y no se lista", async ({
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
