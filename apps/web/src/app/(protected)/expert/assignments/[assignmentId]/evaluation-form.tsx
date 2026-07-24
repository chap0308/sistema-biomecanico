"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  CheckCircle2Icon,
  LoaderCircleIcon,
  SaveIcon,
  SendIcon,
} from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Field, FieldLabel } from "@/components/ui/field";
import { apiClientFetch } from "@/lib/api/client";
import type {
  ExpertAssignment,
  ExpertEvaluationItem,
  ExpertObservedSide,
  ExpertPatternKey,
} from "@/types/squat-expert";

const choiceSchema = z.enum([
  "",
  "ausente",
  "presente_izquierda",
  "presente_derecha",
  "presente_bilateral",
  "presente_sin_direccion",
  "no_concluyente",
]);

const evaluationSchema = z.object({
  trunk: choiceSchema,
  trunkConfidence: z.enum(["baja", "media", "alta"]),
  trunkObservation: z.string().max(500),
  pelvis: choiceSchema,
  pelvisConfidence: z.enum(["baja", "media", "alta"]),
  pelvisObservation: z.string().max(500),
  valgus: choiceSchema,
  valgusConfidence: z.enum(["baja", "media", "alta"]),
  valgusObservation: z.string().max(500),
  asymmetry: choiceSchema,
  asymmetryConfidence: z.enum(["baja", "media", "alta"]),
  asymmetryObservation: z.string().max(500),
  generalObservation: z.string().max(1000),
});

type EvaluationValues = z.infer<typeof evaluationSchema>;
type EvaluationStatus = "draft" | "submitted";

const selectClassName =
  "h-9 w-full rounded-lg border border-input bg-background px-2.5 text-sm " +
  "outline-none focus-visible:border-ring focus-visible:ring-3 " +
  "focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-60";
const textareaClassName =
  "min-h-20 w-full resize-y rounded-lg border border-input bg-background " +
  "px-3 py-2 text-sm outline-none focus-visible:border-ring " +
  "focus-visible:ring-3 focus-visible:ring-ring/50 disabled:opacity-60";

const patternDefinitions: Array<{
  field: "trunk" | "pelvis" | "valgus" | "asymmetry";
  confidenceField:
    | "trunkConfidence"
    | "pelvisConfidence"
    | "valgusConfidence"
    | "asymmetryConfidence";
  observationField:
    | "trunkObservation"
    | "pelvisObservation"
    | "valgusObservation"
    | "asymmetryObservation";
  key: ExpertPatternKey;
  title: string;
  description: string;
  options: Array<[EvaluationValues["trunk"], string]>;
}> = [
  {
    field: "trunk",
    confidenceField: "trunkConfidence",
    observationField: "trunkObservation",
    key: "trunk_lateral_inclination",
    title: "Inclinación lateral del tronco",
    description: "Desviación lateral observable durante la ejecución.",
    options: directionalOptions(),
  },
  {
    field: "pelvis",
    confidenceField: "pelvisConfidence",
    observationField: "pelvisObservation",
    key: "pelvis_lateral_shift",
    title: "Desplazamiento lateral de pelvis",
    description: "Traslación visible de la pelvis hacia un lado.",
    options: directionalOptions(),
  },
  {
    field: "valgus",
    confidenceField: "valgusConfidence",
    observationField: "valgusObservation",
    key: "visible_dynamic_valgus",
    title: "Valgo dinámico visible",
    description: "Desplazamiento medial observable de una o ambas rodillas.",
    options: [
      ["", "Seleccionar"],
      ["ausente", "Ausente"],
      ["presente_izquierda", "Presente en rodilla izquierda"],
      ["presente_derecha", "Presente en rodilla derecha"],
      ["presente_bilateral", "Presente bilateral"],
      ["no_concluyente", "No concluyente"],
    ],
  },
  {
    field: "asymmetry",
    confidenceField: "asymmetryConfidence",
    observationField: "asymmetryObservation",
    key: "bilateral_asymmetry",
    title: "Asimetría bilateral observable",
    description: "Diferencia visible entre los lados durante el movimiento.",
    options: [
      ["", "Seleccionar"],
      ["ausente", "Ausente"],
      ["presente_izquierda", "Presente, predominio izquierdo"],
      ["presente_derecha", "Presente, predominio derecho"],
      ["presente_sin_direccion", "Presente, sin predominio claro"],
      ["no_concluyente", "No concluyente"],
    ],
  },
];

export function EvaluationForm({
  assignment,
}: {
  assignment: ExpertAssignment;
}) {
  const router = useRouter();
  const locked = assignment.status === "submitted";
  const [pending, setPending] = useState<EvaluationStatus>();
  const [message, setMessage] = useState<string>();
  const {
    formState: { errors },
    handleSubmit,
    register,
    setError,
  } = useForm<EvaluationValues>({
    resolver: zodResolver(evaluationSchema),
    mode: "onSubmit",
    reValidateMode: "onBlur",
    defaultValues: defaultsFromAssignment(assignment),
  });

  function save(status: EvaluationStatus) {
    return handleSubmit(async (values) => {
      const items = buildEvaluationItems(values);
      if (status === "submitted" && items.length !== 4) {
        setError("root", {
          message: "Clasifica los cuatro patrones antes de enviar.",
        });
        return;
      }
      setPending(status);
      setMessage(undefined);
      try {
        await apiClientFetch(
          `/squat/expert/assignments/${encodeURIComponent(assignment.assignment_id)}/evaluation`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              status,
              general_observation: values.generalObservation || null,
              items,
            }),
          },
        );
        setMessage(
          status === "submitted"
            ? "Evaluación enviada y bloqueada correctamente."
            : "Borrador guardado.",
        );
        router.refresh();
      } catch (submissionError) {
        setError("root", {
          message:
            submissionError instanceof Error
              ? submissionError.message
              : "No se pudo guardar la evaluación.",
        });
      } finally {
        setPending(undefined);
      }
    });
  }

  return (
    <form className="space-y-4">
      {patternDefinitions.map((pattern) => (
        <Card key={pattern.key}>
          <CardHeader>
            <CardTitle className="text-base">{pattern.title}</CardTitle>
            <CardDescription>{pattern.description}</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-[1fr_0.55fr]">
            <Field>
              <FieldLabel htmlFor={pattern.field}>Clasificación</FieldLabel>
              <select
                id={pattern.field}
                className={selectClassName}
                disabled={locked}
                {...register(pattern.field)}
              >
                {pattern.options.map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </Field>
            <Field>
              <FieldLabel htmlFor={pattern.confidenceField}>
                Confianza
              </FieldLabel>
              <select
                id={pattern.confidenceField}
                className={selectClassName}
                disabled={locked}
                {...register(pattern.confidenceField)}
              >
                <option value="alta">Alta</option>
                <option value="media">Media</option>
                <option value="baja">Baja</option>
              </select>
            </Field>
            <Field className="md:col-span-2">
              <FieldLabel htmlFor={pattern.observationField}>
                Observación opcional
              </FieldLabel>
              <textarea
                id={pattern.observationField}
                className={textareaClassName}
                disabled={locked}
                {...register(pattern.observationField)}
              />
            </Field>
          </CardContent>
        </Card>
      ))}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Observación general</CardTitle>
          <CardDescription>
            Registra dificultades de visibilidad o criterios relevantes.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <textarea
            className={textareaClassName}
            disabled={locked}
            {...register("generalObservation")}
          />
        </CardContent>
      </Card>

      {errors.root?.message ? (
        <Alert variant="destructive">
          <AlertDescription>{errors.root.message}</AlertDescription>
        </Alert>
      ) : null}
      {message ? (
        <Alert>
          <CheckCircle2Icon aria-hidden="true" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      ) : null}

      {locked ? (
        <Alert>
          <CheckCircle2Icon aria-hidden="true" />
          <AlertDescription>
            Esta evaluación fue enviada y ya no puede modificarse.
          </AlertDescription>
        </Alert>
      ) : (
        <div className="flex flex-wrap justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            disabled={Boolean(pending)}
            onClick={save("draft")}
          >
            {pending === "draft" ? (
              <LoaderCircleIcon className="animate-spin" aria-hidden="true" />
            ) : (
              <SaveIcon aria-hidden="true" />
            )}
            Guardar borrador
          </Button>
          <Button
            type="button"
            disabled={Boolean(pending)}
            onClick={save("submitted")}
          >
            {pending === "submitted" ? (
              <LoaderCircleIcon className="animate-spin" aria-hidden="true" />
            ) : (
              <SendIcon aria-hidden="true" />
            )}
            Enviar evaluación
          </Button>
        </div>
      )}
    </form>
  );
}

function directionalOptions(): Array<[EvaluationValues["trunk"], string]> {
  return [
    ["", "Seleccionar"],
    ["ausente", "Ausente"],
    ["presente_izquierda", "Presente hacia la izquierda"],
    ["presente_derecha", "Presente hacia la derecha"],
    ["no_concluyente", "No concluyente"],
  ];
}

function defaultsFromAssignment(
  assignment: ExpertAssignment,
): EvaluationValues {
  const items = new Map(
    (assignment.evaluation?.items ?? []).map((item) => [
      item.pattern_key,
      item,
    ]),
  );
  return {
    trunk: choiceFromItem(items.get("trunk_lateral_inclination")),
    trunkConfidence:
      items.get("trunk_lateral_inclination")?.confidence ?? "media",
    trunkObservation:
      items.get("trunk_lateral_inclination")?.observation ?? "",
    pelvis: choiceFromItem(items.get("pelvis_lateral_shift")),
    pelvisConfidence: items.get("pelvis_lateral_shift")?.confidence ?? "media",
    pelvisObservation:
      items.get("pelvis_lateral_shift")?.observation ?? "",
    valgus: choiceFromItem(items.get("visible_dynamic_valgus")),
    valgusConfidence:
      items.get("visible_dynamic_valgus")?.confidence ?? "media",
    valgusObservation:
      items.get("visible_dynamic_valgus")?.observation ?? "",
    asymmetry: choiceFromItem(items.get("bilateral_asymmetry")),
    asymmetryConfidence:
      items.get("bilateral_asymmetry")?.confidence ?? "media",
    asymmetryObservation:
      items.get("bilateral_asymmetry")?.observation ?? "",
    generalObservation: assignment.evaluation?.general_observation ?? "",
  };
}

function choiceFromItem(
  item?: ExpertEvaluationItem,
): EvaluationValues["trunk"] {
  if (!item) return "";
  if (item.classification !== "presente") return item.classification;
  return `presente_${item.observed_side ?? "sin_direccion"}` as EvaluationValues["trunk"];
}

export function buildEvaluationItems(
  values: EvaluationValues,
): ExpertEvaluationItem[] {
  return patternDefinitions.flatMap((pattern) => {
    const choice = values[pattern.field];
    if (!choice) return [];
    const isPresent = choice.startsWith("presente_");
    return [
      {
        pattern_key: pattern.key,
        classification: isPresent
          ? "presente"
          : (choice as ExpertEvaluationItem["classification"]),
        observed_side: isPresent
          ? (choice.slice("presente_".length) as ExpertObservedSide)
          : null,
        confidence: values[pattern.confidenceField],
        observation: values[pattern.observationField] || null,
      },
    ];
  });
}
