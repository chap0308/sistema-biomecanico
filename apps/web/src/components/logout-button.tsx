"use client";

import { useState } from "react";
import { LoaderCircleIcon, LogOutIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { createClient } from "@/lib/supabase/client";

export function LogoutButton() {
  const [pending, setPending] = useState(false);

  async function logout() {
    setPending(true);
    await createClient().auth.signOut();
    window.location.replace("/login");
  }

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon-sm"
      disabled={pending}
      onClick={logout}
    >
      {pending ? (
        <LoaderCircleIcon className="animate-spin" aria-hidden="true" />
      ) : (
        <LogOutIcon aria-hidden="true" />
      )}
      <span className="sr-only">Cerrar sesión</span>
    </Button>
  );
}
