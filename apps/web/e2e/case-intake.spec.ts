import { expect, test } from "./fixtures/squat-case";
import { expectPlayableVideo } from "./fixtures/media";

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

  await page
    .getByRole("button", { name: "Completar datos de prueba" })
    .click();
  await expect(page.getByLabel("Código del video")).toHaveValue(
    /^dev_case_\d+$/,
  );
  await expect(page.getByLabel("Fuente del video")).toHaveValue(
    "fixture_desarrollo",
  );

  const fixture = await squatCase.fillInstrument1(page);
  await expect(page.getByLabel("Código del video")).toHaveValue(fixture.caseId);
  await expect(page.getByText("dev_negativo_001.mp4")).toBeVisible();
  await expectPlayableVideo(
    page.getByLabel("Vista previa del video seleccionado"),
  );
});
