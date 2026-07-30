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

test("persists the selected color theme across public routes", async ({
  page,
}) => {
  await page.addInitScript(() => localStorage.setItem("theme", "light"));
  await page.goto("/");

  await expect(page.locator("html")).not.toHaveClass(/dark/);
  await page.getByRole("button", { name: "Cambiar tema de color" }).click();
  await expect(page.locator("html")).toHaveClass(/dark/);

  await page.getByRole("link", { name: /ingresar al estudio/i }).click();
  await expect(page.locator("html")).toHaveClass(/dark/);
});

test("keeps the landing page readable on a narrow viewport", async ({
  page,
}) => {
  await page.setViewportSize({ width: 360, height: 740 });
  await page.goto("/");

  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(
    dimensions.clientWidth + 1,
  );
  await expect(
    page.getByRole("heading", {
      name: /la sentadilla, convertida en evidencia/i,
    }),
  ).toBeVisible();
});
