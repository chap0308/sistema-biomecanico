"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { LockIcon, LockKeyholeIcon } from "lucide-react";

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
import { Button } from "@/components/ui/button";
import { apiClientFetch } from "@/lib/api/client";
import type { CaseComparison } from "@/types/squat-comparison";

export function ReferenceLifecycleControls({
  caseId,
  status,
  readyForMetrics,
}: {
  caseId: string;
  status: CaseComparison["reference_status"];
  readyForMetrics: boolean;
}) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string>();

  async function advance(action: "start" | "close") {
    setPending(true);
    setError(undefined);
    try {
      await apiClientFetch(
        `/squat/cases/${encodeURIComponent(caseId)}/reference/${action}`,
        { method: "POST" },
      );
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

  if (status === "closed") {
    return (
      <div className="flex items-center gap-2 text-sm font-medium text-primary">
        <LockIcon className="size-4" aria-hidden="true" />
        Caso cerrado
      </div>
    );
  }

  const starting = status === "open";
  return (
    <div className="grid justify-items-end gap-1.5">
      <AlertDialog>
        <AlertDialogTrigger
          render={
            <Button
              type="button"
              size="sm"
              variant={starting ? "outline" : "destructive"}
              disabled={pending || (!starting && !readyForMetrics)}
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
      {error ? (
        <p className="max-w-sm text-right text-xs text-destructive">{error}</p>
      ) : null}
    </div>
  );
}
