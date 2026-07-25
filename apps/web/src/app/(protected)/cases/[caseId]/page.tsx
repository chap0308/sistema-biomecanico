import Image from "next/image";
import Link from "next/link";
import {
  ActivityIcon,
  ArrowLeftIcon,
  CheckCircle2Icon,
  CircleAlertIcon,
  DownloadIcon,
  FlaskConicalIcon,
  ScanLineIcon,
  UserRoundPlusIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress, ProgressLabel } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { apiServerFetch } from "@/lib/api/server";
import { requireRole } from "@/lib/auth/session";
import type {
  SquatCaseReport,
  SquatRuleDecision,
} from "@/types/squat-case-report";

import { AnalysisPlayer } from "./analysis-player";
import { formatMetric, MetricEvidence } from "./metric-evidence";

type CaseDetailPageProps = {
  params: Promise<{ caseId: string }>;
};

const findingLabels: Record<string, string> = {
  inclinacion_lateral_tronco: "Inclinación lateral del tronco",
  desplazamiento_lateral_pelvis: "Desplazamiento lateral de pelvis",
  valgo_dinamico_visible: "Valgo dinámico visible",
  asimetria_bilateral_observable: "Asimetría bilateral observable",
};

const directionLabels: Record<string, string> = {
  izquierda: "hacia la izquierda",
  derecha: "hacia la derecha",
  bilateral: "bilateral",
  predominio_izquierdo: "predominio izquierdo",
  predominio_derecho: "predominio derecho",
};

export default async function CaseDetailPage({
  params,
}: CaseDetailPageProps) {
  await requireRole("investigator");
  const { caseId } = await params;
  let report: SquatCaseReport | null = null;
  try {
    report = await apiServerFetch<SquatCaseReport>(`/squat/cases/${caseId}`);
  } catch {
    // An explicit recovery state is clearer than a generic server error.
  }

  if (!report) {
    return <UnavailableCase />;
  }

  const assetUrl = (filename: string) =>
    `/api/squat/cases/${encodeURIComponent(report.case_id)}/assets/${encodeURIComponent(filename)}`;
  const captures = report.artifacts?.event_captures ?? [];
  const peakCaptures = captures.filter(
    (capture) => capture.event === "maxima_profundidad",
  );

  return (
    <main className="mx-auto w-full max-w-7xl px-5 py-8 lg:px-10 lg:py-10">
      <Link
        href="/cases"
        className={buttonVariants({
          size: "sm",
          variant: "ghost",
          className: "-ml-3",
        })}
      >
        <ArrowLeftIcon aria-hidden="true" />
        Volver al historial
      </Link>

      <header className="mt-5 border-b pb-7">
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={report.status} />
          {report.findings?.ruleset_status === "provisional" && (
            <Badge variant="outline">Umbrales provisionales</Badge>
          )}
          {report.status === "analisis_completo" ? (
            <div className="ml-auto flex flex-wrap gap-2">
              <Link
                href={`/cases/${report.case_id}/assignments`}
                className={buttonVariants({
                  size: "sm",
                  variant: "outline",
                })}
              >
                <UserRoundPlusIcon aria-hidden="true" />
                Asignar evaluadores
              </Link>
              <Link
                href={`/cases/${report.case_id}/comparison`}
                className={buttonVariants({ size: "sm" })}
              >
                <ActivityIcon aria-hidden="true" />
                Comparar resultados
              </Link>
            </div>
          ) : null}
        </div>
        <div className="mt-4 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground">
              Análisis biomecánico interpretable
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
              {report.case_id}
            </h1>
          </div>
          <p className="max-w-xl text-sm leading-6 text-muted-foreground">
            Pipeline {report.pipeline_version}
            {report.findings
              ? ` · reglas ${report.findings.ruleset_version}`
              : ""}. Los resultados describen compensaciones observables y no
            constituyen un diagnóstico clínico.
          </p>
        </div>
      </header>

      <section
        className="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
        aria-label="Resumen del análisis"
      >
        <SummaryCard
          icon={ScanLineIcon}
          label="Fotogramas válidos"
          value={
            report.pose
              ? `${report.pose.valid_frames_percentage.toFixed(1)} %`
              : "Sin datos"
          }
        />
        <SummaryCard
          icon={ActivityIcon}
          label="Repeticiones"
          value={String(report.segmentation?.repetitions_detected ?? 0)}
        />
        <SummaryCard
          icon={CheckCircle2Icon}
          label="Hallazgos por repetición"
          value={String(report.findings?.detected_findings.length ?? 0)}
        />
        <SummaryCard
          icon={FlaskConicalIcon}
          label="Puntos clave promedio"
          value={report.pose?.mean_detected_keypoints.toFixed(1) ?? "Sin datos"}
        />
      </section>

      {report.quality && !report.quality.eligible_for_analysis && (
        <Card className="mt-6 border-destructive/35 bg-destructive/5">
          <CardHeader className="flex-row items-start gap-3">
            <CircleAlertIcon
              className="mt-0.5 size-5 text-destructive"
              aria-hidden="true"
            />
            <div>
              <CardTitle className="text-base">
                Video no incorporado al análisis formal
              </CardTitle>
              <CardDescription className="mt-1">
                {report.quality.exclusion_reasons.join(" ") ||
                  "No superó uno o más controles técnicos de calidad."}
              </CardDescription>
            </div>
          </CardHeader>
        </Card>
      )}

      <section className="mt-7 grid gap-6 xl:grid-cols-[1.35fr_0.85fr]">
        <Card className="overflow-hidden">
          <CardHeader>
            <CardTitle>Movimiento analizado</CardTitle>
            <CardDescription>
              Overlay anonimizado con pose 2D y accesos a los eventos de cada
              repetición.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {report.artifacts?.overlay_video &&
            report.segmentation?.repetitions.length ? (
              <AnalysisPlayer
                assetUrl={assetUrl(report.artifacts.overlay_video)}
                captures={captures}
                posterUrl={
                  peakCaptures[0]
                    ? assetUrl(peakCaptures[0].relative_path)
                    : undefined
                }
                repetitions={report.segmentation.repetitions}
              />
            ) : (
              <EmptyEvidence text="El overlay o la segmentación no están disponibles para este caso." />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resultado por patrón</CardTitle>
            <CardDescription>
              Cada criterio se evalúa de forma independiente; un caso puede
              presentar múltiples compensaciones.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {report.findings?.decisions.length ? (
              report.findings.decisions.map((decision) => (
                <FindingSummary
                  key={`${decision.repetition_index}-${decision.finding}`}
                  decision={decision}
                />
              ))
            ) : (
              <EmptyEvidence text="No se emitieron decisiones biomecánicas para este registro." />
            )}
          </CardContent>
        </Card>
      </section>

      {report.findings?.decisions.length ? (
        <section className="mt-7">
          <SectionHeading
            eyebrow="Trazabilidad"
            title="Valores y umbrales por repetición"
            description="Cada ejecución conserva su propia etiqueta, valor calculado y criterio provisional aplicado."
          />
          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            {report.findings.decisions.map((decision) => (
              <Card
                key={`${decision.repetition_index}-${decision.finding}`}
              >
                <CardHeader>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <CardTitle className="text-base">
                        Repetición {decision.repetition_index} ·{" "}
                        {findingLabels[decision.finding] ?? decision.finding}
                      </CardTitle>
                      <CardDescription className="mt-1 font-mono text-xs">
                        {decision.metric}
                      </CardDescription>
                    </div>
                    <DecisionBadge status={decision.status} />
                  </div>
                </CardHeader>
                <CardContent>
                  <MetricEvidence decision={decision} />
                  <p className="mt-4 border-t pt-4 text-xs leading-5 text-muted-foreground">
                    {decision.rationale}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      ) : null}

      {peakCaptures.length ? (
        <section className="mt-9">
          <SectionHeading
            eyebrow="Comparación visual"
            title="Máxima profundidad por repetición"
            description="Los fotogramas permiten revisar la consistencia del patrón sin recorrer el video completo."
          />
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            {peakCaptures.map((capture) => {
              const metrics = report.biomechanics?.repetitions.find(
                (item) => item.repetition_index === capture.repetition_index,
              );
              return (
                <Card
                  key={`${capture.repetition_index}-${capture.event}`}
                  className="overflow-hidden"
                >
                  <div className="relative aspect-[4/3] bg-slate-950">
                    <Image
                      src={assetUrl(capture.relative_path)}
                      alt={`Máxima profundidad de la repetición ${capture.repetition_index}`}
                      fill
                      unoptimized
                      className="object-contain"
                      sizes="(max-width: 768px) 100vw, 33vw"
                    />
                  </div>
                  <CardContent className="grid grid-cols-2 gap-x-4 gap-y-3 pt-4 text-xs">
                    <MetricLabel
                      label="Tiempo"
                      value={`${capture.timestamp_seconds.toFixed(2)} s`}
                    />
                    <MetricLabel
                      label="Calidad"
                      value={
                        metrics
                          ? `${metrics.valid_frames_percentage.toFixed(1)} %`
                          : "Sin dato"
                      }
                    />
                    <MetricLabel
                      label="Tronco"
                      value={
                        metrics
                          ? formatMetric(
                              metrics.trunk_inclination_at_peak_deg ?? null,
                              "deg",
                            )
                          : "Sin dato"
                      }
                    />
                    <MetricLabel
                      label="Pelvis"
                      value={
                        metrics
                          ? formatMetric(
                              metrics.pelvis_shift_at_peak_pct ?? null,
                              "pct",
                            )
                          : "Sin dato"
                      }
                    />
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </section>
      ) : null}

      <section className="mt-9">
        <SectionHeading
          eyebrow="Evidencia gráfica"
          title="Calidad, segmentación y variables"
          description="Estas salidas conectan la estimación de pose con las fases del movimiento y las métricas calculadas."
        />
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <EvidencePlot
            alt="Calidad de la estimación de pose por fotograma"
            filename={report.artifacts?.pose_quality_plot}
            title="Calidad de pose 2D"
            assetUrl={assetUrl}
          />
          <EvidencePlot
            alt="Segmentación temporal de las repeticiones"
            filename={report.artifacts?.segmentation_plot}
            title="Fases y repeticiones"
            assetUrl={assetUrl}
          />
          <EvidencePlot
            alt="Variables biomecánicas calculadas"
            filename={report.artifacts?.biomechanical_metrics_plot}
            title="Variables biomecánicas"
            assetUrl={assetUrl}
          />
        </div>
      </section>

      {report.quality ? (
        <section className="mt-9">
          <SectionHeading
            eyebrow="Control técnico"
            title="Criterios de aceptación del análisis"
            description="El sistema registra cada comprobación, el valor observado y el requisito aplicado."
          />
          <Card className="mt-4 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Criterio</TableHead>
                  <TableHead>Observado</TableHead>
                  <TableHead>Requisito</TableHead>
                  <TableHead>Resultado</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {report.quality.checks.map((check) => (
                  <TableRow key={check.check_id}>
                    <TableCell className="max-w-lg">
                      {check.description}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {check.observed}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {check.requirement}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={check.passed ? "secondary" : "destructive"}
                      >
                        {check.passed ? "Cumple" : "No cumple"}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </section>
      ) : null}

      <section className="mt-9">
        <SectionHeading
          eyebrow="Instrumento 2"
          title="Descargas técnicas"
          description="Archivos estructurados para auditoría, reproducción de cálculos y análisis posterior."
        />
        <div className="mt-4 flex flex-wrap gap-2">
          {technicalDownloads(report).map(({ filename, label }) => (
            <a
              key={filename}
              href={assetUrl(filename)}
              download
              className={buttonVariants({ size: "sm", variant: "outline" })}
            >
              <DownloadIcon aria-hidden="true" />
              {label}
            </a>
          ))}
        </div>
      </section>
    </main>
  );
}

function UnavailableCase() {
  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10 lg:px-10">
      <Card className="border-destructive/35">
        <CardHeader>
          <CardTitle>No se pudo recuperar el caso</CardTitle>
          <CardDescription>
            Verifica que FastAPI esté activo y que el análisis haya finalizado.
          </CardDescription>
        </CardHeader>
      </Card>
    </main>
  );
}

function SummaryCard({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof ScanLineIcon;
  label: string;
  value: string;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 pt-5">
        <span className="grid size-10 place-items-center rounded-lg bg-primary/10 text-primary">
          <Icon className="size-5" aria-hidden="true" />
        </span>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="mt-1 font-mono text-xl font-semibold tabular-nums">
            {value}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function FindingSummary({ decision }: { decision: SquatRuleDecision }) {
  const direction = decision.direction
    ? directionLabels[decision.direction] ?? decision.direction
    : null;
  return (
    <div className="rounded-xl border bg-muted/25 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold">
            Repetición {decision.repetition_index} ·{" "}
            {findingLabels[decision.finding] ?? decision.finding}
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            {direction ?? "Sin predominio lateral"}
          </p>
        </div>
        <DecisionBadge status={decision.status} />
      </div>
      <Progress
        className="mt-4"
        value={
          decision.aggregate_value == null
            ? 0
            : Math.min(
                100,
                (Math.abs(decision.aggregate_value) /
                  Math.max(decision.present_min, 1)) *
                  65,
              )
        }
      >
        <ProgressLabel>Valor de la ejecución</ProgressLabel>
        <span className="ml-auto font-mono text-sm text-muted-foreground">
          {formatMetric(decision.aggregate_value ?? null, decision.unit)}
        </span>
      </Progress>
    </div>
  );
}

function DecisionBadge({ status }: { status: SquatRuleDecision["status"] }) {
  if (status === "presente") return <Badge>Presente</Badge>;
  if (status === "ausente") return <Badge variant="secondary">Ausente</Badge>;
  return <Badge variant="outline">No concluyente</Badge>;
}

function StatusBadge({ status }: { status: SquatCaseReport["status"] }) {
  const labels: Record<SquatCaseReport["status"], string> = {
    registro_pendiente: "Registro pendiente",
    registro_rechazado: "Registro rechazado",
    analisis_parcial: "Análisis parcial",
    no_apto_para_analisis: "No apto para análisis",
    analisis_completo: "Análisis completo",
  };
  return <Badge variant="secondary">{labels[status]}</Badge>;
}

function SectionHeading({
  description,
  eyebrow,
  title,
}: {
  description: string;
  eyebrow: string;
  title: string;
}) {
  return (
    <div className="max-w-3xl">
      <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
        {eyebrow}
      </p>
      <h2 className="mt-2 text-2xl font-semibold tracking-tight">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        {description}
      </p>
    </div>
  );
}

function EvidencePlot({
  alt,
  assetUrl,
  filename,
  title,
}: {
  alt: string;
  assetUrl: (filename: string) => string;
  filename?: string | null;
  title: string;
}) {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">{title}</CardTitle>
      </CardHeader>
      {filename ? (
        <div className="relative aspect-[4/3] border-t bg-white">
          <Image
            src={assetUrl(filename)}
            alt={alt}
            fill
            unoptimized
            className="object-contain p-2"
            sizes="(max-width: 1024px) 100vw, 33vw"
          />
        </div>
      ) : (
        <CardContent>
          <EmptyEvidence text="Gráfico no disponible." />
        </CardContent>
      )}
    </Card>
  );
}

function MetricLabel({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-muted-foreground">{label}</p>
      <p className="mt-0.5 font-mono font-medium">{value}</p>
    </div>
  );
}

function EmptyEvidence({ text }: { text: string }) {
  return <p className="text-sm leading-6 text-muted-foreground">{text}</p>;
}

function technicalDownloads(report: SquatCaseReport) {
  const files = [
    {
      filename: report.artifacts?.biomechanical_repetition_metrics_csv,
      label: "Métricas por repetición",
    },
    {
      filename: report.artifacts?.rule_evidence_csv,
      label: "Evidencia de reglas",
    },
    {
      filename: report.artifacts?.repetitions_csv,
      label: "Segmentación",
    },
    {
      filename: report.artifacts?.frame_quality_csv,
      label: "Calidad por fotograma",
    },
    {
      filename: report.artifacts?.landmarks_csv,
      label: "Puntos anatómicos clave",
    },
  ];
  return files.filter(
    (item): item is { filename: string; label: string } =>
      typeof item.filename === "string",
  );
}
