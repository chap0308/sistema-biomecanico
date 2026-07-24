import { expect, test as setup } from "@playwright/test";

const email = process.env.SQUAT_E2E_EMAIL!;
const password = process.env.SQUAT_E2E_PASSWORD!;
const authFile = "playwright/.auth/investigator.json";

setup("authenticate investigator", async ({ page }) => {
  setup.setTimeout(60_000);
  await page.goto("/login");
  await page.getByLabel("Correo institucional").fill(email);
  await page.getByLabel("Contraseña").fill(password);
  await page.getByRole("button", { name: /ingresar al estudio/i }).click();
  await expect(page).toHaveURL(/\/cases$/, { timeout: 20_000 });
  await page.context().storageState({ path: authFile });
});
