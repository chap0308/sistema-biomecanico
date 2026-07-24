import { expect, test } from "@playwright/test";

test("shows the authenticated Instrument 1 intake", async ({ page }) => {
  await page.goto("/cases");
  await page.getByRole("link", { name: /registrar caso/i }).click();
  await expect(page).toHaveURL(/\/cases\/new$/);
  await expect(
    page.getByRole("heading", { name: /registrar video/i }),
  ).toBeVisible();
  await expect(page.getByLabel("Código del video")).toBeVisible();
  await expect(page.getByLabel("Iluminación")).toBeVisible();
  await expect(page.getByLabel("Video del caso")).toBeAttached();
});
