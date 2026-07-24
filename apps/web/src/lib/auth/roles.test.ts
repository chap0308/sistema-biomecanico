import { describe, expect, it } from "vitest";

import { homeForRole, isSquatRole } from "@/lib/auth/roles";

describe("research roles", () => {
  it("accepts only supported study roles", () => {
    expect(isSquatRole("investigator")).toBe(true);
    expect(isSquatRole("expert")).toBe(true);
    expect(isSquatRole("admin")).toBe(false);
  });

  it("maps each role to a protected home route", () => {
    expect(homeForRole("investigator")).toBe("/cases");
    expect(homeForRole("expert")).toBe("/expert/assignments");
  });
});
