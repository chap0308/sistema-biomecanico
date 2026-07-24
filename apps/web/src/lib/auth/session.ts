import "server-only";

import { redirect } from "next/navigation";

import {
  type ResearchProfile,
  type SquatRole,
  isSquatRole,
} from "@/lib/auth/roles";
import { createClient } from "@/lib/supabase/server";

type ProfileRow = {
  display_name: string | null;
  email: string | null;
  squat_role: string | null;
};

export async function requireResearchProfile(): Promise<ResearchProfile> {
  const supabase = await createClient();
  const { data: claimsData, error: claimsError } =
    await supabase.auth.getClaims();
  const userId = claimsData?.claims?.sub;

  if (claimsError || !userId) {
    redirect("/login");
  }

  const { data, error } = await supabase
    .from("profiles")
    .select("display_name,email,squat_role")
    .eq("user_id", userId)
    .single<ProfileRow>();

  if (error || !data || !isSquatRole(data.squat_role)) {
    redirect("/login?error=profile");
  }

  return {
    displayName: data.display_name ?? data.email ?? "Usuario",
    email: data.email ?? "",
    role: data.squat_role,
    userId,
  };
}

export async function requireRole(role: SquatRole): Promise<ResearchProfile> {
  const profile = await requireResearchProfile();
  if (profile.role !== role) {
    redirect(profile.role === "investigator" ? "/cases" : "/expert/assignments");
  }
  return profile;
}
