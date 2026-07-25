import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ExpertReviewPlayer } from "./expert-review-player";

describe("ExpertReviewPlayer", () => {
  it("supports legacy assignments without repetition metadata", () => {
    render(<ExpertReviewPlayer assignmentId="assignment-1" />);

    expect(screen.getByText(/no admite la reproducción/i)).toBeInTheDocument();
    expect(screen.queryByText("Repetición 1")).not.toBeInTheDocument();
  });
});
