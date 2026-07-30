import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const metricSkeletons = ["pose", "segmentación", "variables", "reglas"];

export default function CaseDetailLoading() {
  return (
    <main className="mx-auto w-full max-w-7xl px-5 py-10 lg:px-10">
      <Skeleton className="h-8 w-36" />
      <Skeleton className="mt-8 h-10 w-80 max-w-full" />
      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metricSkeletons.map((section) => (
          <Card key={section}>
            <CardContent className="pt-5">
              <Skeleton className="h-12 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
      <Skeleton className="mt-7 aspect-video w-full rounded-xl" />
    </main>
  );
}
