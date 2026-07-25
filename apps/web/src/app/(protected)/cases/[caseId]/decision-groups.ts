import type { SquatRuleDecision } from "@/types/squat-case-report";

export type SquatDecisionGroup = {
  repetitionIndex: number;
  decisions: SquatRuleDecision[];
};

export function groupCompleteDecisions(
  decisions: SquatRuleDecision[],
  repetitionIndexes: number[],
  expectedFindings: string[],
): { groups: SquatDecisionGroup[]; isComplete: boolean } {
  const groups = repetitionIndexes.map((repetitionIndex) => ({
    repetitionIndex,
    decisions: decisions.filter(
      (decision) => decision.repetition_index === repetitionIndex,
    ),
  }));
  const expected = new Set(expectedFindings);
  const expectedDecisionCount = repetitionIndexes.length * expected.size;
  const isComplete =
    repetitionIndexes.length > 0 &&
    decisions.length === expectedDecisionCount &&
    groups.every((group) => {
      const findings = new Set(
        group.decisions.map((decision) => decision.finding),
      );
      return (
        group.decisions.length === expected.size &&
        findings.size === expected.size &&
        [...findings].every((finding) => expected.has(finding))
      );
    });

  return { groups, isComplete };
}
