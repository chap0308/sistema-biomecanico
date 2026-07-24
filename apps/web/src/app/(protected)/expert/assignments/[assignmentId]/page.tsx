import Link from "next/link";
import { ArrowLeftIcon, EyeOffIcon, ShieldCheckIcon } from "lucide-react";

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
import type { ExpertAssignment } from "@/types/squat-expert";

import { EvaluationForm } from "./evaluation-form";

type ExpertAssignmentPageProps = {
  params: Promise<{ assignmentId: string }>;
};

export default async function ExpertAssignmentPage({
  params,
}: ExpertAssignmentPageProps) {
  await requireRole("expert");
  const { assignmentId } = await params;
  let assignment: ExpertAssignment | null = null;
  try {
    assignment = await apiServerFetch<ExpertAssignment>(
      `/squat/expert/assignments/${assignmentId}`,
    );
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
      <Link
        href="/expert/assignments"
        className={buttonVariants({
          size: "sm",
          variant: "ghost",
          className: "-ml-3",
        })}
      >
        <ArrowLeftIcon aria-hidden="true" />
        Volver a asignaciones
      </Link>

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

      <Alert className="mt-6">
        <ShieldCheckIcon aria-hidden="true" />
        <AlertDescription>
          Las métricas, umbrales y clasificaciones del sistema no están
          disponibles en esta pantalla.
        </AlertDescription>
      </Alert>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Video de revisión anonimizado</CardTitle>
          <CardDescription>
            Puedes pausar, repetir y avanzar libremente antes de emitir el juicio.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-hidden rounded-xl border bg-slate-950">
            <video
              className="aspect-video w-full object-contain"
              controls
              preload="metadata"
              src={`/api/squat/expert/assignments/${assignment.assignment_id}/video`}
            >
              Tu navegador no admite la reproducción de video.
            </video>
          </div>
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
    </main>
  );
}

function assignmentStatus(status: ExpertAssignment["status"]) {
  return {
    pending: "Pendiente",
    in_progress: "Borrador guardado",
    submitted: "Evaluación enviada",
  }[status];
}
