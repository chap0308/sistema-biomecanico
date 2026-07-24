import { ClipboardCheckIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { requireRole } from "@/lib/auth/session";

export default async function ExpertAssignmentsPage() {
  await requireRole("expert");

  return (
    <main className="mx-auto w-full max-w-7xl px-6 py-10 lg:px-10">
      <Badge variant="secondary">Evaluación ciega</Badge>
      <h1 className="mt-4 font-heading text-4xl font-semibold tracking-tight">
        Casos asignados
      </h1>
      <p className="mt-2 text-muted-foreground">
        Los resultados del sistema permanecerán ocultos hasta el envío.
      </p>

      <Card className="mt-10 border-dashed">
        <CardHeader>
          <div className="mb-2 grid size-11 place-items-center rounded-full bg-secondary">
            <ClipboardCheckIcon aria-hidden="true" />
          </div>
          <CardTitle>Sin asignaciones visibles</CardTitle>
          <CardDescription>
            La consulta y el formulario del Instrumento 3 se implementarán en
            la fase de evaluación experta.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          La ruta ya exige una cuenta con rol válido del estudio.
        </CardContent>
      </Card>
    </main>
  );
}
