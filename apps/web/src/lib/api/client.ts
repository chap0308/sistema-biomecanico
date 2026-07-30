"use client";

import { getApiBaseUrl } from "@/lib/api/config";
import { createClient } from "@/lib/supabase/client";

export async function apiClientFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new Error("La sesión expiró. Vuelve a iniciar sesión.");
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${session.access_token}`,
      ...init?.headers,
    },
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      | { detail?: string }
      | null;
    throw new Error(payload?.detail ?? `Error ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  const body = await response.text();
  return (body ? JSON.parse(body) : undefined) as T;
}
