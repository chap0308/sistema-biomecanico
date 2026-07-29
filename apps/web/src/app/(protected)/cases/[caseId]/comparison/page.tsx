import Link from "next/link";
import {
  ArrowLeftIcon,
  CheckCircle2Icon,
  CircleAlertIcon,
  DownloadIcon,
  ScaleIcon,
  UsersRoundIcon,
} from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
  CaseComparison,
  DatasetPerformance,
  PatternComparison,
} from "@/types/squat-comparison";

import { ConsensusForm } from "./consensus-form";
import { ReferenceLifecycleControls } from "./reference-lifecycle-controls";

const patternNames = {
  trunk_lateral_inclination: "Inclinación lateral del tronco",
  pelvis_lateral_shift: "Desplazamiento lateral de pelvis",
  visible_dynamic_valgus: "Valgo dinámico visible",
  bilateral_asymmetry: "Asimetría bilateral observable",
};

type ComparisonPageProps = {
  params: Promise<{ caseId: string }>;
};

export default async function ComparisonPage({
  params,
}: ComparisonPageProps) {
  await requireRole("investigator");
  const { caseId } = await params;
  let comparison: CaseComparison | null = null;
  let performance: DatasetPerformance | null = null;
  try {
    [comparison, performance] = await Promise.all([
      apiServerFetch<CaseComparison>(
        `/squat/cases/${encodeURIComponent(caseId)}/comparison`,
      ),
      apiServerFetch<DatasetPerformance>("/squat/comparison/metrics"),
    ]);
  } catch {
    // The explicit unavailable state avoids exposing backend details.
  }

  if (!comparison || !performance) {
    return (
      <main className="mx-auto w-full max-w-5xl px-6 py-10">
        <Card className="border-destructive/35">
          <CardHeader>
            <CardTitle>Comparación no disponible</CardTitle>
            <CardDescription>
              Verifica que el caso esté procesado y la API se encuentre activa.
            </CardDescription>
          </CardHeader>
        </Card>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-7xl px-5 py-8 lg:px-10 lg:py-10">
      <Link
        href={`/cases/${caseId}`}
        className={buttonVariants({
          size: "sm",
          variant: "ghost",
          className: "-ml-3",
        })}
      >
        <ArrowLeftIcon aria-hidden="true" />
        Volver al caso
      </Link>

      <header className="mt-6 flex flex-col justify-between gap-5 border-b pb-7 lg:flex-row lg:items-end">
        <div>
          <Badge variant="secondary">
            <ScaleIcon aria-hidden="true" />
            Comparación experta-sistema
          </Badge>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight">
            Instrumento 3 y desempeño
          </h1>
          <p className="mt-2 font-mono text-sm text-muted-foreground">
            {comparison.case_id}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <ReferenceLifecycleControls
            caseId={caseId}
            status={comparison.reference_status}
            readyForMetrics={comparison.ready_for_metrics}
          />
          <a
            href={`/api/squat/cases/${caseId}/exports/instruments.xlsx`}
            className={buttonVariants({ size: "sm", variant: "outline" })}
          >
            <DownloadIcon aria-hidden="true" />
            Excel
          </a>
          <a
            href={`/api/squat/cases/${caseId}/exports/report.pdf`}
            className={buttonVariants({ size: "sm" })}
          >
            <DownloadIcon aria-hidden="true" />
            Reporte PDF
          </a>
        </div>
      </header>

      <section className="mt-7 grid gap-4 md:grid-cols-3">
        <SummaryCard
          label="Evaluaciones enviadas"
          value={`${comparison.submitted_evaluations} / ${comparison.assigned_evaluators}`}
        />
        <SummaryCard
          label="Casos consolidados"
          value={String(performance.consolidated_cases)}
        />
        <SummaryCard
          label="F1-score acumulado"
          value={decimal(performance.overall.f1_score)}
        />
      </section>

      {performance.overall.included_pairs < 10 ? (
        <Alert className="mt-5">
          <CircleAlertIcon aria-hidden="true" />
          <AlertDescription>
            Las métricas son descriptivas y todavía tienen una muestra
            insuficiente para interpretar el desempeño definitivo.
          </AlertDescription>
        </Alert>
      ) : null}

      <section className="mt-9">
        <div className="flex items-center gap-3">
          <UsersRoundIcon className="size-5 text-primary" aria-hidden="true" />
          <div>
            <h2 className="text-2xl font-semibold tracking-tight">
              Consolidación por repetición y patrón
            </h2>
            <p className="text-sm text-muted-foreground">
              Cada ejecución y cada patrón constituyen una comparación independiente.
            </p>
          </div>
        </div>
        <div className="mt-5 grid gap-4 xl:grid-cols-2">
          {comparison.patterns.map((pattern) => (
            <PatternCard
              key={`${pattern.repetition_index}-${pattern.pattern_key}`}
              caseId={caseId}
              pattern={pattern}
              referenceStatus={comparison.reference_status}
            />
          ))}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-2xl font-semibold tracking-tight">
          Métricas acumuladas
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Los pares no concluyentes quedan fuera del denominador.
        </p>
        <Card className="mt-5 overflow-hidden">
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Ámbito</TableHead>
                  <TableHead>Pares</TableHead>
                  <TableHead>Exactitud</TableHead>
                  <TableHead>Precisión</TableHead>
                  <TableHead>Sensibilidad</TableHead>
                  <TableHead>F1</TableHead>
                  <TableHead>Kappa</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {[performance.overall, ...performance.by_pattern].map(
                  (metric) => (
                    <TableRow key={metric.scope}>
                      <TableCell className="font-medium">
                        {metricName(metric.scope)}
                      </TableCell>
                      <TableCell>{metric.included_pairs}</TableCell>
                      <TableCell>{percent(metric.accuracy)}</TableCell>
                      <TableCell>{percent(metric.precision)}</TableCell>
                      <TableCell>{percent(metric.sensitivity)}</TableCell>
                      <TableCell>{decimal(metric.f1_score)}</TableCell>
                      <TableCell>{decimal(metric.cohen_kappa)}</TableCell>
                    </TableRow>
                  ),
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}

function PatternCard({
  caseId,
  pattern,
  referenceStatus,
}: {
  caseId: string;
  pattern: PatternComparison;
  referenceStatus: CaseComparison["reference_status"];
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="text-base">
              Repetición {pattern.repetition_index} ·{" "}
              {patternNames[pattern.pattern_key]}
            </CardTitle>
            <CardDescription>
              {pattern.expert_judgments.length} evaluaciones disponibles
            </CardDescription>
          </div>
          <ReferenceBadge pattern={pattern} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 text-sm">
          {pattern.expert_judgments.map((judgment, index) => (
            <div
              key={judgment.evaluator_id}
              className="rounded-lg border bg-muted/35 p-3"
            >
              <p className="text-xs text-muted-foreground">
                Evaluador {index + 1}
              </p>
              <p className="mt-1 font-medium">
                {classificationLabel(
                  judgment.classification,
                  judgment.observed_side,
                )}
              </p>
            </div>
          ))}
          <div className="rounded-lg border bg-primary/5 p-3">
            <p className="text-xs text-muted-foreground">Sistema</p>
            <p className="mt-1 font-medium">
              {label(pattern.system_label)}
            </p>
          </div>
          <div className="rounded-lg border bg-card p-3">
            <p className="text-xs text-muted-foreground">Referencia final</p>
            <p className="mt-1 font-medium">
              {pattern.reference ? label(pattern.reference.label) : "Pendiente"}
            </p>
          </div>
        </div>
        {referenceStatus === "in_progress" &&
        pattern.expert_judgments.length > 0 ? (
          <ConsensusForm
            caseId={caseId}
            repetitionIndex={pattern.repetition_index}
            patternKey={pattern.pattern_key}
            currentReference={pattern.reference}
          />
        ) : null}
      </CardContent>
    </Card>
  );
}

function ReferenceBadge({ pattern }: { pattern: PatternComparison }) {
  if (pattern.reference_status !== "consolidada") {
    return <Badge variant="outline">Pendiente</Badge>;
  }
  if (pattern.exact_match === true) {
    return (
      <Badge>
        <CheckCircle2Icon aria-hidden="true" />
        Coincide
      </Badge>
    );
  }
  if (pattern.exact_match === false) {
    return <Badge variant="destructive">Discrepancia</Badge>;
  }
  return <Badge variant="outline">No calculable</Badge>;
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{label}</CardDescription>
        <CardTitle className="font-mono text-2xl">{value}</CardTitle>
      </CardHeader>
    </Card>
  );
}

function classificationLabel(classification: string, side: string | null) {
  return label(
    classification === "presente" && side
      ? `presente_${side}`
      : classification,
  );
}

function label(value: string) {
  return value.replaceAll("_", " ").replace(/^./, (letter) =>
    letter.toUpperCase(),
  );
}

function metricName(scope: string) {
  if (scope === "general") return "General";
  return patternNames[scope as keyof typeof patternNames] ?? scope;
}

function percent(value: number | null) {
  return value === null ? "N/D" : `${(value * 100).toFixed(1)} %`;
}

function decimal(value: number | null) {
  return value === null ? "N/D" : value.toFixed(3);
}
