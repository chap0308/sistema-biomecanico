import { ActivityIcon, CheckCircle2Icon, ScanLineIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiServerFetch } from "@/lib/api/server";
import { requireRole } from "@/lib/auth/session";
import type { SquatCaseReport } from "@/types/squat-case-report";

type CaseDetailPageProps = {
  params: Promise<{ caseId: string }>;
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
    // The explicit unavailable state below is preferable to a generic 500 page.
  }

  if (!report) {
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

  return (
    <main className="mx-auto w-full max-w-6xl px-6 py-10 lg:px-10">
      <Badge variant="secondary">{report.status.replaceAll("_", " ")}</Badge>
      <h1 className="mt-4 font-mono text-3xl font-semibold tracking-tight">
        {report.case_id}
      </h1>
      <p className="mt-2 text-muted-foreground">
        Pipeline {report.pipeline_version} · reporte trazable del sistema
      </p>

      <section className="mt-8 grid gap-5 md:grid-cols-3">
        <SummaryCard
          icon={ScanLineIcon}
          title="Pose 2D"
          value={
            report.pose
              ? `${report.pose.valid_frames_percentage.toFixed(1)} %`
              : "Sin datos"
          }
          description="Fotogramas válidos"
        />
        <SummaryCard
          icon={ActivityIcon}
          title="Repeticiones"
          value={String(report.segmentation?.repetitions_detected ?? 0)}
          description="Segmentadas en el video"
        />
        <SummaryCard
          icon={CheckCircle2Icon}
          title="Patrones presentes"
          value={String(report.findings?.detected_findings.length ?? 0)}
          description="Clasificación multilabel"
        />
      </section>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Resultado principal</CardTitle>
          <CardDescription>
            Compensaciones observables, no diagnósticos clínicos.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {report.findings?.detected_findings.length ? (
            report.findings.detected_findings.map((finding) => (
              <Badge key={finding}>{finding.replaceAll("_", " ")}</Badge>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">
              No se registraron patrones presentes o el análisis fue parcial.
            </p>
          )}
        </CardContent>
      </Card>
    </main>
  );
}

function SummaryCard({
  description,
  icon: Icon,
  title,
  value,
}: {
  description: string;
  icon: typeof ScanLineIcon;
  title: string;
  value: string;
}) {
  return (
    <Card>
      <CardHeader>
        <Icon className="size-5 text-primary" aria-hidden="true" />
        <CardDescription>{title}</CardDescription>
        <CardTitle className="font-mono text-2xl">{value}</CardTitle>
      </CardHeader>
      <CardContent className="text-xs text-muted-foreground">
        {description}
      </CardContent>
    </Card>
  );
}
