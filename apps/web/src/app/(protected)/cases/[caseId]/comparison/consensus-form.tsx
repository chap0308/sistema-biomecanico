"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2Icon, LoaderCircleIcon } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Field, FieldLabel } from "@/components/ui/field";
import { apiClientFetch } from "@/lib/api/client";
import type { ExpertPatternKey } from "@/types/squat-expert";

const selectClassName =
  "h-9 w-full rounded-lg border border-input bg-background px-2.5 text-sm " +
  "outline-none focus-visible:border-ring focus-visible:ring-3 " +
  "focus-visible:ring-ring/50";
const textareaClassName =
  "min-h-20 w-full resize-y rounded-lg border border-input bg-background " +
  "px-3 py-2 text-sm outline-none focus-visible:border-ring " +
  "focus-visible:ring-3 focus-visible:ring-ring/50";

export function ConsensusForm({
  caseId,
  patternKey,
}: {
  caseId: string;
  patternKey: ExpertPatternKey;
}) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string>();
  const [saved, setSaved] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const choice = String(data.get("reference") ?? "");
    const observation = String(data.get("observation") ?? "").trim();
    if (!choice || observation.length < 3) {
      setError("Selecciona una referencia y documenta el consenso.");
      return;
    }
    const present = choice.startsWith("presente_");
    setPending(true);
    setError(undefined);
    setSaved(false);
    try {
      await apiClientFetch(
        `/squat/cases/${encodeURIComponent(caseId)}/comparison/references/${patternKey}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            classification: present ? "presente" : choice,
            observed_side: present
              ? choice.slice("presente_".length)
              : null,
            observation,
          }),
        },
      );
      setSaved(true);
      router.refresh();
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "No se pudo registrar el consenso.",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <form className="mt-4 grid gap-3" onSubmit={submit}>
      <Field>
        <FieldLabel htmlFor={`reference-${patternKey}`}>
          Referencia acordada
        </FieldLabel>
        <select
          id={`reference-${patternKey}`}
          name="reference"
          className={selectClassName}
          defaultValue=""
        >
          <option value="" disabled>
            Seleccionar
          </option>
          <option value="ausente">Ausente</option>
          {referenceOptions(patternKey).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
          <option value="no_concluyente">No concluyente</option>
        </select>
      </Field>
      <Field>
        <FieldLabel htmlFor={`observation-${patternKey}`}>
          Sustento del consenso
        </FieldLabel>
        <textarea
          id={`observation-${patternKey}`}
          name="observation"
          className={textareaClassName}
          placeholder="Describe brevemente la revisión conjunta y el criterio acordado."
        />
      </Field>
      {error ? (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}
      {saved ? (
        <Alert>
          <CheckCircle2Icon aria-hidden="true" />
          <AlertDescription>Consenso registrado.</AlertDescription>
        </Alert>
      ) : null}
      <Button type="submit" size="sm" disabled={pending}>
        {pending ? (
          <LoaderCircleIcon className="animate-spin" aria-hidden="true" />
        ) : null}
        Registrar consenso
      </Button>
    </form>
  );
}

function referenceOptions(
  patternKey: ExpertPatternKey,
): Array<[string, string]> {
  if (patternKey === "bilateral_asymmetry") {
    return [["presente_sin_direccion", "Presente"]];
  }
  const directional: Array<[string, string]> = [
    ["presente_izquierda", "Presente, izquierda"],
    ["presente_derecha", "Presente, derecha"],
  ];
  return patternKey === "visible_dynamic_valgus"
    ? [...directional, ["presente_bilateral", "Presente, bilateral"]]
    : directional;
}
