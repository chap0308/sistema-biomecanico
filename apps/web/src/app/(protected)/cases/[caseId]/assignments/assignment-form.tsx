"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2Icon, LoaderCircleIcon, UserRoundPlusIcon } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import type { ExpertProfile } from "@/types/squat-expert";
import { apiClientFetch } from "@/lib/api/client";

export function AssignmentForm({
  caseId,
  experts,
}: {
  caseId: string;
  experts: ExpertProfile[];
}) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string>();
  const [assigned, setAssigned] = useState<number>();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const evaluatorIds = data.getAll("evaluator_id").map(String);
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

  return (
    <form className="mt-7 space-y-5" onSubmit={handleSubmit}>
      <div className="grid gap-3">
        {experts.map((expert) => (
          <label
            key={expert.user_id}
            className="flex cursor-pointer items-center gap-3 rounded-xl border bg-card p-4 transition-colors has-checked:border-primary/50 has-checked:bg-primary/5"
          >
            <input
              type="checkbox"
              name="evaluator_id"
              value={expert.user_id}
              className="size-4 accent-primary"
            />
            <span className="grid size-9 place-items-center rounded-full bg-secondary">
              <UserRoundPlusIcon className="size-4" aria-hidden="true" />
            </span>
            <span>
              <span className="block text-sm font-medium">
                {expert.display_name ?? expert.email ?? "Evaluador"}
              </span>
              <span className="block text-xs text-muted-foreground">
                {expert.email}
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

      <Button type="submit" disabled={pending || !experts.length}>
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
