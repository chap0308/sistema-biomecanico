"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import {
  CheckCircle2Icon,
  LoaderCircleIcon,
  Trash2Icon,
  UserRoundPlusIcon,
} from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
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
import { Badge } from "@/components/ui/badge";
import type {
  CaseAssignmentRoster,
  CaseExpertAssignment,
  ExpertProfile,
} from "@/types/squat-expert";
import { apiClientFetch } from "@/lib/api/client";

export function AssignmentForm({
  caseId,
  experts,
  roster,
}: {
  caseId: string;
  experts: ExpertProfile[];
  roster: CaseAssignmentRoster | null;
}) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string>();
  const [assigned, setAssigned] = useState<number>();
  const [selected, setSelected] = useState<string[]>([]);
  const locked = roster?.reference_status !== "open";
  const assignedIds = new Set(
    roster?.assignments.map((assignment) => assignment.evaluator_id) ?? [],
  );
  const availableSlots = 3 - assignedIds.size;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const evaluatorIds = selected;
    if (!evaluatorIds.length) {
      setError("Selecciona al menos un evaluador.");
      return;
    }
    setPending(true);
    setError(undefined);
    setAssigned(undefined);
    try {
      const result = await apiClientFetch<{ assigned: number }>(
        `/squat/cases/${encodeURIComponent(caseId)}/assignments`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ evaluator_ids: evaluatorIds }),
        },
      );
      setAssigned(result.assigned);
      setSelected([]);
      router.refresh();
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "No se pudieron crear las asignaciones.",
      );
    } finally {
      setPending(false);
    }
  }

  async function removeAssignment(assignmentId: string) {
    setPending(true);
    setError(undefined);
    try {
      await apiClientFetch(
        `/squat/cases/${encodeURIComponent(caseId)}/assignments/${assignmentId}`,
        { method: "DELETE" },
      );
      router.refresh();
    } catch (removalError) {
      setError(
        removalError instanceof Error
          ? removalError.message
          : "No se pudo retirar al evaluador.",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <form className="mt-7 space-y-5" onSubmit={handleSubmit}>
      {roster?.assignments.length ? (
        <div className="grid gap-3">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Evaluadores asignados ({roster.assignments.length}/3)
          </p>
          {roster.assignments.map((assignment) => (
            <AssignedExpert
              key={assignment.assignment_id}
              assignment={assignment}
              locked={locked}
              pending={pending}
              onRemove={() => removeAssignment(assignment.assignment_id)}
            />
          ))}
        </div>
      ) : null}

      <div className="grid gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          Disponibles
        </p>
        {experts.map((expert) => (
          <label
            key={expert.user_id}
            className="flex items-center gap-3 rounded-xl border bg-card p-4 transition-colors has-data-[selected=true]:border-primary/50 has-data-[selected=true]:bg-primary/5"
            data-selected={selected.includes(expert.user_id)}
          >
            <Checkbox
              checked={assignedIds.has(expert.user_id) || selected.includes(expert.user_id)}
              disabled={
                locked ||
                pending ||
                assignedIds.has(expert.user_id) ||
                (!selected.includes(expert.user_id) &&
                  selected.length >= availableSlots)
              }
              onCheckedChange={(checked) =>
                setSelected((current) =>
                  checked
                    ? [...current, expert.user_id]
                    : current.filter((id) => id !== expert.user_id),
                )
              }
            />
            <span className="grid size-9 place-items-center rounded-full bg-secondary">
              <UserRoundPlusIcon className="size-4" aria-hidden="true" />
            </span>
            <span>
              <span className="block text-sm font-medium">
                {expert.display_name ?? expert.email ?? "Evaluador"}
              </span>
              <span className="block text-xs text-muted-foreground">
                {assignedIds.has(expert.user_id) ? "Ya asignado" : expert.email}
              </span>
            </span>
          </label>
        ))}
      </div>

      {error ? (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}
      {assigned !== undefined ? (
        <Alert>
          <CheckCircle2Icon aria-hidden="true" />
          <AlertDescription>
            {assigned
              ? `${assigned} asignación(es) creada(s).`
              : "Los evaluadores seleccionados ya tenían este caso asignado."}
          </AlertDescription>
        </Alert>
      ) : null}

      <Button
        type="submit"
        disabled={pending || locked || !selected.length || availableSlots <= 0}
      >
        {pending ? (
          <LoaderCircleIcon className="animate-spin" aria-hidden="true" />
        ) : (
          <UserRoundPlusIcon aria-hidden="true" />
        )}
        {pending ? "Asignando..." : "Asignar caso"}
      </Button>
    </form>
  );
}

function AssignedExpert({
  assignment,
  locked,
  pending,
  onRemove,
}: {
  assignment: CaseExpertAssignment;
  locked: boolean;
  pending: boolean;
  onRemove: () => void;
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl border bg-muted/25 p-4">
      <span className="grid size-9 place-items-center rounded-full bg-secondary">
        <UserRoundPlusIcon className="size-4" aria-hidden="true" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-medium">
          {assignment.display_name ?? assignment.email ?? "Evaluador"}
        </span>
        <span className="block text-xs text-muted-foreground">
          {assignment.email}
        </span>
      </span>
      <Badge variant="outline">
        {assignment.status === "submitted"
          ? "Enviada"
          : assignment.status === "in_progress"
            ? "En progreso"
            : "Pendiente"}
      </Badge>
      <AlertDialog>
        <AlertDialogTrigger
          render={
            <Button
              type="button"
              size="icon-sm"
              variant="ghost"
              disabled={locked || pending}
              aria-label="Retirar evaluador"
            />
          }
        >
          <Trash2Icon aria-hidden="true" />
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Retirar a este evaluador?</AlertDialogTitle>
            <AlertDialogDescription>
              {assignment.has_response
                ? "Su borrador o respuesta enviada se eliminará y las métricas del caso podrán cambiar."
                : "La asignación se eliminará. El evaluador dejará de ver este caso."}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={onRemove}>
              Retirar evaluador
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
