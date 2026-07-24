import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-7xl flex-col gap-8 px-6 py-10 lg:px-10">
      <div className="flex items-center justify-between">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-7 w-36" />
      </div>
      <div className="grid flex-1 gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <Skeleton className="min-h-96 rounded-3xl" />
        <Skeleton className="min-h-96 rounded-3xl" />
      </div>
    </main>
  );
}
