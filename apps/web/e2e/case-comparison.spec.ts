import { expect, test } from "@playwright/test";

const caseId = process.env.SQUAT_E2E_RESULT_CASE_ID;
const referenceCaseId = process.env.SQUAT_E2E_REFERENCE_CASE_ID;

test("investigator reviews comparison metrics and exports", async ({
  page,
}) => {
  test.skip(!caseId, "Set SQUAT_E2E_RESULT_CASE_ID to a closed case.");

  await page.goto(`/cases/${caseId}/comparison`);

  await expect(
    page.getByRole("heading", { name: "Instrumento 3 y desempeño" }),
  ).toBeVisible();
  await expect(page.getByText("Comparación experta-sistema")).toBeVisible();
  await expect(
    page.getByRole("heading", {
      name: "Consolidación por repetición y patrón",
    }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Métricas acumuladas" }),
  ).toBeVisible();

  await expect(
    page.getByRole("link", { name: "Instrumentos Excel" }),
  ).toBeEnabled();
  await expect(page.getByRole("link", { name: "Reporte PDF" })).toBeEnabled();

  const excelDownload = page.waitForEvent("download");
  await page.getByRole("link", { name: "Instrumentos Excel" }).click();
  expect((await excelDownload).suggestedFilename()).toContain(
    "instruments.xlsx",
  );

  const pdfDownload = page.waitForEvent("download");
  await page.getByRole("link", { name: "Reporte PDF" }).click();
  expect((await pdfDownload).suggestedFilename()).toContain("report.pdf");
});

test("starts final-reference review and exposes pending forms without reload", async ({
  page,
}) => {
  test.skip(
    !referenceCaseId,
    "Set SQUAT_E2E_REFERENCE_CASE_ID to an open case with all evaluations submitted.",
  );

  await page.goto(`/cases/${referenceCaseId}/comparison`);
  const startButton = page.getByRole("button", {
    name: "Comenzar referencia final",
  });
  await expect(startButton).toBeEnabled();
  await expect(page.getByLabel("Referencia final")).toHaveCount(0);

  await startButton.click();
  await page.getByRole("button", { name: "Comenzar revisión" }).click();

  await expect(page.getByLabel("Referencia final").first()).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Registrar referencia" }).first(),
  ).toBeVisible();
  await expect(page.getByText("Pendiente").first()).toBeVisible();
  await expect(page.getByRole("button", { name: "Cerrar caso" })).toBeDisabled();
});
