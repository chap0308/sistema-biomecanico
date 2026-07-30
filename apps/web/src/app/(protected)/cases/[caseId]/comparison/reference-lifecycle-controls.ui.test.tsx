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
import { ReferenceLifecycleControls } from "./reference-lifecycle-controls";
import {
  ReferenceReviewProvider,
} from "./reference-review-context";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

vi.mock("@/lib/api/client", () => ({
  apiClientFetch: vi.fn(),
}));

describe("ReferenceLifecycleControls", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("enables final exports immediately after closing the case", async () => {
    const comparison = comparisonWithStatus("in_progress", true);
    vi.mocked(apiClientFetch).mockResolvedValue(
      comparisonWithStatus("closed", true),
    );

    render(
      <ReferenceReviewProvider initialComparison={comparison}>
        <ReferenceLifecycleControls caseId="case-1" />
      </ReferenceReviewProvider>,
    );

    expect(
      screen.getByRole("button", { name: "Instrumentos Excel" }),
    ).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "Cerrar caso" }));
    fireEvent.click(
      screen.getByRole("button", { name: "Cerrar definitivamente" }),
    );

    await waitFor(() => {
      expect(screen.getByText("Caso cerrado")).toBeInTheDocument();
    });
    expect(
      screen.getByRole("link", { name: "Instrumentos Excel" }),
    ).toHaveAttribute(
      "href",
      "/api/squat/cases/case-1/exports/instruments.xlsx",
    );
    expect(screen.getByRole("link", { name: "Reporte PDF" })).toHaveAttribute(
      "href",
      "/api/squat/cases/case-1/exports/report.pdf",
    );
    expect(refresh).toHaveBeenCalledOnce();
  });

  it("updates the review state immediately after starting", async () => {
    vi.mocked(apiClientFetch).mockResolvedValue(
      comparisonWithStatus("in_progress", false),
    );

    render(
      <ReferenceReviewProvider
        initialComparison={comparisonWithStatus("open", false)}
      >
        <ReferenceLifecycleControls caseId="case-1" />
        <PatternComparisonCard
          caseId="case-1"
          initialPattern={pendingPattern}
        />
      </ReferenceReviewProvider>,
    );

    fireEvent.click(
      screen.getByRole("button", { name: "Comenzar referencia final" }),
    );
    fireEvent.click(screen.getByRole("button", { name: "Comenzar revisión" }));

    await waitFor(() => {
      expect(screen.getByLabelText("Referencia final")).toBeInTheDocument();
    });
    expect(screen.getAllByText("Pendiente").length).toBeGreaterThan(0);
    expect(
      screen.getByRole("button", { name: "Registrar referencia" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Cerrar caso" }),
    ).toBeDisabled();
  });
});

const pendingPattern = {
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

function comparisonWithStatus(
  referenceStatus: CaseComparison["reference_status"],
  readyForMetrics: boolean,
): CaseComparison {
  return {
    case_id: "case-1",
    assigned_evaluators: 2,
    submitted_evaluations: 2,
    reference_status: referenceStatus,
    patterns: [pendingPattern],
    evaluator_observations: [],
    ready_for_metrics: readyForMetrics,
    expert_fleiss_kappa: null,
    fleiss_items: 0,
  };
}
