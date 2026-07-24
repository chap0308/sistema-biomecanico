import { expect, test } from "@playwright/test";

const email = process.env.SQUAT_E2E_EMAIL;
const password = process.env.SQUAT_E2E_PASSWORD;

test("authenticates the investigator through Supabase SSR", async ({ page }) => {
  test.skip(!email || !password, "Local E2E credentials are not configured.");

  await page.goto("/login");
  await page.getByLabel("Correo institucional").fill(email!);
  await page.getByLabel("Contraseña").fill(password!);
  await page.getByRole("button", { name: /ingresar al estudio/i }).click();

  await expect(page).toHaveURL(/\/cases$/);
  await expect(
    page.getByRole("heading", { name: /casos de sentadilla/i }),
  ).toBeVisible();
  await expect(
    page
      .locator('[data-slot="badge"]')
      .filter({ hasText: /^Investigador$/ }),
  ).toBeVisible();
});
