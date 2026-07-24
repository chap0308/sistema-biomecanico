"use server";

import { redirect } from "next/navigation";

import { homeForRole, isSquatRole } from "@/lib/auth/roles";
import { createClient } from "@/lib/supabase/server";

export type LoginState = {
  error?: string;
};

export async function login(
  _previousState: LoginState,
  formData: FormData,
): Promise<LoginState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  if (!email || !password) {
    return { error: "Ingresa el correo y la contraseña." };
  }

  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    return { error: "No se pudo validar la cuenta indicada." };
  }

  const { data: profile } = await supabase
    .from("profiles")
    .select("squat_role")
    .single<{ squat_role: string | null }>();

  if (!profile || !isSquatRole(profile.squat_role)) {
    await supabase.auth.signOut();
    return {
      error: "La cuenta no tiene un rol habilitado para este estudio.",
    };
  }

  redirect(homeForRole(profile.squat_role));
}

export async function logout(): Promise<never> {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/login");
}
