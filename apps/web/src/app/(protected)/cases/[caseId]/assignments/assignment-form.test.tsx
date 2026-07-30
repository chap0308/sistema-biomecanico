import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { apiClientFetch } from "@/lib/api/client";
import type { CaseAssignmentRoster } from "@/types/squat-expert";

import { AssignmentForm } from "./assignment-form";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

vi.mock("@/lib/api/client", () => ({
  apiClientFetch: vi.fn(),
}));

const expert = {
  user_id: "expert-1",
  email: "expert1@example.test",
  display_name: "Experto uno",
  role: "expert" as const,
};

describe("AssignmentForm", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("adds an evaluator and refreshes the visible roster", async () => {
    const updatedRoster: CaseAssignmentRoster = {
      case_id: "case-1",
      reference_status: "open",
      assignments: [
        {
          assignment_id: "assignment-1",
          evaluator_id: expert.user_id,
          email: expert.email,
          display_name: expert.display_name,
          status: "pending",
          has_response: false,
        },
      ],
    };
    vi.mocked(apiClientFetch)
      .mockResolvedValueOnce({ assigned: 1 })
      .mockResolvedValueOnce(updatedRoster);

    render(
      <AssignmentForm
        caseId="case-1"
        experts={[expert]}
        roster={{
          case_id: "case-1",
          reference_status: "open",
          assignments: [],
        }}
      />,
    );

    fireEvent.click(screen.getByRole("checkbox", { name: /Experto uno/ }));
    fireEvent.click(screen.getByRole("button", { name: "Asignar caso" }));

    await waitFor(() => {
      expect(screen.getByText("Evaluadores asignados (1/3)")).toBeInTheDocument();
    });
    expect(screen.getByText("1 asignación(es) creada(s).")).toBeInTheDocument();
    expect(refresh).toHaveBeenCalledOnce();
  });

  it("removes an evaluator from the visible roster after confirmation", async () => {
    vi.mocked(apiClientFetch).mockResolvedValue(undefined);

    render(
      <AssignmentForm
        caseId="case-1"
        experts={[expert]}
        roster={{
          case_id: "case-1",
          reference_status: "open",
          assignments: [
            {
              assignment_id: "assignment-1",
              evaluator_id: expert.user_id,
              email: expert.email,
              display_name: expert.display_name,
              status: "submitted",
              has_response: true,
            },
          ],
        }}
      />,
    );

    fireEvent.click(
      screen.getByRole("button", { name: "Retirar evaluador" }),
    );
    expect(
      screen.getByText(/Su borrador o respuesta enviada se eliminará/),
    ).toBeInTheDocument();
    fireEvent.click(
      screen.getByRole("button", { name: "Retirar evaluador" }),
    );

    await waitFor(() => {
      expect(
        screen.queryByText("Evaluadores asignados (1/3)"),
      ).not.toBeInTheDocument();
    });
    expect(refresh).toHaveBeenCalledOnce();
  });
});
