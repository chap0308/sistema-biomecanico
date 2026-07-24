import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function CaseDetailLoading() {
  return (
    <main className="mx-auto w-full max-w-7xl px-5 py-10 lg:px-10">
      <Skeleton className="h-8 w-36" />
      <Skeleton className="mt-8 h-10 w-80 max-w-full" />
      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => (
          <Card key={index}>
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
