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
  pattern_key: ExpertPatternKey;
  classification: "presente" | "ausente" | "no_concluyente";
  observed_side: ExpertObservedSide | null;
  confidence: "baja" | "media" | "alta" | null;
  observation: string | null;
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
  evaluation: ExpertEvaluation | null;
};
