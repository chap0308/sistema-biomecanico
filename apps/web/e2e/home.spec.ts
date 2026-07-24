import { expect, test } from "@playwright/test";

test("presents the research scope", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: /la sentadilla, convertida en evidencia/i }),
  ).toBeVisible();
  await expect(page.getByText("Prototipo de investigación")).toBeVisible();
});
