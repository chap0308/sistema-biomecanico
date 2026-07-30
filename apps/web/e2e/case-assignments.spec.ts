import { expect, test } from "@playwright/test";

const caseId = process.env.SQUAT_E2E_ASSIGNMENT_CASE_ID;
const expertEmail = process.env.SQUAT_E2E_ASSIGNMENT_EXPERT_EMAIL;

test("adds and removes an evaluator without reloading the assignment page", async ({
  page,
}) => {
  test.skip(
    !caseId || !expertEmail,
    "Set a disposable open case and an unassigned evaluator for this mutating flow.",
  );

  await page.goto(`/cases/${caseId}/assignments`);
  const expertCard = page.locator("label").filter({ hasText: expertEmail! });
  await expertCard.getByRole("checkbox").click();
  await page.getByRole("button", { name: "Asignar caso" }).click();

  const assignedExpert = page
    .getByText(/Evaluadores asignados/)
    .locator("..")
    .getByText(expertEmail!, { exact: true });
  await expect(assignedExpert).toBeVisible();

  const assignedRow = assignedExpert.locator("..").locator("..");
  await assignedRow.getByRole("button", { name: "Retirar evaluador" }).click();
  await page
    .getByRole("button", { name: "Retirar evaluador", exact: true })
    .last()
    .click();

  await expect(assignedExpert).toHaveCount(0);
  await expect(expertCard.getByRole("checkbox")).toBeEnabled();
});
