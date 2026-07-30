import { expect, test } from "@playwright/test";

test("authenticates the investigator through Supabase SSR", async ({ page }) => {
  await page.goto("/cases");
  await expect(
    page.getByRole("heading", { name: /casos de sentadilla/i }),
  ).toBeVisible();
  await expect(
    page
      .locator('[data-slot="badge"]')
      .filter({ hasText: /^Investigador$/ }),
  ).toBeVisible();
});

test("lists the unfiltered investigator history", async ({ page }) => {
  await page.goto("/cases");

  await expect(
    page.getByText("Historial temporalmente no disponible"),
  ).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Todos" })).toBeVisible();
  await expect(page.getByText(/dev_case_/).first()).toBeVisible();
});

test("logs out without retaining credentials or a pending login state", async ({
  browser,
}) => {
  test.skip(
    process.env.SQUAT_E2E_RUN_LOGOUT !== "1",
    "Logout invalidates the account sessions and must run in isolation.",
  );
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto("/login");
  await page
    .getByLabel("Correo institucional")
    .fill(process.env.SQUAT_E2E_EMAIL!);
  await page
    .getByLabel(/contrase/i)
    .fill(process.env.SQUAT_E2E_PASSWORD!);
  await page.getByRole("button", { name: "Ingresar al estudio" }).click();
  await expect(page).toHaveURL(/\/cases$/);

  await page.getByRole("button", { name: /cerrar sesi/i }).click();
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByLabel("Correo institucional")).toHaveValue("");
  await expect(page.getByLabel(/contrase/i)).toHaveValue("");
  await expect(
    page.getByRole("button", { name: "Ingresar al estudio" }),
  ).toBeEnabled();
  await context.close();
});
