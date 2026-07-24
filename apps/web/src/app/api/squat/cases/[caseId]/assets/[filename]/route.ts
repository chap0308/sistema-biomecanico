import { getApiBaseUrl } from "@/lib/api/config";
import { createClient } from "@/lib/supabase/server";

type AssetRouteContext = {
  params: Promise<{ caseId: string; filename: string }>;
};

export async function GET(request: Request, context: AssetRouteContext) {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session?.access_token) {
    return new Response("No autorizado", { status: 401 });
  }

  const { caseId, filename } = await context.params;
  const range = request.headers.get("range");
  const response = await fetch(
    `${getApiBaseUrl()}/squat/cases/${encodeURIComponent(caseId)}/assets/${encodeURIComponent(filename)}`,
    {
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${session.access_token}`,
        ...(range ? { Range: range } : {}),
      },
    },
  );
  if (!response.ok && response.status !== 206) {
    return new Response("Artefacto no disponible", {
      status: response.status,
    });
  }

  const headers = new Headers();
  for (const name of [
    "accept-ranges",
    "content-disposition",
    "content-length",
    "content-range",
    "content-type",
  ]) {
    const value = response.headers.get(name);
    if (value) headers.set(name, value);
  }
  headers.set("Cache-Control", "private, no-store");
  return new Response(response.body, {
    status: response.status,
    headers,
  });
}
