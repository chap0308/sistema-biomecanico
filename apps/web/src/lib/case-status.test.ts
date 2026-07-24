import { describe, expect, it } from "vitest";

import { formatCaseStatus } from "@/lib/case-status";

describe("formatCaseStatus", () => {
  it("uses formal Spanish labels for internal states", () => {
    expect(formatCaseStatus("processing")).toBe("En procesamiento");
    expect(formatCaseStatus("excluded")).toBe("No incorporado");
  });
});
