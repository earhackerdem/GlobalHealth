import { expect, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import {
  randomEmail,
  randomItemDescription,
  randomItemTitle,
  randomPassword,
} from "./utils/random"
import { logInUser } from "./utils/user"

test("Items page is accessible and shows correct title", async ({ page }) => {
  await page.goto("/items")
  await expect(page.getByRole("heading", { name: "Elementos" })).toBeVisible()
  await expect(page.getByText("Crea y administra tus elementos")).toBeVisible()
})

test("Add Item button is visible", async ({ page }) => {
  await page.goto("/items")
  await expect(page.getByRole("button", { name: "Agregar elemento" })).toBeVisible()
})

test.describe("Items management", () => {
  test.use({ storageState: { cookies: [], origins: [] } })
  let email: string
  const password = randomPassword()

  test.beforeAll(async () => {
    email = randomEmail()
    await createUser({ email, password })
  })

  test.beforeEach(async ({ page }) => {
    await logInUser(page, email, password)
    await page.goto("/items")
  })

  test("Create a new item successfully", async ({ page }) => {
    const title = randomItemTitle()
    const description = randomItemDescription()

    await page.getByRole("button", { name: "Agregar elemento" }).click()
    await page.getByLabel("Título").fill(title)
    await page.getByLabel("Descripción").fill(description)
    await page.getByRole("button", { name: "Guardar" }).click()

    await expect(page.getByText("Elemento creado correctamente")).toBeVisible()
    await expect(page.getByText(title)).toBeVisible()
  })

  test("Create item with only required fields", async ({ page }) => {
    const title = randomItemTitle()

    await page.getByRole("button", { name: "Agregar elemento" }).click()
    await page.getByLabel("Título").fill(title)
    await page.getByRole("button", { name: "Guardar" }).click()

    await expect(page.getByText("Elemento creado correctamente")).toBeVisible()
    await expect(page.getByText(title)).toBeVisible()
  })

  test("Cancel item creation", async ({ page }) => {
    await page.getByRole("button", { name: "Agregar elemento" }).click()
    await page.getByLabel("Título").fill("Test Item")
    await page.getByRole("button", { name: "Cancelar" }).click()

    await expect(page.getByRole("dialog")).not.toBeVisible()
  })

  test("Title is required", async ({ page }) => {
    await page.getByRole("button", { name: "Agregar elemento" }).click()
    await page.getByLabel("Título").fill("")
    await page.getByLabel("Título").blur()

    await expect(page.getByText("El título es obligatorio")).toBeVisible()
  })

  test.describe("Edit and Delete", () => {
    let itemTitle: string

    test.beforeEach(async ({ page }) => {
      itemTitle = randomItemTitle()

      await page.getByRole("button", { name: "Agregar elemento" }).click()
      await page.getByLabel("Título").fill(itemTitle)
      await page.getByRole("button", { name: "Guardar" }).click()
      await expect(page.getByText("Elemento creado correctamente")).toBeVisible()
      await expect(page.getByRole("dialog")).not.toBeVisible()
    })

    test("Edit an item successfully", async ({ page }) => {
      const itemRow = page.getByRole("row").filter({ hasText: itemTitle })
      await itemRow.getByRole("button").last().click()
      await page.getByRole("menuitem", { name: "Editar elemento" }).click()

      const updatedTitle = randomItemTitle()
      await page.getByLabel("Título").fill(updatedTitle)
      await page.getByRole("button", { name: "Guardar" }).click()

      await expect(
        page.getByText("Elemento actualizado correctamente"),
      ).toBeVisible()
      await expect(page.getByText(updatedTitle)).toBeVisible()
    })

    test("Delete an item successfully", async ({ page }) => {
      const itemRow = page.getByRole("row").filter({ hasText: itemTitle })
      await itemRow.getByRole("button").last().click()
      await page.getByRole("menuitem", { name: "Eliminar elemento" }).click()

      await page.getByRole("button", { name: "Eliminar" }).click()

      await expect(
        page.getByText("El elemento se eliminó correctamente"),
      ).toBeVisible()
      await expect(page.getByText(itemTitle)).not.toBeVisible()
    })
  })
})

test.describe("Items empty state", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test("Shows empty state message when no items exist", async ({ page }) => {
    const email = randomEmail()
    const password = randomPassword()
    await createUser({ email, password })
    await logInUser(page, email, password)

    await page.goto("/items")

    await expect(page.getByText("Aún no tienes elementos")).toBeVisible()
    await expect(
      page.getByText("Agrega un elemento nuevo para comenzar"),
    ).toBeVisible()
  })
})
