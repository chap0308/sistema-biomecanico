import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { apiClientFetch } from "@/lib/api/client";

import { ReferenceLifecycleControls } from "./reference-lifecycle-controls";

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
    vi.mocked(apiClientFetch).mockResolvedValue(undefined);

    render(
      <ReferenceLifecycleControls
        caseId="case-1"
        status="in_progress"
        readyForMetrics
        assignedEvaluators={2}
        submittedEvaluations={2}
      />,
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
});
