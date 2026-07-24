import { expect, test } from "@playwright/test";

const assignmentId = process.env.SQUAT_E2E_EXPERT_ASSIGNMENT_ID!;

test("expert completes a blinded Instrument 3 evaluation", async ({
  page,
}) => {
  await page.goto(`/expert/assignments/${assignmentId}`);

  await expect(
    page.getByRole("heading", { name: "Instrumento 3" }),
  ).toBeVisible();
  await expect(page.getByText("Evaluación ciega")).toBeVisible();
  await expect(page.locator("video")).toHaveAttribute(
    "src",
    `/api/squat/expert/assignments/${assignmentId}/video`,
  );
  await expect(page.getByText("Resultado del sistema")).toHaveCount(0);
  await expect(page.getByText("Compensaciones detectadas")).toHaveCount(0);

  await page.locator("#trunk").selectOption("presente_izquierda");
  await page.locator("#pelvis").selectOption("ausente");
  await page.locator("#valgus").selectOption("presente_izquierda");
  await page.locator("#asymmetry").selectOption("presente_izquierda");
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
