import {
  CheckCircle2Icon,
  ChevronRightIcon,
  ClipboardCheckIcon,
  Clock3Icon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiServerFetch } from "@/lib/api/server";
import { requireRole } from "@/lib/auth/session";
import type { ExpertAssignment } from "@/types/squat-expert";

export default async function ExpertAssignmentsPage() {
  await requireRole("expert");
  let assignments: ExpertAssignment[] = [];
  let unavailable = false;
  try {
    assignments = await apiServerFetch<ExpertAssignment[]>(
      "/squat/expert/assignments",
    );
  } catch {
    unavailable = true;
  }

  return (
    <main className="mx-auto w-full max-w-6xl px-6 py-10 lg:px-10">
      <Badge variant="secondary">Evaluación ciega</Badge>
      <h1 className="mt-4 text-4xl font-semibold tracking-tight">
        Casos asignados
      </h1>
      <p className="mt-2 max-w-2xl leading-6 text-muted-foreground">
        Revisa cada video de forma independiente. Las métricas y clasificaciones
        del sistema permanecen ocultas durante esta fase.
      </p>

      {unavailable ? (
        <Card className="mt-10 border-destructive/35">
          <CardHeader>
            <CardTitle>No se pudieron consultar las asignaciones</CardTitle>
            <CardDescription>
              Verifica la conexión con FastAPI e intenta nuevamente.
            </CardDescription>
          </CardHeader>
        </Card>
      ) : assignments.length ? (
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {assignments.map((assignment) => (
            <a
              key={assignment.assignment_id}
              href={`/expert/assignments/${assignment.assignment_id}`}
              className="group"
            >
              <Card className="h-full transition-colors group-hover:border-primary/45">
                <CardHeader className="flex-row items-start justify-between gap-4">
                  <div>
                    <CardDescription>Código del video</CardDescription>
                    <CardTitle className="mt-1 font-mono text-lg">
                      {assignment.case_id}
                    </CardTitle>
                  </div>
                  <AssignmentStatus status={assignment.status} />
                </CardHeader>
                <CardContent className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>
                    Asignado el{" "}
                    {new Intl.DateTimeFormat("es-PE", {
                      dateStyle: "medium",
                    }).format(new Date(assignment.created_at))}
                  </span>
                  <ChevronRightIcon
                    className="size-4 transition-transform group-hover:translate-x-1"
                    aria-hidden="true"
                  />
                </CardContent>
              </Card>
            </a>
          ))}
        </div>
      ) : (
        <Card className="mt-10 border-dashed">
          <CardHeader>
            <div className="mb-2 grid size-11 place-items-center rounded-full bg-secondary">
              <ClipboardCheckIcon aria-hidden="true" />
            </div>
            <CardTitle>Sin casos pendientes</CardTitle>
            <CardDescription>
              Las nuevas asignaciones aparecerán en esta bandeja.
            </CardDescription>
          </CardHeader>
        </Card>
      )}
    </main>
  );
}

function AssignmentStatus({
  status,
}: {
  status: ExpertAssignment["status"];
}) {
  if (status === "submitted") {
    return (
      <Badge variant="secondary">
        <CheckCircle2Icon aria-hidden="true" />
        Enviada
      </Badge>
    );
  }
  if (status === "in_progress") {
    return (
      <Badge variant="outline">
        <Clock3Icon aria-hidden="true" />
        Borrador
      </Badge>
    );
  }
  return <Badge>Pendiente</Badge>;
}
