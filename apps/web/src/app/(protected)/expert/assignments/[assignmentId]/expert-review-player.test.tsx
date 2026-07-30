import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ExpertReviewPlayer } from "./expert-review-player";

describe("ExpertReviewPlayer", () => {
  beforeEach(() => {
    vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("supports legacy assignments without repetition metadata", () => {
    render(<ExpertReviewPlayer assignmentId="assignment-1" />);

    expect(screen.getByText(/no admite la reproducción/i)).toBeInTheDocument();
    expect(screen.queryByText("Repetición 1")).not.toBeInTheDocument();
  });

  it("shows the selected repetition and its analysis interval", () => {
    render(
      <ExpertReviewPlayer
        assignmentId="assignment-1"
        repetitions={[
          {
            repetition_index: 2,
            start_seconds: 4.2,
            peak_depth_seconds: 5.1,
            end_seconds: 6.4,
          },
        ]}
        activeRepetition={2}
      />,
    );

    expect(screen.getAllByText("Repetición 2")).toHaveLength(2);
    expect(screen.getByText("4.20–6.40 s")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Video completo" }),
    ).toBeInTheDocument();
  });
});
