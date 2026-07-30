/* eslint-disable @next/next/no-html-link-for-pages -- Full navigation avoids a stale authenticated RSC transition. */
import {
  ArrowLeftIcon,
  EyeIcon,
  EyeOffIcon,
  ShieldCheckIcon,
} from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiServerFetch } from "@/lib/api/server";
import { requireRole } from "@/lib/auth/session";
import type { SquatCaseReport } from "@/types/squat-case-report";
import type { ExpertAssignment } from "@/types/squat-expert";

import { EvaluationForm } from "./evaluation-form";
import { ExpertReviewPlayer } from "./expert-review-player";

type ExpertAssignmentPageProps = {
  params: Promise<{ assignmentId: string }>;
};

export default async function ExpertAssignmentPage({
  params,
}: ExpertAssignmentPageProps) {
  await requireRole("expert");
  const { assignmentId } = await params;
  let assignment: ExpertAssignment | null = null;
  let systemReport: SquatCaseReport | null = null;
  try {
    assignment = await apiServerFetch<ExpertAssignment>(
      `/squat/expert/assignments/${assignmentId}`,
    );
    if (assignment.reference_status === "closed") {
      systemReport = await apiServerFetch<SquatCaseReport>(
        `/squat/expert/assignments/${assignmentId}/system-results`,
      );
    }
  } catch {
    // The explicit unavailable state below avoids exposing backend details.
  }

  if (!assignment) {
    return (
      <main className="mx-auto w-full max-w-4xl px-6 py-10 lg:px-10">
        <Card className="border-destructive/35">
          <CardHeader>
            <CardTitle>Asignación no disponible</CardTitle>
            <CardDescription>
              El caso no existe o no está asignado a tu cuenta.
            </CardDescription>
          </CardHeader>
        </Card>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10 lg:px-10">
      <a
        href="/expert/assignments"
        className={buttonVariants({
          size: "sm",
          variant: "ghost",
          className: "-ml-3",
        })}
      >
        <ArrowLeftIcon aria-hidden="true" />
        Volver a asignaciones
      </a>

      <div className="mt-6 flex flex-wrap items-center gap-2">
        <Badge variant="secondary">
          <EyeOffIcon aria-hidden="true" />
          Evaluación ciega
        </Badge>
        <Badge variant="outline">{assignmentStatus(assignment.status)}</Badge>
      </div>
      <h1 className="mt-4 text-3xl font-semibold tracking-tight">
        Instrumento 3
      </h1>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        Video <span className="font-mono">{assignment.case_id}</span>. Clasifica
        únicamente lo observable, sin inferir diagnósticos o causas anatómicas.
      </p>

      {assignment.reference_status === "closed" ? (
        <Alert className="mt-6">
          <EyeIcon aria-hidden="true" />
          <AlertDescription>
            El caso fue cerrado. El análisis del sistema ya está disponible
            debajo de tu evaluación.
          </AlertDescription>
        </Alert>
      ) : (
        <Alert className="mt-6">
          <ShieldCheckIcon aria-hidden="true" />
          <AlertDescription>
            Las métricas, umbrales y clasificaciones del sistema permanecen
            ocultas hasta el cierre definitivo del caso.
          </AlertDescription>
        </Alert>
      )}

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Video de revisión anonimizado</CardTitle>
          <CardDescription>
            Puedes pausar, repetir y avanzar libremente antes de emitir el juicio.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ExpertReviewPlayer
            assignmentId={assignment.assignment_id}
            repetitions={assignment.repetitions ?? []}
          />
        </CardContent>
      </Card>

      <section className="mt-8">
        <div className="mb-5">
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
            Clasificación observacional
          </p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight">
            Patrones del movimiento
          </h2>
        </div>
        <EvaluationForm assignment={assignment} />
      </section>

      {systemReport ? <SystemResults report={systemReport} /> : null}
    </main>
  );
}

function SystemResults({ report }: { report: SquatCaseReport }) {
  return (
    <section className="mt-10 border-t pt-8">
      <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
        Resultado revelado
      </p>
      <h2 className="mt-2 text-2xl font-semibold tracking-tight">
        Clasificaciones del sistema
      </h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Estas salidas aparecen después del cierre para preservar la
        independencia de la evaluación experta.
      </p>
      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {(report.findings?.decisions ?? []).map((decision, index) => (
          <Card key={`${decision.repetition_index}-${decision.finding}-${index}`}>
            <CardHeader className="pb-2">
              <CardDescription>
                Repetición {decision.repetition_index ?? 1}
              </CardDescription>
              <CardTitle className="text-base capitalize">
                {String(decision.finding).replaceAll("_", " ")}
              </CardTitle>
            </CardHeader>
            <CardContent className="flex items-center justify-between gap-3 text-sm">
              <Badge className="capitalize">
                {String(decision.status).replaceAll("_", " ")}
              </Badge>
              <span className="font-mono text-muted-foreground">
                {decision.aggregate_value ?? "N/D"} {decision.unit}
              </span>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}

function assignmentStatus(status: ExpertAssignment["status"]) {
  return {
    pending: "Pendiente",
    in_progress: "Borrador guardado",
    submitted: "Evaluación enviada",
  }[status];
}
