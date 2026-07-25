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

const patternResponseSchema = z.object({
  choice: choiceSchema,
  confidence: z.enum(["baja", "media", "alta"]),
  observation: z.string().max(500),
});

const repetitionEvaluationSchema = z.object({
  repetitionIndex: z.number().int().positive(),
  trunk: patternResponseSchema,
  pelvis: patternResponseSchema,
  valgus: patternResponseSchema,
  asymmetry: patternResponseSchema,
});

const evaluationSchema = z.object({
  repetitions: z.array(repetitionEvaluationSchema).min(1),
  generalObservation: z.string().max(1000),
});

type EvaluationValues = z.infer<typeof evaluationSchema>;
type EvaluationChoice = z.infer<typeof choiceSchema>;
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
  key: ExpertPatternKey;
  title: string;
  description: string;
  options: Array<[EvaluationChoice, string]>;
}> = [
  {
    field: "trunk",
    key: "trunk_lateral_inclination",
    title: "Inclinación lateral del tronco",
    description: "Desviación lateral observable durante la ejecución.",
    options: directionalOptions(),
  },
  {
    field: "pelvis",
    key: "pelvis_lateral_shift",
    title: "Desplazamiento lateral de pelvis",
    description: "Traslación visible de la pelvis hacia un lado.",
    options: directionalOptions(),
  },
  {
    field: "valgus",
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
      if (
        status === "submitted" &&
        items.length !== values.repetitions.length * 4
      ) {
        setError("root", {
          message:
            "Clasifica los cuatro patrones de cada repetición antes de enviar.",
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
      {defaultRepetitionIndexes(assignment).map(
        (repetitionIndex, repetitionPosition) => (
          <section
            key={repetitionIndex}
            className="space-y-4 rounded-2xl border border-primary/20 bg-primary/[0.025] p-4"
          >
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.16em] text-primary">
                {assignment.case_id}-repeticion-{repetitionIndex}
              </p>
              <h3 className="mt-1 text-lg font-semibold">
                Repetición {repetitionIndex}
              </h3>
            </div>
            {patternDefinitions.map((pattern) => {
              const fieldBase =
                `repetitions.${repetitionPosition}.${pattern.field}` as const;
              return (
                <Card key={`${repetitionIndex}-${pattern.key}`}>
                  <CardHeader>
                    <CardTitle className="text-base">{pattern.title}</CardTitle>
                    <CardDescription>{pattern.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="grid gap-4 md:grid-cols-[1fr_0.55fr]">
                    <Field>
                      <FieldLabel
                        htmlFor={`${fieldBase}.choice`}
                      >
                        Clasificación
                      </FieldLabel>
                      <select
                        id={`${fieldBase}.choice`}
                        className={selectClassName}
                        disabled={locked}
                        {...register(`${fieldBase}.choice`)}
                      >
                        {pattern.options.map(([value, label]) => (
                          <option key={value} value={value}>
                            {label}
                          </option>
                        ))}
                      </select>
                    </Field>
                    <Field>
                      <FieldLabel
                        htmlFor={`${fieldBase}.confidence`}
                      >
                        Confianza
                      </FieldLabel>
                      <select
                        id={`${fieldBase}.confidence`}
                        className={selectClassName}
                        disabled={locked}
                        {...register(`${fieldBase}.confidence`)}
                      >
                        <option value="alta">Alta</option>
                        <option value="media">Media</option>
                        <option value="baja">Baja</option>
                      </select>
                    </Field>
                    <Field className="md:col-span-2">
                      <FieldLabel
                        htmlFor={`${fieldBase}.observation`}
                      >
                        Observación opcional
                      </FieldLabel>
                      <textarea
                        id={`${fieldBase}.observation`}
                        className={textareaClassName}
                        disabled={locked}
                        {...register(`${fieldBase}.observation`)}
                      />
                    </Field>
                  </CardContent>
                </Card>
              );
            })}
          </section>
        ),
      )}

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

function directionalOptions(): Array<[EvaluationChoice, string]> {
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
      `${item.repetition_index}:${item.pattern_key}`,
      item,
    ]),
  );
  return {
    repetitions: defaultRepetitionIndexes(assignment).map(
      (repetitionIndex) => ({
        repetitionIndex,
        trunk: responseDefaults(
          items.get(`${repetitionIndex}:trunk_lateral_inclination`),
        ),
        pelvis: responseDefaults(
          items.get(`${repetitionIndex}:pelvis_lateral_shift`),
        ),
        valgus: responseDefaults(
          items.get(`${repetitionIndex}:visible_dynamic_valgus`),
        ),
        asymmetry: responseDefaults(
          items.get(`${repetitionIndex}:bilateral_asymmetry`),
        ),
      }),
    ),
    generalObservation: assignment.evaluation?.general_observation ?? "",
  };
}

function defaultRepetitionIndexes(assignment: ExpertAssignment): number[] {
  const indexes = assignment.repetitions.map(
    (repetition) => repetition.repetition_index,
  );
  return indexes.length ? indexes : [1];
}

function responseDefaults(item?: ExpertEvaluationItem) {
  return {
    choice: choiceFromItem(item),
    confidence: item?.confidence ?? ("media" as const),
    observation: item?.observation ?? "",
  };
}

function choiceFromItem(
  item?: ExpertEvaluationItem,
): EvaluationChoice {
  if (!item) return "";
  if (item.classification !== "presente") return item.classification;
  return `presente_${item.observed_side ?? "sin_direccion"}` as EvaluationChoice;
}

export function buildEvaluationItems(
  values: EvaluationValues,
): ExpertEvaluationItem[] {
  return values.repetitions.flatMap((repetition) =>
    patternDefinitions.flatMap((pattern) => {
      const response = repetition[pattern.field];
      const choice = response.choice;
      if (!choice) return [];
      const isPresent = choice.startsWith("presente_");
      return [
        {
          repetition_index: repetition.repetitionIndex,
          pattern_key: pattern.key,
          classification: isPresent
            ? "presente"
            : (choice as ExpertEvaluationItem["classification"]),
          observed_side: isPresent
            ? (choice.slice("presente_".length) as ExpertObservedSide)
            : null,
          confidence: response.confidence,
          observation: response.observation || null,
        },
      ];
    }),
  );
}
