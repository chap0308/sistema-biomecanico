import { getApiBaseUrl } from "@/lib/api/config";
import { createClient } from "@/lib/supabase/server";

type ExportRouteContext = {
  params: Promise<{ caseId: string; filename: string }>;
};

export async function GET(_request: Request, context: ExportRouteContext) {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session?.access_token) {
    return new Response("No autorizado", { status: 401 });
  }

  const { caseId, filename } = await context.params;
  if (
    ![
      "instruments.xlsx",
      "report.pdf",
      "technical-data.xlsx",
    ].includes(filename)
  ) {
    return new Response("Exportación no disponible", { status: 404 });
  }
  const response = await fetch(
    `${getApiBaseUrl()}/squat/cases/${encodeURIComponent(caseId)}/exports/${encodeURIComponent(filename)}`,
    {
      cache: "no-store",
      headers: { Authorization: `Bearer ${session.access_token}` },
    },
  );
  if (!response.ok) {
    return new Response("Exportación no disponible", {
      status: response.status,
    });
  }
  const headers = new Headers();
  for (const name of [
    "content-disposition",
    "content-length",
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
