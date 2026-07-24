export const CASE_STATUS_LABELS = {
  draft: "Borrador",
  uploaded: "Cargado",
  under_review: "En revisión",
  processing: "En procesamiento",
  completed: "Completado",
  excluded: "No incorporado",
  inconclusive: "No concluyente",
  failed: "Error de procesamiento",
} as const;

export type CaseStatus = keyof typeof CASE_STATUS_LABELS;

export function formatCaseStatus(status: CaseStatus): string {
  return CASE_STATUS_LABELS[status];
}
