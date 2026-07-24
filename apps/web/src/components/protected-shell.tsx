import Link from "next/link";
import { LogOutIcon, ScanLineIcon } from "lucide-react";

import { logout } from "@/app/login/actions";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { homeForRole } from "@/lib/auth/roles";
import { requireResearchProfile } from "@/lib/auth/session";

export async function ProtectedShell({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const profile = await requireResearchProfile();
  const roleLabel =
    profile.role === "investigator" ? "Investigador" : "Evaluador experto";

  return (
    <div className="min-h-dvh">
      <header className="border-b bg-background/90 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-6 py-4 lg:px-10">
          <Link
            href={homeForRole(profile.role)}
            className="flex min-w-0 items-center gap-3"
          >
            <div className="grid size-9 shrink-0 place-items-center rounded-full bg-foreground text-background">
              <ScanLineIcon aria-hidden="true" />
            </div>
            <div className="min-w-0">
              <p className="truncate font-heading text-sm font-semibold">
                Laboratorio de movimiento
              </p>
              <p className="truncate font-mono text-[0.64rem] uppercase tracking-[0.15em] text-muted-foreground">
                {profile.displayName}
              </p>
            </div>
          </Link>
          <div className="flex items-center gap-2">
            <Badge variant="outline">{roleLabel}</Badge>
            <form action={logout}>
              <Button type="submit" variant="ghost" size="icon-sm">
                <LogOutIcon aria-hidden="true" />
                <span className="sr-only">Cerrar sesión</span>
              </Button>
            </form>
          </div>
        </div>
      </header>
      {children}
    </div>
  );
}
