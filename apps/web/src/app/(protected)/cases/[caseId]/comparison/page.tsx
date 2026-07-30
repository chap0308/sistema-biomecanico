import Link from "next/link";
import {
  ArrowLeftIcon,
  CircleAlertIcon,
  DownloadIcon,
  ScaleIcon,
  UsersRoundIcon,
} from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
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
} from "@/types/squat-comparison";

import { PatternComparisonCard } from "./pattern-comparison-card";
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
          <a
            href={`/api/squat/cases/${caseId}/exports/technical-data.xlsx`}
            className={buttonVariants({ size: "sm", variant: "outline" })}
          >
            <DownloadIcon aria-hidden="true" />
            Datos técnicos
          </a>
          <ReferenceLifecycleControls
            caseId={caseId}
            status={comparison.reference_status}
            readyForMetrics={comparison.ready_for_metrics}
            assignedEvaluators={comparison.assigned_evaluators}
            submittedEvaluations={comparison.submitted_evaluations}
          />
          {comparison.reference_status === "closed" ? (
            <>
              <a
                href={`/api/squat/cases/${caseId}/exports/instruments.xlsx`}
                className={buttonVariants({
                  size: "sm",
                  variant: "outline",
                })}
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
            </>
          ) : (
            <>
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled
                title="Cierra el caso para habilitar la descarga."
              >
                <DownloadIcon aria-hidden="true" />
                Excel
              </Button>
              <Button
                type="button"
                size="sm"
                disabled
                title="Cierra el caso para habilitar la descarga."
              >
                <DownloadIcon aria-hidden="true" />
                Reporte PDF
              </Button>
            </>
          )}
        </div>
      </header>

      <section className="mt-7 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
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
        <SummaryCard
          label="Kappa de Fleiss del caso"
          value={decimal(comparison.expert_fleiss_kappa ?? null)}
          detail={
            (comparison.fleiss_items ?? 0)
              ? `${comparison.fleiss_items} ítems con tres expertos`
              : "Requiere tres expertos por ítem"
          }
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
            <PatternComparisonCard
              key={`${caseId}-${pattern.repetition_index}-${pattern.pattern_key}-${pattern.reference?.label ?? "pending"}`}
              caseId={caseId}
              initialPattern={pattern}
              referenceStatus={comparison.reference_status}
            />
          ))}
        </div>
      </section>

      {comparison.evaluator_observations.some(
        (item) => item.general_observation,
      ) ? (
        <section className="mt-8">
          <h2 className="text-xl font-semibold tracking-tight">
            Observaciones generales de los evaluadores
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Notas contextuales registradas al finalizar cada evaluación.
          </p>
          <div className="mt-4 grid gap-3 lg:grid-cols-3">
            {comparison.evaluator_observations.map((item, index) =>
              item.general_observation ? (
                <Card key={item.evaluator_id}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">
                      Evaluador {index + 1}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm leading-6 text-muted-foreground">
                    {item.general_observation}
                  </CardContent>
                </Card>
              ) : null,
            )}
          </div>
        </section>
      ) : null}

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
                  <TableHead>Kappa de Cohen</TableHead>
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

function SummaryCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail?: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{label}</CardDescription>
        <CardTitle className="font-mono text-2xl">{value}</CardTitle>
        {detail ? (
          <p className="text-xs text-muted-foreground">{detail}</p>
        ) : null}
      </CardHeader>
    </Card>
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
