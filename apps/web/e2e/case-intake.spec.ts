import { expect, test } from "./fixtures/squat-case";

test("fills Instrument 1 and attaches a fixture video", async ({
  page,
  squatCase,
}) => {
  await page.goto("/cases");
  await page.getByRole("link", { name: /registrar caso/i }).click();
  await expect(page).toHaveURL(/\/cases\/new$/);
  await expect(
    page.getByRole("heading", { name: /registrar video/i }),
  ).toBeVisible();
  await expect(page.getByLabel("Código del video")).toBeVisible();
  await expect(page.getByLabel("Iluminación")).toBeVisible();
  await expect(page.getByLabel("Video del caso")).toBeAttached();

  const fixture = await squatCase.fillInstrument1(page);
  await expect(page.getByLabel("Código del video")).toHaveValue(fixture.caseId);
  await expect(page.getByText("dev_negativo_001.mp4")).toBeVisible();
});
