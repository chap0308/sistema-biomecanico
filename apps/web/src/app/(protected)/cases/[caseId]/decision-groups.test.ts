import { describe, expect, it } from "vitest";

import type { SquatRuleDecision } from "@/types/squat-case-report";

import { groupCompleteDecisions } from "./decision-groups";

const findings = ["tronco", "pelvis"];

function decision(
  repetitionIndex: number,
  finding: string,
): SquatRuleDecision {
  return {
    repetition_index: repetitionIndex,
    finding,
    status: "ausente",
    direction: null,
    metric: `${finding}_metric`,
    unit: "deg",
    aggregate_value: 0,
    repetition_values: [0],
    repetition_states: ["ausente"],
    absent_max: 1,
    present_min: 2,
    rationale: "Prueba.",
  };
}

describe("groupCompleteDecisions", () => {
  it("groups a complete report by repetition", () => {
    const result = groupCompleteDecisions(
      [
        decision(1, "tronco"),
        decision(1, "pelvis"),
        decision(2, "tronco"),
        decision(2, "pelvis"),
      ],
      [1, 2],
      findings,
    );

    expect(result.isComplete).toBe(true);
    expect(result.groups.map((group) => group.repetitionIndex)).toEqual([1, 2]);
  });

  it("rejects a legacy aggregate report assigned to the first repetition", () => {
    const result = groupCompleteDecisions(
      [decision(1, "tronco"), decision(1, "pelvis")],
      [1, 2, 3],
      findings,
    );

    expect(result.isComplete).toBe(false);
  });
});
