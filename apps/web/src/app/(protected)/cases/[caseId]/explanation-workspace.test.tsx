import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { SquatCaseExplanation } from "@/types/squat-explanation";

import {
  ExplanationWorkspace,
  formatTooltipSeconds,
} from "./explanation-workspace";

const explanation: SquatCaseExplanation = {
  schema_version: "1.0",
  contract: "squat_case_explanation",
  case_id: "case_test",
  pipeline_version: "test",
  ruleset_version: "test-rules",
  quality: {
    visibility_threshold: 0.5,
    processed_percentage: 100,
    valid_percentage: 100,
    selected_keypoints: 13,
    mean_detected_keypoints: 13,
    minimum_observed_visibility: 0.9,
  },
  normalization_reference: "initial_shoulder_width",
  normalization_value: 0.25,
  total_source_frames: 3,
  frames_sampled: false,
  frames: [
    frame(0, 0, "descenso"),
    frame(1, 1, "maxima_profundidad"),
    frame(2, 2, "cierre"),
  ],
  repetitions: [
    {
      segmentation: {
        repetition_index: 1,
        start_frame: 0,
        peak_depth_frame: 1,
        end_frame: 2,
        start_seconds: 0,
        peak_depth_seconds: 1,
        end_seconds: 2,
        descent_duration_seconds: 1,
        ascent_duration_seconds: 1,
        total_duration_seconds: 2,
        peak_hip_midpoint_y: 0.6,
        valid_frames_percentage: 100,
      },
      metrics: null,
      decisions: [],
    },
  ],
  key_frames: [],
  artifact_downloads: [],
};

describe("ExplanationWorkspace", () => {
  it("presents the four explanatory stages for the active repetition", () => {
    render(
      <ExplanationWorkspace
        activeRepetition={1}
        currentTime={1}
        explanation={explanation}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Cómo se obtuvo este resultado" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "1. Pose 2D" })).toBeInTheDocument();
    expect(
      screen.getByRole("tab", { name: "2. Segmentación" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "3. Variables" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "4. Reglas" })).toBeInTheDocument();
    expect(
      screen.getByText("Disponibilidad de pose por fotograma"),
    ).toBeInTheDocument();
  });

  it("navigates repetitions from the traceability workspace", () => {
    const onRepetitionChange = vi.fn();
    const multiRepetitionExplanation = {
      ...explanation,
      repetitions: [
        explanation.repetitions[0],
        {
          ...explanation.repetitions[0],
          segmentation: {
            ...explanation.repetitions[0].segmentation,
            repetition_index: 2,
            start_seconds: 3,
            peak_depth_seconds: 4,
            end_seconds: 5,
          },
        },
      ],
    } satisfies SquatCaseExplanation;

    render(
      <ExplanationWorkspace
        activeRepetition={1}
        currentTime={1}
        explanation={multiRepetitionExplanation}
        onRepetitionChange={onRepetitionChange}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Siguiente" }));

    expect(onRepetitionChange).toHaveBeenCalledWith(2);
  });

  it("formats tooltip time from the frame timestamp", () => {
    expect(formatTooltipSeconds(6.699116)).toBe("6.70 s");
    expect(formatTooltipSeconds("Centro de caderas")).toBe(
      "Tiempo no disponible",
    );
  });
});

function frame(
  frameIndex: number,
  timestamp: number,
  phase: string,
): SquatCaseExplanation["frames"][number] {
  return {
    frame_index: frameIndex,
    timestamp_seconds: timestamp,
    valid_for_analysis: true,
    detected_keypoints: 13,
    minimum_critical_visibility: 0.9,
    hip_midpoint_y: 0.4 + frameIndex * 0.1,
    hip_midpoint_y_smoothed: 0.4 + frameIndex * 0.1,
    repetition_index: 1,
    phase,
    trunk_inclination_deg: frameIndex,
    pelvis_lateral_shift_pct: frameIndex,
    left_knee_medial_deviation_pct: frameIndex,
    right_knee_medial_deviation_pct: -frameIndex,
    bilateral_alignment_difference_pct: frameIndex * 2,
  };
}
