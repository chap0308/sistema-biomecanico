"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import {
  FileVideoIcon,
  FlaskConicalIcon,
  LoaderCircleIcon,
  UploadCloudIcon,
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
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { getApiBaseUrl } from "@/lib/api/config";
import { createClient } from "@/lib/supabase/client";

const selectClassName =
  "h-8 w-full rounded-lg border border-input bg-background px-2.5 text-sm " +
  "outline-none focus-visible:border-ring focus-visible:ring-3 " +
  "focus-visible:ring-ring/50";

export function NewCaseForm() {
  const router = useRouter();
  const formRef = useRef<HTMLFormElement>(null);
  const [videoSelection, setVideoSelection] = useState<{
    file: File;
    previewUrl: string;
  }>();
  const video = videoSelection?.file;
  const previewUrl = videoSelection?.previewUrl;
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string>();
  const development =
    process.env.NODE_ENV === "development" ||
    process.env.NEXT_PUBLIC_ENABLE_DEV_FIXTURES === "1";
  const dropzone = useDropzone({
    accept: {
      "video/mp4": [".mp4"],
      "video/quicktime": [".mov"],
      "video/webm": [".webm"],
      "video/x-msvideo": [".avi"],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024,
    onDropAccepted(files) {
      setVideoSelection({
        file: files[0],
        previewUrl: URL.createObjectURL(files[0]),
      });
      setError(undefined);
    },
    onDropRejected() {
      setVideoSelection(undefined);
      setError("Selecciona un solo video compatible de hasta 50 MiB.");
    },
  });

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  function fillDevelopmentFixture() {
    const form = formRef.current;
    if (!form) {
      return;
    }
    const values: Record<string, string> = {
      case_id: `dev_case_${Date.now()}`,
      participant_code: "P-DEV-001",
      participant_age: "28",
      participant_sex: "ninguno_de_los_anteriores",
      record_date: new Date().toISOString().slice(0, 10),
      video_source: "fixture_desarrollo",
      capture_device: "smartphone",
      lighting: "adecuada",
      background: "adecuado",
      body_visibility: "completa",
      occlusions: "ninguna",
      surface: "plana",
      external_heel_support: "no",
      apparent_heel_contact: "continuo",
      complete_squat_observable: "true",
      support_condition_compliant: "true",
      plantar_support_observation: "Apoyo observable conforme al protocolo.",
    };
    for (const [name, value] of Object.entries(values)) {
      const field = form.elements.namedItem(name);
      if (
        field instanceof HTMLInputElement ||
        field instanceof HTMLSelectElement ||
        field instanceof HTMLTextAreaElement
      ) {
        field.value = value;
      }
    }
    setError(undefined);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!video) {
      setError("Selecciona el video que será analizado.");
      return;
    }
    setPending(true);
    setError(undefined);

    const raw = new FormData(event.currentTarget);
    const caseId = String(raw.get("case_id") ?? "").trim();
    const manualReview = {
      record_date: optionalString(raw, "record_date"),
      video_source: optionalString(raw, "video_source"),
      capture_device: optionalString(raw, "capture_device"),
      lighting: raw.get("lighting"),
      background: raw.get("background"),
      body_visibility: raw.get("body_visibility"),
      occlusions: raw.get("occlusions"),
      complete_squat_observable:
        raw.get("complete_squat_observable") === "true",
      surface: raw.get("surface"),
      external_heel_support: raw.get("external_heel_support"),
      apparent_heel_contact: raw.get("apparent_heel_contact"),
      support_condition_compliant:
        raw.get("support_condition_compliant") === "true",
      plantar_support_observation: optionalString(
        raw,
        "plantar_support_observation",
      ),
    };
    const payload = new FormData();
    payload.set("video", video);
    payload.set("case_id", caseId);
    payload.set(
      "participant_code",
      optionalString(raw, "participant_code") ?? "",
    );
    const participantAge = optionalString(raw, "participant_age");
    const participantSex = optionalString(raw, "participant_sex");
    if (participantAge) payload.set("participant_age", participantAge);
    if (participantSex) payload.set("participant_sex", participantSex);
    payload.set("profile", "no_etiquetado");
    payload.set("protocol_review_status", "aceptado");
    payload.set("manual_review_json", JSON.stringify(manualReview));

    const supabase = createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();
    if (!session?.access_token) {
      setError("La sesión expiró. Vuelve a iniciar sesión.");
      setPending(false);
      return;
    }

    try {
      const response = await fetch(`${getApiBaseUrl()}/squat/cases`, {
        method: "POST",
        headers: { Authorization: `Bearer ${session.access_token}` },
        body: payload,
      });
      if (!response.ok) {
        const detail = (await response.json().catch(() => null)) as
          | { detail?: string }
          | null;
        throw new Error(detail?.detail ?? `Error ${response.status}`);
      }
      router.push(`/cases/${caseId}`);
      router.refresh();
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "No se pudo registrar el caso.",
      );
      setPending(false);
    }
  }

  return (
    <form ref={formRef} onSubmit={handleSubmit} className="mt-8 grid gap-6">
      {development ? (
        <div className="flex flex-col gap-3 rounded-2xl border border-dashed border-primary/40 bg-primary/5 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium">Herramientas de desarrollo</p>
            <p className="text-xs text-muted-foreground">
              Completa el Instrumento 1 con valores reproducibles. El video se
              adjunta por separado.
            </p>
          </div>
          <Button
            type="button"
            variant="outline"
            onClick={fillDevelopmentFixture}
          >
            <FlaskConicalIcon aria-hidden="true" />
            Completar datos de prueba
          </Button>
        </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Identificación y captura</CardTitle>
          <CardDescription>
            Datos trazables del registro, sin información clínica.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FieldGroup className="grid gap-5 md:grid-cols-2">
            <TextField
              name="case_id"
              label="Código del video"
              description="Entre 3 y 64 caracteres: letras, números, guion o guion bajo."
              pattern="[A-Za-z0-9][A-Za-z0-9_-]{2,63}"
              required
            />
            <TextField
              name="participant_code"
              label="Código del participante"
            />
            <TextField
              name="participant_age"
              label="Edad del participante"
              type="number"
              min={18}
              max={120}
            />
            <SelectField
              name="participant_sex"
              label="Sexo del participante"
              options={[
                ["", "No especificado"],
                ["masculino", "Masculino"],
                ["femenino", "Femenino"],
                [
                  "ninguno_de_los_anteriores",
                  "Ninguno de los anteriores",
                ],
              ]}
            />
            <TextField name="record_date" label="Fecha de registro" type="date" />
            <TextField name="video_source" label="Fuente del video" />
            <TextField
              name="capture_device"
              label="Dispositivo de captura"
            />
          </FieldGroup>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Condiciones observables</CardTitle>
          <CardDescription>
            Escalas cerradas validadas en el Instrumento 1.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-5 md:grid-cols-2">
          <SelectField
            name="lighting"
            label="Iluminación"
            options={[
              ["adecuada", "Adecuada"],
              ["regular", "Regular"],
              ["deficiente", "Deficiente"],
            ]}
          />
          <SelectField
            name="background"
            label="Fondo visual"
            options={[
              ["adecuado", "Adecuado"],
              ["regular", "Regular"],
              ["deficiente", "Deficiente"],
            ]}
          />
          <SelectField
            name="body_visibility"
            label="Visibilidad corporal"
            options={[
              ["completa", "Completa"],
              ["parcial_utilizable", "Parcial utilizable"],
              ["insuficiente", "Insuficiente"],
            ]}
          />
          <SelectField
            name="occlusions"
            label="Oclusiones"
            options={[
              ["ninguna", "Ninguna"],
              ["leve", "Leve"],
              ["moderada", "Moderada"],
              ["severa", "Severa"],
            ]}
          />
          <SelectField
            name="surface"
            label="Superficie"
            options={[
              ["plana", "Plana"],
              ["no_plana", "No plana"],
              ["no_verificable", "No verificable"],
            ]}
          />
          <SelectField
            name="external_heel_support"
            label="Soporte externo bajo talones"
            options={[
              ["no", "No"],
              ["si", "Sí"],
              ["no_verificable", "No verificable"],
            ]}
          />
          <SelectField
            name="apparent_heel_contact"
            label="Contacto aparente de talones"
            options={[
              ["continuo", "Continuo"],
              ["elevacion_breve", "Elevación breve"],
              [
                "elevacion_evidente_o_sostenida",
                "Elevación evidente o sostenida",
              ],
              ["no_verificable", "No verificable"],
            ]}
          />
          <SelectField
            name="complete_squat_observable"
            label="Sentadilla completa observable"
            options={[
              ["true", "Sí"],
              ["false", "No"],
            ]}
          />
          <SelectField
            name="support_condition_compliant"
            label="Condición de apoyo conforme al protocolo"
            options={[
              ["true", "Sí"],
              ["false", "No"],
            ]}
          />
          <TextField
            name="plantar_support_observation"
            label="Observación del apoyo plantar"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Archivo de video</CardTitle>
          <CardDescription>
            Vista anterior, plano frontal y sin carga externa.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            {...dropzone.getRootProps()}
            className="grid cursor-pointer place-items-center rounded-2xl border border-dashed p-10 text-center transition-colors hover:bg-muted/50 focus-within:ring-3 focus-within:ring-ring/50"
          >
            <input {...dropzone.getInputProps()} aria-label="Video del caso" />
            {video ? (
              <>
                <FileVideoIcon className="size-9 text-primary" />
                <p className="mt-3 font-medium">{video.name}</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {(video.size / 1024 / 1024).toFixed(1)} MiB
                </p>
              </>
            ) : (
              <>
                <UploadCloudIcon className="size-9 text-primary" />
                <p className="mt-3 font-medium">
                  Arrastra el video o selecciónalo
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  MP4, MOV, WEBM o AVI · máximo 50 MiB
                </p>
              </>
            )}
          </div>
          {previewUrl ? (
            <div className="mt-5 overflow-hidden rounded-2xl border bg-black">
              <video
                key={previewUrl}
                src={previewUrl}
                aria-label="Vista previa del video seleccionado"
                className="max-h-[34rem] w-full object-contain"
                controls
                muted
                playsInline
                preload="metadata"
              />
            </div>
          ) : null}
        </CardContent>
      </Card>

      {error ? (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}

      <div className="flex justify-end">
        <Button type="submit" size="lg" disabled={pending}>
          {pending ? (
            <LoaderCircleIcon className="animate-spin" aria-hidden="true" />
          ) : (
            <UploadCloudIcon aria-hidden="true" />
          )}
          {pending ? "Procesando video..." : "Registrar y analizar"}
        </Button>
      </div>
    </form>
  );
}

function TextField({
  description,
  label,
  name,
  ...inputProps
}: {
  description?: string;
  label: string;
  name: string;
} & React.ComponentProps<typeof Input>) {
  return (
    <Field>
      <FieldLabel htmlFor={name}>{label}</FieldLabel>
      <Input id={name} name={name} {...inputProps} />
      {description ? (
        <FieldDescription>{description}</FieldDescription>
      ) : null}
    </Field>
  );
}

function SelectField({
  label,
  name,
  options,
}: {
  label: string;
  name: string;
  options: Array<[string, string]>;
}) {
  return (
    <Field>
      <FieldLabel htmlFor={name}>{label}</FieldLabel>
      <select id={name} name={name} className={selectClassName}>
        {options.map(([value, text]) => (
          <option key={value} value={value}>
            {text}
          </option>
        ))}
      </select>
    </Field>
  );
}

function optionalString(formData: FormData, name: string): string | null {
  const value = String(formData.get(name) ?? "").trim();
  return value || null;
}
