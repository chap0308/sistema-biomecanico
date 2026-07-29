import { expect, test } from "@playwright/test";
import { expectPlayableVideo } from "./fixtures/media";

const assignmentId = process.env.SQUAT_E2E_EXPERT_ASSIGNMENT_ID!;

test("expert completes a blinded Instrument 3 evaluation", async ({
  page,
}) => {
  await page.goto("/expert/assignments");
  await expect(
    page.locator(`a[href="/expert/assignments/${assignmentId}"]`),
  ).toBeVisible();

  await page.goto(`/expert/assignments/${assignmentId}`);

  await expect(
    page.getByRole("heading", { name: "Instrumento 3" }),
  ).toBeVisible();
  await expect(page.getByText("Evaluación ciega")).toBeVisible();
  await expect(page.locator("video")).toHaveAttribute(
    "src",
    `/api/squat/expert/assignments/${assignmentId}/video`,
  );
  await expectPlayableVideo(page.locator("video"));
  await expect(page.getByText("Resultado del sistema")).toHaveCount(0);
  await expect(page.getByText("Compensaciones detectadas")).toHaveCount(0);

  const choices = {
    trunk: "presente_izquierda",
    pelvis: "ausente",
    valgus: "presente_izquierda",
    asymmetry: "presente_izquierda",
  } as const;
  for (const [pattern, choice] of Object.entries(choices)) {
    const fields = page.locator(`select[id$=".${pattern}.choice"]`);
    for (let index = 0; index < (await fields.count()); index += 1) {
      await fields.nth(index).selectOption(choice);
    }
  }
  await page
    .getByRole("button", { name: "Guardar borrador" })
    .click();
  await expect(page.getByText("Borrador guardado.")).toBeVisible();

  await page.getByRole("button", { name: "Enviar evaluación" }).click();
  await expect(
    page.getByText("Esta evaluación fue enviada y ya no puede modificarse."),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Enviar evaluación" }),
  ).toHaveCount(0);
});
