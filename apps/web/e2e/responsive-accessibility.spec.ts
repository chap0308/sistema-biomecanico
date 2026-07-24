import { expect, test } from "@playwright/test";

const caseId = process.env.SQUAT_E2E_RESULT_CASE_ID;

async function expectNoPageOverflow(page: import("@playwright/test").Page) {
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));

  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.clientWidth + 1);
}

test.describe("responsive and keyboard evidence", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!caseId, "Set SQUAT_E2E_RESULT_CASE_ID to a persisted complete case.");
    await page.setViewportSize({ width: 390, height: 844 });
  });

  test("result remains readable on a mobile viewport", async ({ page }) => {
    await page.goto(`/cases/${caseId}`);

    await expect(page.locator("main")).toHaveCount(1);
    await expect(
      page.getByRole("heading", { name: caseId!, exact: true }),
    ).toBeVisible();
    await expect(page.locator("video")).toBeVisible();
    await expectNoPageOverflow(page);
  });

  test("comparison remains readable and exposes accessible exports", async ({
    page,
  }) => {
    await page.goto(`/cases/${caseId}/comparison`);

    await expect(page.locator("main")).toHaveCount(1);
    await expect(
      page.getByRole("heading", { name: "Instrumento 3 y desempeño" }),
    ).toBeVisible();
    await expect(page.getByRole("link", { name: "Excel" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Reporte PDF" })).toBeVisible();
    await expectNoPageOverflow(page);
  });

  test("keyboard users can bypass the protected header", async ({ page }) => {
    await page.goto(`/cases/${caseId}`);

    await page.keyboard.press("Tab");
    const skipLink = page.getByRole("link", { name: "Ir al contenido principal" });
    await expect(skipLink).toBeFocused();
    await skipLink.press("Enter");
    await expect(page.locator("#main-content")).toBeFocused();
  });
});
