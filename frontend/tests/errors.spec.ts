import { expect, test } from "@playwright/test"

test.use({ storageState: { cookies: [], origins: [] } })

test("Not found page shows es-MX message and Volver action", async ({
  page,
}) => {
  await page.goto("/ruta-inexistente")

  await expect(
    page.getByText("No encontramos la página que buscas."),
  ).toBeVisible()
  await expect(page.getByText("Volver")).toBeVisible()
})

test("Login page has es-MX tab title", async ({ page }) => {
  await page.goto("/login")

  await expect(page).toHaveTitle("Iniciar sesión - FastAPI Template")
})

test("Recover password page has es-MX tab title", async ({ page }) => {
  await page.goto("/recover-password")

  await expect(page).toHaveTitle("Recuperar contraseña - FastAPI Template")
})
