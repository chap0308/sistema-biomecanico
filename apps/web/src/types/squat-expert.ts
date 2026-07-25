export type ExpertProfile = {
  user_id: string;
  email: string | null;
  display_name: string | null;
};

export type ExpertPatternKey =
  | "trunk_lateral_inclination"
  | "pelvis_lateral_shift"
  | "visible_dynamic_valgus"
  | "bilateral_asymmetry";

export type ExpertObservedSide =
  | "izquierda"
  | "derecha"
  | "bilateral"
  | "sin_direccion";

export type ExpertEvaluationItem = {
  repetition_index: number;
  pattern_key: ExpertPatternKey;
  classification: "presente" | "ausente" | "no_concluyente";
  observed_side: ExpertObservedSide | null;
  confidence: "baja" | "media" | "alta" | null;
  observation: string | null;
};

export type ExpertRepetition = {
  repetition_index: number;
  start_seconds: number;
  peak_depth_seconds: number;
  end_seconds: number;
};

export type ExpertEvaluation = {
  evaluation_id: string;
  status: "draft" | "submitted";
  general_observation: string | null;
  created_at: string | null;
  updated_at: string | null;
  submitted_at: string | null;
  items: ExpertEvaluationItem[];
};

export type ExpertAssignment = {
  assignment_id: string;
  case_id: string;
  status: "pending" | "in_progress" | "submitted";
  created_at: string;
  updated_at: string;
  repetitions: ExpertRepetition[];
  evaluation: ExpertEvaluation | null;
};
