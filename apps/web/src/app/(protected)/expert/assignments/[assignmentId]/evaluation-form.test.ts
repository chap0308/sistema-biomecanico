import { describe, expect, it } from "vitest";

import { buildEvaluationItems } from "./evaluation-form";

describe("buildEvaluationItems", () => {
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
});
