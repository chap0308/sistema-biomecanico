import { expectPlayableVideo } from "./fixtures/media";
import { expect, test } from "./fixtures/squat-case";

test("registers and processes a fixture video end to end", async ({
  page,
  squatCase,
}) => {
  test.setTimeout(360_000);
  test.skip(
    process.env.SQUAT_E2E_RUN_ANALYSIS !== "1",
    "Set SQUAT_E2E_RUN_ANALYSIS=1 to execute the real video pipeline.",
  );
  await page.goto("/cases/new");
  const input = await squatCase.fillInstrument1(page);

  await page.getByRole("button", { name: "Registrar y analizar" }).click();
  await expect(page).toHaveURL(new RegExp(`/cases/${input.caseId}$`), {
    timeout: 300_000,
  });
  await expect(
    page.getByRole("heading", { name: input.caseId, exact: true }),
  ).toBeVisible();
  await expectPlayableVideo(page.locator("video"));
});
