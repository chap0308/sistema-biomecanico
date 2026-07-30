import { expect, test } from "@playwright/test";
import { expectPlayableVideo } from "./fixtures/media";

const caseId = process.env.SQUAT_E2E_RESULT_CASE_ID;
const partialCaseId = process.env.SQUAT_E2E_PARTIAL_CASE_ID;
const noValidCaseId = process.env.SQUAT_E2E_NO_VALID_CASE_ID;
const oneValidMultiCaseId =
  process.env.SQUAT_E2E_ONE_VALID_MULTI_CASE_ID;
const singleValidCaseId = process.env.SQUAT_E2E_SINGLE_VALID_CASE_ID;
const singleInvalidCaseId =
  process.env.SQUAT_E2E_SINGLE_INVALID_CASE_ID;

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

test("shows valid repetitions and explains the excluded repetition", async ({
  page,
}) => {
  test.skip(
    !partialCaseId,
    "Set SQUAT_E2E_PARTIAL_CASE_ID to a case with valid and excluded repetitions.",
  );
  await page.goto(`/cases/${partialCaseId}`);

  const results = page.getByTestId("case-results");
  await expect(results).toBeVisible();
  await expect(results.locator("[data-result-repetition='1']")).toBeVisible();
  await expect(results.locator("[data-result-repetition='2']")).toBeVisible();
  await expect(results.locator("[data-result-repetition='3']")).toHaveCount(0);
  await expect(
    page.getByText("El informe requiere reprocesamiento"),
  ).toHaveCount(0);

  await page.getByRole("button", { name: "Siguiente" }).click();
  await page.getByRole("button", { name: "Siguiente" }).click();
  await expect(page.getByText(/Repetici.n 3 de 3/)).toBeVisible();
  await page.getByRole("tab", { name: "4. Reglas" }).click();
  await expect(
    page.getByText("Repetición excluida del análisis"),
  ).toBeVisible();
  await expect(
    page.getByText(/Fotogramas v.lidos de la repetici.n 3: 78.30 %/),
  ).toBeVisible();
});

test("keeps technical downloads but blocks comparison without valid repetitions", async ({
  page,
}) => {
  test.skip(
    !noValidCaseId,
    "Set SQUAT_E2E_NO_VALID_CASE_ID to a case without valid repetitions.",
  );
  await page.goto(`/cases/${noValidCaseId}`);

  await expect(
    page.getByRole("link", { name: "Datos técnicos normalizados" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Asignar evaluadores" }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("link", { name: "Comparar resultados" }),
  ).toHaveCount(0);

  await page.goto(`/cases/${noValidCaseId}/assignments`);
  await expect(
    page.getByText(/no contiene repeticiones v.lidas/),
  ).toBeVisible();

  await page.goto(`/cases/${noValidCaseId}/comparison`);
  await expect(
    page.getByText("Comparación no disponible", { exact: true }),
  ).toBeVisible();
});

test("shows only the eligible result when one repetition is valid among several", async ({
  page,
}) => {
  test.skip(
    !oneValidMultiCaseId,
    "Set SQUAT_E2E_ONE_VALID_MULTI_CASE_ID to a mixed-quality case with one valid repetition.",
  );
  await page.goto(`/cases/${oneValidMultiCaseId}`);

  const results = page.getByTestId("case-results");
  await expect(results).toBeVisible();
  await expect(results.locator("[data-result-repetition]")).toHaveCount(1);
  await expect(
    page.getByRole("link", { name: "Asignar evaluadores" }),
  ).toBeVisible();
});

test("supports a case with one valid repetition", async ({ page }) => {
  test.skip(
    !singleValidCaseId,
    "Set SQUAT_E2E_SINGLE_VALID_CASE_ID to a one-repetition valid case.",
  );
  await page.goto(`/cases/${singleValidCaseId}`);

  await expect(
    page.getByTestId("case-results").locator("[data-result-repetition]"),
  ).toHaveCount(1);
  await expect(
    page.getByRole("link", { name: "Comparar resultados" }),
  ).toBeVisible();
});

test("blocks expert workflows for a case with one invalid repetition", async ({
  page,
}) => {
  test.skip(
    !singleInvalidCaseId,
    "Set SQUAT_E2E_SINGLE_INVALID_CASE_ID to a one-repetition invalid case.",
  );
  await page.goto(`/cases/${singleInvalidCaseId}`);

  await expect(
    page.getByRole("link", { name: "Datos técnicos normalizados" }),
  ).toBeVisible();
  await expect(page.getByTestId("case-results")).toHaveCount(0);
  await expect(
    page.getByRole("link", { name: "Asignar evaluadores" }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("link", { name: "Comparar resultados" }),
  ).toHaveCount(0);
});
