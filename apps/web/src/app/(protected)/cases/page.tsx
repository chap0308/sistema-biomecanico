import Link from "next/link";
import { FileVideoIcon, PlusIcon } from "lucide-react";
import type { Metadata } from "next";

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
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  CASE_STATUS_LABELS,
  type CaseStatus,
  formatCaseStatus,
} from "@/lib/case-status";
import { apiServerFetch } from "@/lib/api/server";
import { requireRole } from "@/lib/auth/session";
import type { SquatCasePage } from "@/types/squat-case-page";

type CasesPageProps = {
  searchParams: Promise<{ page?: string; status?: string }>;
};

export const metadata: Metadata = {
  title: "Casos",
};

const caseDateFormatter = new Intl.DateTimeFormat("es-PE", {
  dateStyle: "medium",
});
const caseFilters: Array<{ label: string; value?: CaseStatus }> = [
  { label: "Todos" },
  { label: "Completados", value: "completed" },
  { label: "No incorporados", value: "excluded" },
  { label: "Con error", value: "failed" },
];

export default async function CasesPage({ searchParams }: CasesPageProps) {
  await requireRole("investigator");
  const query = await searchParams;
  const page = positiveInteger(query.page);
  const status = isCaseStatus(query.status) ? query.status : undefined;
  const params = new URLSearchParams({
    page: String(page),
    page_size: "10",
  });
  if (status) {
    params.set("status", status);
  }

  let result: SquatCasePage | null = null;
  let unavailable = false;
  try {
    result = await apiServerFetch<SquatCasePage>(
      `/squat/cases?${params.toString()}`,
    );
  } catch {
    unavailable = true;
  }

  return (
    <main className="mx-auto w-full max-w-7xl px-6 py-10 lg:px-10">
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <Badge variant="secondary">Área del investigador</Badge>
          <h1 className="mt-4 font-heading text-4xl font-semibold tracking-tight">
            Casos de sentadilla
          </h1>
          <p className="mt-2 text-muted-foreground">
            Registro, procesamiento y evidencia persistente del estudio.
          </p>
        </div>
        <Link href="/cases/new" className={buttonVariants()}>
          <PlusIcon aria-hidden="true" />
          Registrar caso
        </Link>
      </div>

      <StatusFilters activeStatus={status} />

      {unavailable ? (
        <ServiceUnavailable />
      ) : result && result.items.length ? (
        <CaseHistory result={result} status={status} />
      ) : (
        <EmptyHistory />
      )}
    </main>
  );
}

function StatusFilters({ activeStatus }: { activeStatus?: CaseStatus }) {
  return (
    <nav aria-label="Filtros del historial" className="mt-8 flex flex-wrap gap-2">
      {caseFilters.map((filter) => {
        const active = filter.value === activeStatus;
        return (
          <Link
            key={filter.label}
            href={{
              pathname: "/cases",
              query: filter.value ? { status: filter.value } : undefined,
            }}
            className={buttonVariants({
              size: "sm",
              variant: active ? "default" : "outline",
            })}
          >
            {filter.label}
          </Link>
        );
      })}
    </nav>
  );
}

function CaseHistory({
  result,
  status,
}: {
  result: SquatCasePage;
  status?: CaseStatus;
}) {
  return (
    <Card className="mt-5">
      <CardHeader className="border-b">
        <CardTitle>
          {result.total} {result.total === 1 ? "registro" : "registros"}
        </CardTitle>
        <CardDescription>
          Ordenados desde la incorporación más reciente.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Caso</TableHead>
              <TableHead>Participante</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead>Fecha</TableHead>
              <TableHead className="text-right">Detalle</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {result.items.map((item) => (
              <TableRow key={item.case_id}>
                <TableCell className="font-mono font-medium">
                  {item.case_id}
                </TableCell>
                <TableCell>{item.participant_code ?? "No indicado"}</TableCell>
                <TableCell>
                  <Badge variant="outline">
                    {formatCaseStatus(item.status)}
                  </Badge>
                </TableCell>
                <TableCell>
                  {caseDateFormatter.format(new Date(item.created_at))}
                </TableCell>
                <TableCell className="text-right">
                  <Link
                    href={`/cases/${item.case_id}`}
                    className={buttonVariants({ size: "sm", variant: "ghost" })}
                  >
                    Revisar
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {result.total_pages > 1 ? (
          <HistoryPagination result={result} status={status} />
        ) : null}
      </CardContent>
    </Card>
  );
}

function HistoryPagination({
  result,
  status,
}: {
  result: SquatCasePage;
  status?: CaseStatus;
}) {
  const href = (page: number) => {
    const params = new URLSearchParams({ page: String(page) });
    if (status) {
      params.set("status", status);
    }
    return `/cases?${params.toString()}`;
  };
  return (
    <Pagination className="mt-6">
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious
            href={href(Math.max(1, result.page - 1))}
            aria-disabled={result.page === 1}
            text="Anterior"
          />
        </PaginationItem>
        <PaginationItem>
          <span className="px-3 font-mono text-xs text-muted-foreground">
            {result.page} / {result.total_pages}
          </span>
        </PaginationItem>
        <PaginationItem>
          <PaginationNext
            href={href(Math.min(result.total_pages, result.page + 1))}
            aria-disabled={result.page === result.total_pages}
            text="Siguiente"
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}

function EmptyHistory() {
  return (
    <Card className="mt-5 border-dashed">
      <CardHeader>
        <div className="mb-2 grid size-11 place-items-center rounded-full bg-secondary">
          <FileVideoIcon aria-hidden="true" />
        </div>
        <CardTitle>Aún no hay casos registrados</CardTitle>
        <CardDescription>
          Registra el primer video para iniciar el Instrumento 1.
        </CardDescription>
      </CardHeader>
    </Card>
  );
}

function ServiceUnavailable() {
  return (
    <Card className="mt-5 border-destructive/35">
      <CardHeader>
        <CardTitle>Historial temporalmente no disponible</CardTitle>
        <CardDescription>
          Verifica que FastAPI y la persistencia de Supabase estén activos.
        </CardDescription>
      </CardHeader>
    </Card>
  );
}

function positiveInteger(value?: string): number {
  const parsed = Number(value ?? "1");
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 1;
}

function isCaseStatus(value?: string): value is CaseStatus {
  return Boolean(value && value in CASE_STATUS_LABELS);
}
