import { expect, test } from "@playwright/test";
import { expectPlayableVideo } from "./fixtures/media";

const caseId = process.env.SQUAT_E2E_RESULT_CASE_ID;

test("shows traceable squat results for a completed case", async ({ page }) => {
  test.skip(!caseId, "Set SQUAT_E2E_RESULT_CASE_ID to a persisted complete case.");

  await page.goto(`/cases/${caseId}`);

  await expect(
    page.getByRole("heading", { name: caseId!, exact: true }),
  ).toBeVisible();
  await expect(page.getByText("Resultado por patrón", { exact: true })).toBeVisible();
  await expect(page.getByText("Umbrales provisionales")).toBeVisible();
  await expectPlayableVideo(page.locator("video"));
  await expect(
    page.getByRole("heading", {
      name: "Máxima profundidad por repetición",
    }),
  ).toBeVisible();
});
