import { Suspense } from "react";

import { ProtectedShell } from "@/components/protected-shell";
import { Skeleton } from "@/components/ui/skeleton";

export default function ProtectedLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <Suspense fallback={<ProtectedShellSkeleton />}>
      <ProtectedShell>{children}</ProtectedShell>
    </Suspense>
  );
}

function ProtectedShellSkeleton() {
  return (
    <main className="mx-auto min-h-dvh w-full max-w-7xl px-6 py-8 lg:px-10">
      <div className="flex items-center justify-between border-b pb-6">
        <Skeleton className="h-10 w-56" />
        <Skeleton className="h-9 w-32" />
      </div>
      <Skeleton className="mt-10 h-64 w-full" />
    </main>
  );
}
