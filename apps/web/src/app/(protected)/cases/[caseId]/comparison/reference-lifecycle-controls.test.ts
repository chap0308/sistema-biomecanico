import { describe, expect, it } from "vitest";

import { canStartReferenceReview } from "./reference-lifecycle-controls";

describe("canStartReferenceReview", () => {
  it("requires at least one assignment and every submitted evaluation", () => {
    expect(canStartReferenceReview(0, 0)).toBe(false);
    expect(canStartReferenceReview(3, 2)).toBe(false);
    expect(canStartReferenceReview(3, 3)).toBe(true);
  });
});
