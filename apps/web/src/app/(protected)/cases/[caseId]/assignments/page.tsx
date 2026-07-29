import Link from "next/link";
import { ArrowLeftIcon, ShieldCheckIcon } from "lucide-react";

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
import type {
  CaseAssignmentRoster,
  ExpertProfile,
} from "@/types/squat-expert";

import { AssignmentForm } from "./assignment-form";

type AssignmentPageProps = {
  params: Promise<{ caseId: string }>;
};

export default async function AssignmentPage({
  params,
}: AssignmentPageProps) {
  await requireRole("investigator");
  const { caseId } = await params;
  let experts: ExpertProfile[] = [];
  let roster: CaseAssignmentRoster | null = null;
  let unavailable = false;
  try {
    [experts, roster] = await Promise.all([
      apiServerFetch<ExpertProfile[]>("/squat/experts"),
      apiServerFetch<CaseAssignmentRoster>(
        `/squat/cases/${encodeURIComponent(caseId)}/assignments`,
      ),
    ]);
  } catch {
    unavailable = true;
  }

  return (
    <main className="mx-auto w-full max-w-3xl px-6 py-10 lg:px-10">
      <Link
        href={`/cases/${caseId}`}
        className={buttonVariants({ size: "sm", variant: "ghost", className: "-ml-3" })}
      >
        <ArrowLeftIcon aria-hidden="true" />
        Volver al caso
      </Link>
      <Badge variant="secondary" className="mt-6">
        Evaluación ciega
      </Badge>
      <h1 className="mt-4 text-3xl font-semibold tracking-tight">
        Asignar evaluadores
      </h1>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        Caso <span className="font-mono">{caseId}</span>. Los expertos recibirán
        únicamente el video anonimizado y el Instrumento 3.
      </p>

      <Card className="mt-8">
        <CardHeader>
          <div className="grid size-10 place-items-center rounded-lg bg-primary/10 text-primary">
            <ShieldCheckIcon className="size-5" aria-hidden="true" />
          </div>
          <CardTitle>Expertos en análisis del movimiento</CardTitle>
          <CardDescription>
            Selecciona hasta tres cuentas. Las asignaciones repetidas se omiten.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {unavailable ? (
            <p className="text-sm text-destructive">
              No se pudo consultar la lista de evaluadores.
            </p>
          ) : experts.length ? (
            <AssignmentForm
              caseId={caseId}
              experts={experts}
              roster={roster}
            />
          ) : (
            <p className="text-sm text-muted-foreground">
              No existen cuentas expertas configuradas.
            </p>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
