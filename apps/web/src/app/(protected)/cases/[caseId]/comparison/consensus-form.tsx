"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2Icon, LoaderCircleIcon } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Field, FieldLabel } from "@/components/ui/field";
import { apiClientFetch } from "@/lib/api/client";
import type { ExpertPatternKey } from "@/types/squat-expert";
import type {
  CaseComparison,
  FinalReference,
} from "@/types/squat-comparison";

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
  repetitionIndex,
  currentReference,
  onSaved,
}: {
  caseId: string;
  patternKey: ExpertPatternKey;
  repetitionIndex: number;
  currentReference?: FinalReference | null;
  onSaved?: (comparison: CaseComparison) => void;
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
    if (!choice) {
      setError("Selecciona una referencia final.");
      return;
    }
    const present = choice.startsWith("presente_");
    setPending(true);
    setError(undefined);
    setSaved(false);
    try {
      const comparison = await apiClientFetch<CaseComparison>(
        `/squat/cases/${encodeURIComponent(caseId)}/comparison/references/${repetitionIndex}/${patternKey}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            classification: present ? "presente" : choice,
            observed_side: present
              ? choice.slice("presente_".length)
              : null,
            observation: observation || null,
          }),
        },
      );
      setSaved(true);
      onSaved?.(comparison);
      router.refresh();
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "No se pudo guardar la referencia final.",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <form className="mt-4 grid gap-3" onSubmit={submit}>
      <Field>
        <FieldLabel htmlFor={`reference-${repetitionIndex}-${patternKey}`}>
          Referencia final
        </FieldLabel>
        <select
          id={`reference-${repetitionIndex}-${patternKey}`}
          name="reference"
          className={selectClassName}
          defaultValue={referenceValue(currentReference)}
        >
          <option value="" disabled>
            Seleccionar
          </option>
          <option value="ausente">Ausente</option>
          {referenceOptions(patternKey).map(([value, optionLabel]) => (
            <option key={value} value={value}>
              {optionLabel}
            </option>
          ))}
          <option value="no_concluyente">No concluyente</option>
        </select>
      </Field>
      <Field>
        <FieldLabel htmlFor={`observation-${repetitionIndex}-${patternKey}`}>
          Documentación de la referencia (opcional)
        </FieldLabel>
        <textarea
          id={`observation-${repetitionIndex}-${patternKey}`}
          name="observation"
          className={textareaClassName}
          defaultValue={currentReference?.observation ?? ""}
          placeholder="Añade una nota solo si ayuda a explicar la decisión."
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
          <AlertDescription>Referencia guardada.</AlertDescription>
        </Alert>
      ) : null}
      <Button type="submit" size="sm" disabled={pending}>
        {pending ? (
          <LoaderCircleIcon className="animate-spin" aria-hidden="true" />
        ) : null}
        {currentReference ? "Guardar cambios" : "Registrar referencia"}
      </Button>
    </form>
  );
}

function referenceValue(reference?: FinalReference | null) {
  if (!reference) return "";
  return reference.classification === "presente" && reference.observed_side
    ? `presente_${reference.observed_side}`
    : reference.classification;
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
