import Link from "next/link";
import { ArrowLeftIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { requireRole } from "@/lib/auth/session";
import { NewCaseForm } from "./new-case-form";

export default async function NewCasePage() {
  await requireRole("investigator");
  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10 lg:px-10">
      <Link
        href="/cases"
        className={buttonVariants({
          size: "sm",
          variant: "ghost",
          className: "-ml-3 mb-5",
        })}
      >
        <ArrowLeftIcon aria-hidden="true" />
        Volver al historial
      </Link>
      <Badge variant="secondary">Instrumento 1</Badge>
      <h1 className="mt-4 font-heading text-4xl font-semibold tracking-tight">
        Registrar video
      </h1>
      <p className="mt-2 max-w-2xl text-muted-foreground">
        Documenta las condiciones observables antes de ejecutar el análisis.
      </p>
      <NewCaseForm />
    </main>
  );
}
