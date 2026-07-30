"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { DownloadIcon, LockIcon, LockKeyholeIcon } from "lucide-react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button, buttonVariants } from "@/components/ui/button";
import { apiClientFetch } from "@/lib/api/client";
import type { CaseComparison } from "@/types/squat-comparison";

import { useReferenceReview } from "./reference-review-context";

export function ReferenceLifecycleControls({
  caseId,
}: {
  caseId: string;
}) {
  const router = useRouter();
  const { comparison, updateComparison } = useReferenceReview();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string>();
  const currentStatus = comparison.reference_status;

  async function advance(action: "start" | "close") {
    setPending(true);
    setError(undefined);
    try {
      const updatedComparison = await apiClientFetch<CaseComparison>(
        `/squat/cases/${encodeURIComponent(caseId)}/reference/${action}`,
        { method: "POST" },
      );
      updateComparison(updatedComparison);
      router.refresh();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "No se pudo actualizar el estado del caso.",
      );
    } finally {
      setPending(false);
    }
  }

  const starting = currentStatus === "open";
  const everyEvaluatorSubmitted = canStartReferenceReview(
    comparison.assigned_evaluators,
    comparison.submitted_evaluations,
  );

  if (currentStatus === "closed") {
    return (
      <div className="contents">
        <div className="flex items-center gap-2 text-sm font-medium text-primary">
          <LockIcon className="size-4" aria-hidden="true" />
          Caso cerrado
        </div>
        <DownloadLinks caseId={caseId} enabled />
      </div>
    );
  }

  return (
    <div className="contents">
      <div className="grid justify-items-end gap-1.5">
        <AlertDialog>
          <AlertDialogTrigger
            render={
              <Button
                type="button"
                size="sm"
                variant={starting ? "outline" : "destructive"}
                disabled={
                  pending ||
                  (starting && !everyEvaluatorSubmitted) ||
                  (!starting && !comparison.ready_for_metrics)
                }
              />
            }
          >
            <LockKeyholeIcon aria-hidden="true" />
            {starting ? "Comenzar referencia final" : "Cerrar caso"}
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>
                {starting
                  ? "¿Comenzar la referencia final?"
                  : "¿Cerrar el caso definitivamente?"}
              </AlertDialogTitle>
              <AlertDialogDescription>
                {starting
                  ? "La nómina de evaluadores quedará bloqueada. Ya no podrás agregar ni retirar expertos, pero sí seleccionar y editar referencias finales."
                  : "Las referencias finales ya no podrán editarse. Los expertos asignados podrán consultar el análisis del sistema."}
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancelar</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => advance(starting ? "start" : "close")}
              >
                {starting ? "Comenzar revisión" : "Cerrar definitivamente"}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
        {starting && !everyEvaluatorSubmitted ? (
          <p className="max-w-sm text-right text-xs text-muted-foreground">
            La revisión comenzará cuando todos los evaluadores asignados hayan
            enviado sus respuestas ({comparison.submitted_evaluations}/
            {comparison.assigned_evaluators}).
          </p>
        ) : null}
        {error ? (
          <p className="max-w-sm text-right text-xs text-destructive">{error}</p>
        ) : null}
      </div>
      <DownloadLinks caseId={caseId} enabled={false} />
    </div>
  );
}

function DownloadLinks({
  caseId,
  enabled,
}: {
  caseId: string;
  enabled: boolean;
}) {
  if (enabled) {
    return (
      <>
        <a
          href={`/api/squat/cases/${caseId}/exports/instruments.xlsx`}
          className={buttonVariants({ size: "sm", variant: "outline" })}
        >
          <DownloadIcon aria-hidden="true" />
          Instrumentos Excel
        </a>
        <a
          href={`/api/squat/cases/${caseId}/exports/report.pdf`}
          className={buttonVariants({ size: "sm" })}
        >
          <DownloadIcon aria-hidden="true" />
          Reporte PDF
        </a>
      </>
    );
  }
  return (
    <>
      <Button
        type="button"
        size="sm"
        variant="outline"
        disabled
        title="Cierra el caso para habilitar la descarga."
      >
        <DownloadIcon aria-hidden="true" />
        Instrumentos Excel
      </Button>
      <Button
        type="button"
        size="sm"
        disabled
        title="Cierra el caso para habilitar la descarga."
      >
        <DownloadIcon aria-hidden="true" />
        Reporte PDF
      </Button>
    </>
  );
}

export function canStartReferenceReview(
  assignedEvaluators: number,
  submittedEvaluations: number,
) {
  return (
    assignedEvaluators > 0 && submittedEvaluations === assignedEvaluators
  );
}
