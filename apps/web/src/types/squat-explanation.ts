import type {
  SquatRepetition,
  SquatRepetitionMetrics,
  SquatRuleDecision,
} from "@/types/squat-case-report";

export type SquatExplanationFrame = {
  frame_index: number;
  timestamp_seconds: number;
  valid_for_analysis: boolean;
  detected_keypoints: number | null;
  minimum_critical_visibility: number | null;
  hip_midpoint_y: number | null;
  hip_midpoint_y_smoothed: number | null;
  repetition_index: number;
  phase: string;
  trunk_inclination_deg: number | null;
  pelvis_lateral_shift_pct: number | null;
  left_knee_medial_deviation_pct: number | null;
  right_knee_medial_deviation_pct: number | null;
  bilateral_alignment_difference_pct: number | null;
  landmark_visibility: Record<string, number>;
};

export type SquatLandmarkVisibilitySummary = {
  repetition_index: number;
  landmark: string;
  anatomical_group: string;
  side: "izquierda" | "derecha" | "central";
  mean_visibility: number;
  usable_frames_percentage: number;
  availability: "visible_estable" | "intermitente" | "no_disponible";
};

export type SquatExplanationKeyFrame = {
  repetition_index: number;
  event: "inicio_descenso" | "maxima_profundidad" | "final_ascenso";
  frame_index: number;
  timestamp_seconds: number;
  landmarks: Record<
    string,
    { x: number; y: number; visibility: number }
  >;
  geometry: {
    shoulder_midpoint: ExplanationPoint | null;
    pelvis_midpoint: ExplanationPoint | null;
    ankle_midpoint: ExplanationPoint | null;
    left_knee_projection: ExplanationPoint | null;
    right_knee_projection: ExplanationPoint | null;
  };
};

type ExplanationPoint = { x: number; y: number; visibility: number };

export type SquatCaseExplanation = {
  schema_version: "1.0";
  contract: "squat_case_explanation";
  case_id: string;
  pipeline_version: string;
  ruleset_version: string | null;
  quality: {
    visibility_threshold: number;
    processed_percentage: number;
    valid_percentage: number;
    selected_keypoints: number;
    mean_detected_keypoints: number;
    minimum_observed_visibility: number | null;
  } | null;
  normalization_reference: "initial_shoulder_width" | null;
  normalization_value: number | null;
  total_source_frames: number;
  frames_sampled: boolean;
  frames: SquatExplanationFrame[];
  repetitions: {
    segmentation: SquatRepetition;
    metrics: SquatRepetitionMetrics | null;
    decisions: SquatRuleDecision[];
  }[];
  key_frames: SquatExplanationKeyFrame[];
  landmark_visibility_summaries: SquatLandmarkVisibilitySummary[];
  artifact_downloads: { kind: string; filename: string }[];
};
