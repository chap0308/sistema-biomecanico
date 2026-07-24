import "server-only";

import { getApiBaseUrl } from "@/lib/api/config";
import { createClient } from "@/lib/supabase/server";

export async function apiServerFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    throw new Error("No authenticated API session is available.");
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${session.access_token}`,
      ...init?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}.`);
  }
  return (await response.json()) as T;
}
