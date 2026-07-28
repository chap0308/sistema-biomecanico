import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { SquatRuleDecision } from "@/types/squat-case-report";

import { MetricEvidence } from "./metric-evidence";

const decision: SquatRuleDecision = {
  repetition_index: 1,
  finding: "valgo_dinamico_visible",
  status: "presente",
  direction: "izquierda",
  metric: "knee_medial_deviation_at_peak_pct",
  unit: "pct_ancho_hombros",
  aggregate_value: 12.5,
  repetition_values: [12.5],
  repetition_states: ["presente"],
  absent_max: 2,
  present_min: 5,
  rationale: "Regla de prueba",
};

describe("MetricEvidence", () => {
  it("shows repetition values and interpretable thresholds", () => {
    render(
      <MetricEvidence
        decision={decision}
        repetitionMetrics={{
          repetition_index: 1,
          peak_depth_frame: 100,
          valid_frames_percentage: 100,
          left_knee_medial_deviation_at_peak_pct: 12.5,
          right_knee_medial_deviation_at_peak_pct: -4.25,
          bilateral_alignment_difference_at_peak_pct: 16.75,
        }}
      />,
    );

    expect(screen.getByText("Valor calculado")).toBeInTheDocument();
    expect(screen.getAllByText(/12[.,]5 %/)).toHaveLength(2);
    expect(screen.getByText("Ausente ≤ 2")).toBeInTheDocument();
    expect(screen.getByText("Presente ≥ 5")).toBeInTheDocument();
    expect(screen.getByText("Rodilla izquierda")).toBeInTheDocument();
    expect(screen.getByText("Rodilla derecha")).toBeInTheDocument();
    expect(
      screen.getByText(/porcentaje del ancho inicial de hombros/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Ver fórmula y convención"),
    ).toBeInTheDocument();
  });
});
