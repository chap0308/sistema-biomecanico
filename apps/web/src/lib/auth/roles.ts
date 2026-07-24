export const SQUAT_ROLES = ["investigator", "expert"] as const;

export type SquatRole = (typeof SQUAT_ROLES)[number];

export type ResearchProfile = {
  displayName: string;
  email: string;
  role: SquatRole;
  userId: string;
};

export function isSquatRole(value: unknown): value is SquatRole {
  return typeof value === "string" && SQUAT_ROLES.includes(value as SquatRole);
}

export function homeForRole(role: SquatRole): "/cases" | "/expert/assignments" {
  return role === "investigator" ? "/cases" : "/expert/assignments";
}
