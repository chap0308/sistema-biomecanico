import { ArrowLeftIcon, FileQuestionIcon } from "lucide-react";
import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function NotFound() {
  return (
    <main className="grid min-h-dvh place-items-center px-6 py-12">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="mb-2 grid size-11 place-items-center rounded-full bg-secondary">
            <FileQuestionIcon aria-hidden="true" />
          </div>
          <CardTitle>La página no existe</CardTitle>
          <CardDescription>
            Verifica la dirección o regresa al acceso principal del estudio.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link href="/" className={buttonVariants({ variant: "outline" })}>
            <ArrowLeftIcon data-icon="inline-start" aria-hidden="true" />
            Volver al inicio
          </Link>
        </CardContent>
      </Card>
    </main>
  );
}
