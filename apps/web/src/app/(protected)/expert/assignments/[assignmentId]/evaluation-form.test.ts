import { describe, expect, it } from "vitest";

import { buildEvaluationItems } from "./evaluation-form";

describe("buildEvaluationItems", () => {
  it("maps combined visible choices to independent Instrument 3 items", () => {
    const items = buildEvaluationItems({
      trunk: "ausente",
      trunkConfidence: "alta",
      trunkObservation: "",
      pelvis: "presente_izquierda",
      pelvisConfidence: "media",
      pelvisObservation: "Traslación visible",
      valgus: "presente_bilateral",
      valgusConfidence: "alta",
      valgusObservation: "",
      asymmetry: "no_concluyente",
      asymmetryConfidence: "baja",
      asymmetryObservation: "Oclusión parcial",
      generalObservation: "",
    });

    expect(items).toHaveLength(4);
    expect(items[1]).toMatchObject({
      pattern_key: "pelvis_lateral_shift",
      classification: "presente",
      observed_side: "izquierda",
    });
    expect(items[2].observed_side).toBe("bilateral");
    expect(items[3].classification).toBe("no_concluyente");
  });

  it("omits unanswered patterns from a draft", () => {
    const items = buildEvaluationItems({
      trunk: "",
      trunkConfidence: "media",
      trunkObservation: "",
      pelvis: "ausente",
      pelvisConfidence: "media",
      pelvisObservation: "",
      valgus: "",
      valgusConfidence: "media",
      valgusObservation: "",
      asymmetry: "",
      asymmetryConfidence: "media",
      asymmetryObservation: "",
      generalObservation: "",
    });

    expect(items).toHaveLength(1);
    expect(items[0].pattern_key).toBe("pelvis_lateral_shift");
  });
});
