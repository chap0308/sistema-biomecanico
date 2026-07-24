"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import {
  FileVideoIcon,
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
  const [video, setVideo] = useState<File>();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string>();
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
      setVideo(files[0]);
      setError(undefined);
    },
    onDropRejected() {
      setVideo(undefined);
      setError("Selecciona un solo video compatible de hasta 50 MiB.");
    },
  });

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
    <form onSubmit={handleSubmit} className="mt-8 grid gap-6">
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
