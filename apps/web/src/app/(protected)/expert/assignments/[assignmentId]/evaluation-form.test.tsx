import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  buildEvaluationItems,
  EvaluationForm,
  findMissingClassifications,
} from "./evaluation-form";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh: vi.fn(),
    replace: vi.fn(),
  }),
}));

vi.mock("./expert-review-player", () => ({
  ExpertReviewPlayer: () => null,
}));

describe("buildEvaluationItems", () => {
  afterEach(cleanup);

  it("maps combined visible choices to independent Instrument 3 items", () => {
    const items = buildEvaluationItems({
      repetitions: [
        {
          repetitionIndex: 2,
          trunk: {
            choice: "ausente",
            confidence: "alta",
            observation: "",
          },
          pelvis: {
            choice: "presente_izquierda",
            confidence: "media",
            observation: "Traslación visible",
          },
          valgus: {
            choice: "presente_bilateral",
            confidence: "alta",
            observation: "",
          },
          asymmetry: {
            choice: "no_concluyente",
            confidence: "baja",
            observation: "Oclusión parcial",
          },
        },
      ],
      generalObservation: "",
    });

    expect(items).toHaveLength(4);
    expect(items[1]).toMatchObject({
      pattern_key: "pelvis_lateral_shift",
      repetition_index: 2,
      classification: "presente",
      observed_side: "izquierda",
    });
    expect(items[2].observed_side).toBe("bilateral");
    expect(items[3].classification).toBe("no_concluyente");
  });

  it("omits unanswered patterns from a draft", () => {
    const items = buildEvaluationItems({
      repetitions: [
        {
          repetitionIndex: 1,
          trunk: { choice: "", confidence: "media", observation: "" },
          pelvis: {
            choice: "ausente",
            confidence: "media",
            observation: "",
          },
          valgus: { choice: "", confidence: "media", observation: "" },
          asymmetry: { choice: "", confidence: "media", observation: "" },
        },
      ],
      generalObservation: "",
    });

    expect(items).toHaveLength(1);
    expect(items[0].pattern_key).toBe("pelvis_lateral_shift");
  });

  it("identifies unanswered classifications in repetition order", () => {
    const missing = findMissingClassifications([
      {
        repetitionIndex: 2,
        trunk: { choice: "", confidence: "media", observation: "" },
        pelvis: {
          choice: "ausente",
          confidence: "media",
          observation: "",
        },
        valgus: { choice: "", confidence: "media", observation: "" },
        asymmetry: {
          choice: "presente_sin_direccion",
          confidence: "media",
          observation: "",
        },
      },
    ]);

    expect(missing).toEqual([
      {
        path: "repetitions.0.trunk.choice",
        repetitionIndex: 2,
        label: "Inclinación lateral del tronco",
      },
      {
        path: "repetitions.0.valgus.choice",
        repetitionIndex: 2,
        label: "Valgo dinámico visible",
      },
    ]);
  });

  it("shows missing fields before opening the final confirmation", async () => {
    render(
      <EvaluationForm
        assignment={{
          assignment_id: "assignment-1",
          case_id: "case-1",
          status: "pending",
          created_at: "2026-07-30T00:00:00Z",
          updated_at: "2026-07-30T00:00:00Z",
          reference_status: "open",
          repetitions: [
            {
              repetition_index: 1,
              start_seconds: 0.5,
              peak_depth_seconds: 1,
              end_seconds: 1.5,
            },
          ],
          evaluation: null,
        }}
      />,
    );

    fireEvent.click(
      screen.getByRole("button", { name: "Enviar evaluación" }),
    );

    expect(
      screen.queryByText("¿Enviar la evaluación definitivamente?"),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText("Faltan 4 clasificaciones"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Repetición 1 · Inclinación lateral del tronco",
      }),
    ).toBeInTheDocument();
    expect(screen.getAllByText("Clasificación pendiente")).toHaveLength(4);

    for (const select of screen.getAllByLabelText("Clasificación")) {
      fireEvent.change(select, { target: { value: "ausente" } });
    }

    await waitFor(() => {
      expect(
        screen.queryByText("Faltan 4 clasificaciones"),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByText("Clasificación pendiente"),
      ).not.toBeInTheDocument();
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Enviar evaluación" }),
    );
    expect(
      screen.getByText("¿Enviar la evaluación definitivamente?"),
    ).toBeInTheDocument();
  });
});
