"use client";

import { CircleAlertIcon, RotateCcwIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function GlobalError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="grid min-h-dvh place-items-center px-6 py-12">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="mb-2 grid size-11 place-items-center rounded-full bg-destructive/10 text-destructive">
            <CircleAlertIcon aria-hidden="true" />
          </div>
          <CardTitle>No se pudo mostrar esta sección</CardTitle>
          <CardDescription>
            La sesión y los datos permanecen intactos. Intenta cargar nuevamente
            la vista.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button type="button" onClick={reset}>
            <RotateCcwIcon data-icon="inline-start" aria-hidden="true" />
            Reintentar
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
