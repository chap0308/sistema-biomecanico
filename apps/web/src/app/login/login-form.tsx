"use client";

import { useState, type FormEvent } from "react";
import { LockKeyholeIcon } from "lucide-react";
import { useRouter } from "next/navigation";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { homeForRole, isSquatRole } from "@/lib/auth/roles";
import { createClient } from "@/lib/supabase/client";

export function LoginForm() {
  const router = useRouter();
  const [error, setError] = useState<string>();
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    setPending(true);
    setError(undefined);

    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") ?? "").trim();
    const password = String(formData.get("password") ?? "");
    const supabase = createClient();
    try {
      const { data, error: authError } =
        await supabase.auth.signInWithPassword({ email, password });
      const role = data.user?.user_metadata.squat_role;

      if (authError || !data.user) {
        setError("No se pudo validar la cuenta indicada.");
        return;
      }
      if (!isSquatRole(role)) {
        await supabase.auth.signOut();
        form.reset();
        setError("La cuenta no tiene un rol habilitado para este estudio.");
        return;
      }

      form.reset();
      router.replace(homeForRole(role));
      router.refresh();
    } catch {
      setError("No se pudo conectar con el servicio de autenticación.");
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <FieldGroup>
        <Field>
          <FieldLabel htmlFor="email">Correo institucional</FieldLabel>
          <Input
            id="email"
            name="email"
            type="email"
            autoComplete="username"
            required
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="password">Contraseña</FieldLabel>
          <Input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
          />
          <FieldDescription>
            Acceso exclusivo para el investigador y evaluadores asignados.
          </FieldDescription>
        </Field>
        {error ? (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : null}
        <Button type="submit" disabled={pending} className="w-full">
          <LockKeyholeIcon aria-hidden="true" />
          {pending ? "Validando..." : "Ingresar al estudio"}
        </Button>
      </FieldGroup>
    </form>
  );
}
