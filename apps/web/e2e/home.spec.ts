import { expect, test } from "@playwright/test";

test("presents the research scope", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: /la sentadilla, convertida en evidencia/i }),
  ).toBeVisible();
  await expect(page.getByText("Prototipo de investigación")).toBeVisible();
});

test("opens the controlled access form", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: /ingresar al estudio/i }).click();

  await expect(page).toHaveURL(/\/login$/);
  await expect(
    page.getByRole("heading", { name: /iniciar sesión/i }),
  ).toBeVisible({ timeout: 15_000 });
  await expect(page.getByLabel("Correo institucional")).toBeVisible();
  await expect(page.getByLabel("Contraseña")).toBeVisible();
});
