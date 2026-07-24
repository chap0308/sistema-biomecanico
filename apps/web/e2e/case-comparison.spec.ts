import { expect, test } from "@playwright/test";

const caseId = process.env.SQUAT_E2E_RESULT_CASE_ID;

test("investigator reviews comparison metrics and exports", async ({
  page,
}) => {
  test.skip(!caseId, "Set SQUAT_E2E_RESULT_CASE_ID to a consolidated case.");

  await page.goto(`/cases/${caseId}/comparison`);

  await expect(
    page.getByRole("heading", { name: "Instrumento 3 y desempeño" }),
  ).toBeVisible();
  await expect(page.getByText("Comparación experta-sistema")).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Consolidación por patrón" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Métricas acumuladas" }),
  ).toBeVisible();

  const excelDownload = page.waitForEvent("download");
  await page.getByRole("link", { name: "Excel" }).click();
  expect((await excelDownload).suggestedFilename()).toContain(
    "instruments.xlsx",
  );

  const pdfDownload = page.waitForEvent("download");
  await page.getByRole("link", { name: "Reporte PDF" }).click();
  expect((await pdfDownload).suggestedFilename()).toContain("report.pdf");
});
