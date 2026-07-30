import type {
  ExpertEvaluationObservation,
  ExpertEvaluationItem,
  ExpertObservedSide,
  ExpertPatternKey,
} from "@/types/squat-expert";

export type ExpertJudgment = ExpertEvaluationItem & {
  evaluator_id: string;
};

export type FinalReference = {
  classification: "presente" | "ausente" | "no_concluyente";
  observed_side: ExpertObservedSide | null;
  method:
    | "coincidencia_directa"
    | "mayoria_absoluta"
    | "consenso_guiado";
  observation: string | null;
  label: string;
};

export type PatternComparison = {
  repetition_index: number;
  pattern_key: ExpertPatternKey;
  expert_judgments: ExpertJudgment[];
  reference: FinalReference | null;
  reference_status:
    | "consolidada"
    | "consenso_requerido"
    | "evaluaciones_pendientes";
  system_classification: "presente" | "ausente" | "no_concluyente";
  system_side: string | null;
  system_label: string;
  exact_match: boolean | null;
  binary_outcome: "TP" | "TN" | "FP" | "FN" | null;
};

export type CaseComparison = {
  case_id: string;
  assigned_evaluators: number;
  submitted_evaluations: number;
  reference_status: "open" | "in_progress" | "closed";
  patterns: PatternComparison[];
  evaluator_observations: ExpertEvaluationObservation[];
  ready_for_metrics: boolean;
  expert_fleiss_kappa: number | null;
  fleiss_items: number;
};

export type PerformanceMetrics = {
  scope: string;
  included_pairs: number;
  excluded_inconclusive_pairs: number;
  true_positive: number;
  true_negative: number;
  false_positive: number;
  false_negative: number;
  accuracy: number | null;
  precision: number | null;
  sensitivity: number | null;
  specificity: number | null;
  f1_score: number | null;
  exact_agreement: number | null;
  cohen_kappa: number | null;
};

export type DatasetPerformance = {
  consolidated_cases: number;
  pending_cases: number;
  overall: PerformanceMetrics;
  by_pattern: PerformanceMetrics[];
};
