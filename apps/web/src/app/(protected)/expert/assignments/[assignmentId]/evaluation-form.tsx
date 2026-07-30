"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  useForm,
  useWatch,
  type UseFormRegister,
} from "react-hook-form";
import { z } from "zod";
import {
  CheckCircle2Icon,
  CircleAlertIcon,
  LoaderCircleIcon,
  SaveIcon,
  SendIcon,
} from "lucide-react";

import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
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

import { ExpertReviewPlayer } from "./expert-review-player";

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

export type EvaluationValues = z.infer<typeof evaluationSchema>;
type EvaluationChoice = z.infer<typeof choiceSchema>;
type EvaluationStatus = "draft" | "submitted";
export type MissingClassification = {
  path: string;
  repetitionIndex: number;
  label: string;
};

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
  shortTitle: string;
  title: string;
  description: string;
  options: Array<[EvaluationChoice, string]>;
}> = [
  {
    field: "trunk",
    key: "trunk_lateral_inclination",
    shortTitle: "Tronco",
    title: "Inclinación lateral del tronco",
    description: "Desviación lateral observable durante la ejecución.",
    options: directionalOptions(),
  },
  {
    field: "pelvis",
    key: "pelvis_lateral_shift",
    shortTitle: "Pelvis",
    title: "Desplazamiento lateral de pelvis",
    description: "Traslación visible de la pelvis hacia un lado.",
    options: directionalOptions(),
  },
  {
    field: "valgus",
    key: "visible_dynamic_valgus",
    shortTitle: "Valgo",
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
    shortTitle: "Asimetría",
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
  activeRepetition,
  onRepetitionFocus,
}: {
  assignment: ExpertAssignment;
  activeRepetition?: number | null;
  onRepetitionFocus?: (repetitionIndex: number) => void;
}) {
  const router = useRouter();
  const locked = assignment.status === "submitted";
  const [pending, setPending] = useState<EvaluationStatus>();
  const [message, setMessage] = useState<string>();
  const [validationRequested, setValidationRequested] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const {
    control,
    formState: { errors },
    getValues,
    handleSubmit,
    register,
    setError,
  } = useForm<EvaluationValues>({
    resolver: zodResolver(evaluationSchema),
    mode: "onSubmit",
    reValidateMode: "onBlur",
    defaultValues: defaultsFromAssignment(assignment),
  });
  const watchedRepetitions = useWatch({
    control,
    name: "repetitions",
  });
  const missingClassifications = validationRequested
    ? findMissingClassifications(watchedRepetitions ?? [])
    : [];
  const missingPaths = new Set(
    missingClassifications.map((item) => item.path),
  );

  function revealMissing(item: MissingClassification) {
    onRepetitionFocus?.(item.repetitionIndex);
    requestAnimationFrame(() => {
      const field = document.getElementById(item.path);
      field?.scrollIntoView?.({
        behavior: "smooth",
        block: "center",
        inline: "center",
      });
      field?.focus({ preventScroll: true });
    });
  }

  function requestSubmission() {
    const missing = findMissingClassifications(getValues("repetitions"));
    setValidationRequested(true);
    setMessage(undefined);
    if (missing.length > 0) {
      revealMissing(missing[0]);
      return;
    }
    setConfirmOpen(true);
  }

  function save(status: EvaluationStatus) {
    return handleSubmit(async (values) => {
      const items = buildEvaluationItems(values);
      const missing = findMissingClassifications(values.repetitions);
      if (status === "submitted" && missing.length > 0) {
        setValidationRequested(true);
        setConfirmOpen(false);
        revealMissing(missing[0]);
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
        if (status === "submitted") {
          toast.success("Respuestas enviadas correctamente.");
          router.replace("/expert/assignments");
          return;
        }
        setMessage("Borrador guardado.");
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
            data-repetition-index={repetitionIndex}
            className="space-y-4 rounded-2xl border border-primary/20 bg-primary/[0.025] p-4"
            onFocusCapture={() => onRepetitionFocus?.(repetitionIndex)}
          >
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.16em] text-primary">
                {assignment.case_id}-repeticion-{repetitionIndex}
              </p>
              <h3 className="mt-1 text-lg font-semibold">
                Repetición {repetitionIndex}
              </h3>
              <Button
                type="button"
                size="sm"
                variant="ghost"
                className="-ml-3 mt-2 hidden lg:inline-flex"
                onClick={() => onRepetitionFocus?.(repetitionIndex)}
              >
                Ver fragmento de esta repetición
              </Button>
            </div>
            <div className="lg:hidden">
              <ExpertReviewPlayer
                assignmentId={assignment.assignment_id}
                repetitions={(assignment.repetitions ?? []).filter(
                  (repetition) =>
                    repetition.repetition_index === repetitionIndex,
                )}
                activeRepetition={repetitionIndex}
                autoPlaySelected={activeRepetition === repetitionIndex}
                loopSelectedRepetition
                lockNavigationToActive
                showRepetitionNavigation={false}
                showFullVideoOption={false}
              />
            </div>
            <PatternCarousel
              locked={locked}
              missingPaths={missingPaths}
              register={register}
              repetitionIndex={repetitionIndex}
              repetitionPosition={repetitionPosition}
            />
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
      {validationRequested && missingClassifications.length > 0 ? (
        <Alert variant="destructive">
          <CircleAlertIcon aria-hidden="true" />
          <AlertTitle>
            Faltan {missingClassifications.length} clasificaciones
          </AlertTitle>
          <AlertDescription>
            <p>
              Completa los siguientes patrones antes de enviar la evaluación:
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {missingClassifications.map((item) => (
                <Button
                  key={item.path}
                  type="button"
                  size="sm"
                  variant="outline"
                  className="border-destructive/40 bg-background"
                  onClick={() => revealMissing(item)}
                >
                  Repetición {item.repetitionIndex} · {item.label}
                </Button>
              ))}
            </div>
          </AlertDescription>
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
            onClick={requestSubmission}
          >
            {pending === "submitted" ? (
              <LoaderCircleIcon
                className="animate-spin"
                aria-hidden="true"
              />
            ) : (
              <SendIcon aria-hidden="true" />
            )}
            Enviar evaluación
          </Button>
          <AlertDialog open={confirmOpen} onOpenChange={setConfirmOpen}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>
                  ¿Enviar la evaluación definitivamente?
                </AlertDialogTitle>
                <AlertDialogDescription>
                  Revisa tus clasificaciones antes de continuar. Una vez
                  enviada, la evaluación quedará bloqueada y no podrás
                  modificar sus respuestas.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Volver a revisar</AlertDialogCancel>
                <AlertDialogAction onClick={save("submitted")}>
                  Enviar definitivamente
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      )}
    </form>
  );
}

function PatternCarousel({
  locked,
  missingPaths,
  register,
  repetitionIndex,
  repetitionPosition,
}: {
  locked: boolean;
  missingPaths: Set<string>;
  register: UseFormRegister<EvaluationValues>;
  repetitionIndex: number;
  repetitionPosition: number;
}) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [activePattern, setActivePattern] = useState(0);

  function goToPattern(index: number) {
    const track = trackRef.current;
    if (!track) return;
    track.scrollTo({
      left: index * track.clientWidth,
      behavior: "smooth",
    });
    setActivePattern(index);
  }

  function updateActivePattern() {
    const track = trackRef.current;
    if (!track?.clientWidth) return;
    setActivePattern(
      Math.min(
        patternDefinitions.length - 1,
        Math.max(0, Math.round(track.scrollLeft / track.clientWidth)),
      ),
    );
  }

  return (
    <div className="min-w-0 space-y-3">
      <div
        className="flex gap-2 overflow-x-auto pb-1 lg:hidden"
        aria-label={`Variables de la repetición ${repetitionIndex}`}
      >
        {patternDefinitions.map((pattern, index) => (
          <Button
            key={pattern.key}
            type="button"
            size="sm"
            variant={activePattern === index ? "default" : "outline"}
            className="shrink-0"
            aria-pressed={activePattern === index}
            onClick={() => goToPattern(index)}
          >
            {pattern.shortTitle}
          </Button>
        ))}
      </div>
      <div
        ref={trackRef}
        className="-mx-1 flex snap-x snap-mandatory gap-3 overflow-x-auto px-1 pb-2 lg:mx-0 lg:grid lg:snap-none lg:overflow-visible lg:px-0 lg:pb-0"
        onScroll={updateActivePattern}
      >
        {patternDefinitions.map((pattern) => {
          const fieldBase =
            `repetitions.${repetitionPosition}.${pattern.field}` as const;
          const classificationPath = `${fieldBase}.choice`;
          const isMissing = missingPaths.has(classificationPath);
          return (
            <div
              key={`${repetitionIndex}-${pattern.key}`}
              data-classification-path={classificationPath}
              className="w-full shrink-0 snap-start lg:w-auto"
            >
              <Card
                className={
                  isMissing
                    ? "h-full border-destructive ring-1 ring-destructive/20"
                    : "h-full"
                }
              >
                <CardHeader>
                  <CardTitle className="text-base">{pattern.title}</CardTitle>
                  <CardDescription>{pattern.description}</CardDescription>
                  {isMissing ? (
                    <p className="text-xs font-medium text-destructive">
                      Clasificación pendiente
                    </p>
                  ) : null}
                </CardHeader>
                <CardContent className="grid gap-4 md:grid-cols-[1fr_0.55fr]">
                  <Field>
                    <FieldLabel htmlFor={`${fieldBase}.choice`}>
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
                    <FieldLabel htmlFor={`${fieldBase}.confidence`}>
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
                    <FieldLabel htmlFor={`${fieldBase}.observation`}>
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
            </div>
          );
        })}
      </div>
    </div>
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
  const indexes = (assignment.repetitions ?? []).map(
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

export function findMissingClassifications(
  repetitions: EvaluationValues["repetitions"],
): MissingClassification[] {
  return repetitions.flatMap((repetition, repetitionPosition) =>
    patternDefinitions.flatMap((pattern) =>
      repetition[pattern.field].choice
        ? []
        : [
            {
              path:
                `repetitions.${repetitionPosition}.${pattern.field}.choice`,
              repetitionIndex: repetition.repetitionIndex,
              label: pattern.title,
            },
          ],
    ),
  );
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
