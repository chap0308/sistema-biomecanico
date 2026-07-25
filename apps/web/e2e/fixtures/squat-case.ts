import path from "node:path";

import { expect, test as base, type Page } from "@playwright/test";

type SquatCaseInput = {
  caseId: string;
  participantCode: string;
  videoPath: string;
};

type SquatCaseFixture = {
  fillInstrument1: (
    page: Page,
    overrides?: Partial<SquatCaseInput>,
  ) => Promise<SquatCaseInput>;
};

const defaultVideoPath =
  process.env.SQUAT_E2E_UPLOAD_VIDEO ??
  path.resolve(
    process.cwd(),
    "../../data/sentadilla_bilateral/raw/dev_negativo_001.mp4",
  );

export const test = base.extend<{ squatCase: SquatCaseFixture }>({
  squatCase: async ({}, provide) => {
    await provide({
      async fillInstrument1(page, overrides = {}) {
        const input: SquatCaseInput = {
          caseId: overrides.caseId ?? `e2e_case_${Date.now()}`,
          participantCode: overrides.participantCode ?? "P-E2E-001",
          videoPath: overrides.videoPath ?? defaultVideoPath,
        };

        await page.getByLabel("Código del video").fill(input.caseId);
        await page
          .getByLabel("Código del participante")
          .fill(input.participantCode);
        await page.getByLabel("Fecha de registro").fill("2026-07-24");
        await page.getByLabel("Fuente del video").fill("fixture_playwright");
        await page.getByLabel("Dispositivo de captura").fill("smartphone");
        await page.getByLabel("Iluminación").selectOption("adecuada");
        await page.getByLabel("Fondo visual").selectOption("adecuado");
        await page.getByLabel("Visibilidad corporal").selectOption("completa");
        await page.getByLabel("Oclusiones").selectOption("ninguna");
        await page.getByLabel("Superficie").selectOption("plana");
        await page
          .getByLabel("Soporte externo bajo talones")
          .selectOption("no");
        await page
          .getByLabel("Contacto aparente de talones")
          .selectOption("continuo");
        await page
          .getByLabel("Sentadilla completa observable")
          .selectOption("true");
        await page
          .getByLabel("Condición de apoyo conforme al protocolo")
          .selectOption("true");
        await page.getByLabel("Video del caso").setInputFiles(input.videoPath);
        return input;
      },
    });
  },
});

export { expect };
