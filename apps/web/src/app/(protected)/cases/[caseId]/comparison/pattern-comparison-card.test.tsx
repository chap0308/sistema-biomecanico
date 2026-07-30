import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { apiClientFetch } from "@/lib/api/client";
import type { CaseComparison } from "@/types/squat-comparison";

import { PatternComparisonCard } from "./pattern-comparison-card";
import { ReferenceReviewProvider } from "./reference-review-context";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: vi.fn() }),
}));

vi.mock("@/lib/api/client", () => ({
  apiClientFetch: vi.fn(),
}));

const initialPattern = {
  repetition_index: 1,
  pattern_key: "trunk_lateral_inclination" as const,
  expert_judgments: [
    {
      evaluator_id: "expert-1",
      repetition_index: 1,
      pattern_key: "trunk_lateral_inclination" as const,
      classification: "ausente" as const,
      observed_side: null,
      confidence: "alta" as const,
      observation: null,
    },
  ],
  reference: null,
  reference_status: "consenso_requerido" as const,
  system_classification: "ausente" as const,
  system_side: null,
  system_label: "Ausente",
  exact_match: null,
  binary_outcome: null,
};

describe("PatternComparisonCard", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("updates the visible reference from the save response", async () => {
    const updatedPattern = {
      ...initialPattern,
      reference: {
        classification: "ausente" as const,
        observed_side: null,
        method: "consenso_guiado" as const,
        observation: null,
        label: "Ausente",
      },
      reference_status: "consolidada" as const,
      exact_match: true,
      binary_outcome: "TN" as const,
    };
    const comparison: CaseComparison = {
      case_id: "case-1",
      assigned_evaluators: 1,
      submitted_evaluations: 1,
      reference_status: "in_progress",
      patterns: [updatedPattern],
      evaluator_observations: [],
      ready_for_metrics: true,
      expert_fleiss_kappa: null,
      fleiss_items: 0,
    };
    vi.mocked(apiClientFetch).mockResolvedValue(comparison);

    render(
      <ReferenceReviewProvider
        initialComparison={{
          case_id: "case-1",
          assigned_evaluators: 1,
          submitted_evaluations: 1,
          reference_status: "in_progress",
          patterns: [initialPattern],
          evaluator_observations: [],
          ready_for_metrics: false,
          expert_fleiss_kappa: null,
          fleiss_items: 0,
        }}
      >
        <PatternComparisonCard
          caseId="case-1"
          initialPattern={initialPattern}
        />
      </ReferenceReviewProvider>,
    );

    fireEvent.change(screen.getByLabelText("Referencia final"), {
      target: { value: "ausente" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Registrar referencia" }),
    );

    await waitFor(() => {
      expect(screen.getByText("Coincide")).toBeInTheDocument();
    });
    expect(
      screen.getByRole("button", { name: "Guardar cambios" }),
    ).toBeInTheDocument();
  });
});
