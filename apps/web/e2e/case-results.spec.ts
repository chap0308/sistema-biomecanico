import { expect, test } from "@playwright/test";
import { expectPlayableVideo } from "./fixtures/media";

const caseId = process.env.SQUAT_E2E_RESULT_CASE_ID;

test("shows traceable squat results for a completed case", async ({ page }) => {
  test.skip(!caseId, "Set SQUAT_E2E_RESULT_CASE_ID to a persisted complete case.");

  await page.goto(`/cases/${caseId}`);

  await expect(
    page.getByRole("heading", { name: caseId!, exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", {
      name: "Compensaciones y variables por repetición",
    }),
  ).toBeVisible();
  await expect(page.getByText("Umbrales provisionales")).toBeVisible();
  await expectPlayableVideo(page.locator("video"));
  await expect(
    page.getByRole("heading", { name: "Cómo se obtuvo este resultado" }),
  ).toBeVisible();
  await expect(page.getByRole("tab", { name: "1. Pose 2D" })).toBeVisible();
  await expect(
    page.getByRole("tab", { name: "2. Segmentación" }),
  ).toBeVisible();
  await expect(page.getByRole("tab", { name: "3. Variables" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "4. Reglas" })).toBeVisible();
  await expect(
    page.getByRole("heading", {
      name: "Máxima profundidad por repetición",
    }),
  ).toBeVisible();

  await expect(page.getByText("Repetición 1 de 3")).toBeVisible();
  await page.getByRole("button", { name: "Siguiente" }).click();
  await expect(page.getByText("Repetición 2 de 3")).toBeVisible();
  await expect
    .poll(() =>
      page
        .locator("video")
        .evaluate((video) => (video as HTMLVideoElement).currentTime),
    )
    .toBeGreaterThan(10);
  const qualityChart = page.locator('[data-slot="chart"]').first();
  const chartBox = await qualityChart.boundingBox();
  expect(chartBox).not.toBeNull();
  await page.mouse.move(
    chartBox!.x + chartBox!.width * 0.55,
    chartBox!.y + chartBox!.height * 0.5,
  );
  await expect(
    qualityChart.getByText(/^\d+\.\d{2} s$/),
  ).toBeVisible();
  await expect(qualityChart.getByText("NaN s")).toHaveCount(0);

  await page.getByRole("button", { name: "Overlay técnico" }).click();
  await expect
    .poll(() =>
      page
        .locator("video")
        .evaluate((video) => (video as HTMLVideoElement).currentTime),
    )
    .toBeGreaterThan(10);
});
