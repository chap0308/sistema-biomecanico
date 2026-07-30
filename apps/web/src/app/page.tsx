import {
  ActivityIcon,
  CameraIcon,
  ChartNoAxesCombinedIcon,
  ChevronRightIcon,
  ScanLineIcon,
} from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";

const pipelineSteps = [
  {
    index: "01",
    title: "Registro técnico",
    description: "Protocolo, trazabilidad y factibilidad del video.",
    icon: CameraIcon,
  },
  {
    index: "02",
    title: "Estimación de pose",
    description: "Puntos anatómicos clave y calidad por fotograma.",
    icon: ScanLineIcon,
  },
  {
    index: "03",
    title: "Lectura biomecánica",
    description: "Variables, fases y reglas interpretables.",
    icon: ActivityIcon,
  },
  {
    index: "04",
    title: "Evidencia",
    description: "Overlay, métricas y comparación con expertos.",
    icon: ChartNoAxesCombinedIcon,
  },
] as const;

export default function Home() {
  return (
    <main className="relative isolate min-h-dvh overflow-hidden">
      <div className="lab-grid absolute inset-0 -z-20" />
      <div className="absolute -top-48 right-[-12rem] -z-10 size-[34rem] rounded-full bg-primary/10 blur-3xl" />

      <header className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
        <div className="flex items-center gap-3">
          <div className="grid size-9 place-items-center rounded-full border bg-background shadow-sm">
            <ScanLineIcon aria-hidden="true" />
          </div>
          <div>
            <p className="font-heading text-sm font-semibold tracking-tight">
              Laboratorio de movimiento
            </p>
            <p className="font-mono text-[0.64rem] uppercase tracking-[0.18em] text-muted-foreground">
              Tesis · Lima Sur 2026
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge className="hidden sm:inline-flex" variant="outline">
            Prototipo de investigación
          </Badge>
          <ThemeToggle />
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-7xl gap-12 px-6 pb-20 pt-14 lg:grid-cols-[1.1fr_0.9fr] lg:px-10 lg:pb-28 lg:pt-24">
        <div className="max-w-3xl" data-reveal>
          <Badge className="mb-6" variant="secondary">
            Visión por computadora + criterios interpretables
          </Badge>
          <h1 className="text-balance font-heading text-5xl font-semibold leading-[0.96] tracking-[-0.055em] sm:text-6xl lg:text-7xl">
            La sentadilla,
            <span className="block text-primary">convertida en evidencia.</span>
          </h1>
          <p className="mt-7 max-w-2xl text-pretty text-base leading-7 text-muted-foreground sm:text-lg">
            Un entorno trazable para registrar videos, observar compensaciones
            y contrastar la salida del sistema con evaluadores expertos sin
            presentar diagnósticos clínicos.
          </p>

          <div className="mt-10 grid max-w-xl grid-cols-3 border-y py-5">
            <Metric value="13" label="puntos críticos" />
            <Metric value="4" label="patrones" />
            <Metric value="3" label="instrumentos" />
          </div>
        </div>

        <Card
          className="self-end border-0 bg-foreground text-background shadow-[0_28px_80px_-38px_color-mix(in_oklch,var(--foreground),transparent_36%)] ring-0"
          data-reveal
          style={{ animationDelay: "120ms" }}
        >
          <CardHeader className="border-b border-background/15 pb-5">
            <CardTitle className="text-xl">Flujo verificable</CardTitle>
            <CardDescription className="text-background/60">
              Cada resultado conserva su origen técnico y metodológico.
            </CardDescription>
            <CardAction>
              <span className="font-mono text-xs text-background/45">v0.1</span>
            </CardAction>
          </CardHeader>
          <CardContent className="grid gap-1">
            {pipelineSteps.map((step) => {
              const Icon = step.icon;
              return (
                <div
                  key={step.index}
                  className="group grid grid-cols-[2rem_1fr_auto] items-center gap-3 border-b border-background/10 py-4 last:border-0"
                >
                  <span className="font-mono text-xs text-background/40">
                    {step.index}
                  </span>
                  <div>
                    <p className="font-heading font-medium">{step.title}</p>
                    <p className="mt-0.5 text-xs leading-5 text-background/55">
                      {step.description}
                    </p>
                  </div>
                  <div className="grid size-9 place-items-center rounded-full border border-background/15 transition-transform group-hover:translate-x-1">
                    <Icon aria-hidden="true" />
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      </section>

      <section className="border-t bg-background/75 py-9 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl flex-col justify-between gap-5 px-6 sm:flex-row sm:items-center lg:px-10">
          <div>
            <p className="font-heading text-lg font-semibold">
              Arquitectura preparada para la evaluación formal
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              Next.js SSR · FastAPI · Supabase local · procesamiento Python
            </p>
          </div>
          <Link
            href="/login"
            className={buttonVariants({ variant: "outline" })}
          >
            Ingresar al estudio
            <ChevronRightIcon aria-hidden="true" />
          </Link>
        </div>
      </section>
    </main>
  );
}

function Metric({ value, label }: { value: string; label: string }) {
  return (
    <div className="border-r px-4 first:pl-0 last:border-0">
      <p className="font-mono text-2xl font-semibold tracking-tight">{value}</p>
      <p className="mt-1 text-xs text-muted-foreground">{label}</p>
    </div>
  );
}
