import { Skeleton } from "@/components/ui/skeleton";

export default function ProtectedLoading() {
  return (
    <main className="mx-auto w-full max-w-7xl px-6 py-10 lg:px-10">
      <Skeleton className="h-5 w-28" />
      <Skeleton className="mt-6 h-10 w-80 max-w-full" />
      <Skeleton className="mt-3 h-5 w-full max-w-2xl" />
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        <Skeleton className="h-28 rounded-2xl" />
        <Skeleton className="h-28 rounded-2xl" />
        <Skeleton className="h-28 rounded-2xl" />
      </div>
      <Skeleton className="mt-7 h-80 rounded-2xl" />
    </main>
  );
}
