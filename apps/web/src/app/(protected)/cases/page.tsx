import { FileVideoIcon, PlusIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { requireRole } from "@/lib/auth/session";

export default async function CasesPage() {
  await requireRole("investigator");

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
        <Button disabled>
          <PlusIcon aria-hidden="true" />
          Registrar caso
        </Button>
      </div>

      <Card className="mt-10 border-dashed">
        <CardHeader>
          <div className="mb-2 grid size-11 place-items-center rounded-full bg-secondary">
            <FileVideoIcon aria-hidden="true" />
          </div>
          <CardTitle>Historial preparado</CardTitle>
          <CardDescription>
            La carga y paginación persistente se habilitarán en la fase F2.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          La sesión ya está protegida mediante Supabase SSR y el perfil activo
          posee permisos de investigador.
        </CardContent>
      </Card>
    </main>
  );
}
