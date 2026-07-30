import { ScanLineIcon } from "lucide-react";
import type { Metadata } from "next";

import { LoginForm } from "@/app/login/login-form";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";

export const metadata: Metadata = {
  title: "Acceso",
  description: "Acceso por rol al laboratorio de sentadilla bilateral.",
};

export default function LoginPage() {
  return (
    <main className="relative grid min-h-dvh place-items-center overflow-hidden px-6 py-12">
      <div className="lab-grid absolute inset-0 -z-20" />
      <div className="absolute left-[-12rem] top-[-16rem] -z-10 size-[34rem] rounded-full bg-primary/12 blur-3xl" />

      <div className="absolute right-5 top-5">
        <ThemeToggle />
      </div>

      <div className="grid w-full max-w-5xl gap-10 lg:grid-cols-[1fr_28rem] lg:items-center">
        <section data-reveal>
          <Badge variant="secondary">Acceso controlado</Badge>
          <h1 className="mt-5 max-w-xl font-heading text-5xl font-semibold leading-[0.98] tracking-[-0.05em]">
            Evidencia biomecánica con trazabilidad por rol.
          </h1>
          <p className="mt-6 max-w-lg leading-7 text-muted-foreground">
            El investigador registra y analiza casos. Los evaluadores revisan
            únicamente los videos asignados y mantienen una evaluación ciega
            hasta completar su clasificación.
          </p>
        </section>

        <Card
          className="shadow-2xl shadow-primary/10"
          data-reveal
          style={{ animationDelay: "100ms" }}
        >
          <CardHeader>
            <div className="mb-3 grid size-11 place-items-center rounded-full bg-primary text-primary-foreground">
              <ScanLineIcon aria-hidden="true" />
            </div>
            <CardTitle role="heading" aria-level={2}>
              Iniciar sesión
            </CardTitle>
            <CardDescription>
              Laboratorio de sentadilla bilateral · Lima Sur 2026
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LoginForm />
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
