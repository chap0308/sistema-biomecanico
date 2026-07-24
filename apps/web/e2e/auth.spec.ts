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
