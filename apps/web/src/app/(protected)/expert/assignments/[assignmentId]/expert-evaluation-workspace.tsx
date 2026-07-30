"use client";

import { useEffect, useRef, useState } from "react";
import { EyeIcon, EyeOffIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { ExpertAssignment } from "@/types/squat-expert";

import { EvaluationForm } from "./evaluation-form";
import { ExpertReviewPlayer } from "./expert-review-player";

export function ExpertEvaluationWorkspace({
  assignment,
}: {
  assignment: ExpertAssignment;
}) {
  const repetitions = assignment.repetitions ?? [];
  const workspaceRef = useRef<HTMLDivElement>(null);
  const [activeRepetition, setActiveRepetition] = useState<number | null>(
    repetitions[0]?.repetition_index ?? null,
  );
  const [followReached, setFollowReached] = useState(false);
  const [playerDismissed, setPlayerDismissed] = useState(false);

  useEffect(() => {
    let frame = 0;

    function updateFromScroll() {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const sections = Array.from(
          workspaceRef.current?.querySelectorAll<HTMLElement>(
            "[data-repetition-index]",
          ) ?? [],
        );
        if (!sections.length) return;

        const firstTop = sections[0].getBoundingClientRect().top;
        const activationLine = Math.min(180, window.innerHeight * 0.25);
        setFollowReached(firstTop <= 96);

        const active =
          sections
            .filter(
              (section) =>
                section.getBoundingClientRect().top <= activationLine,
            )
            .at(-1) ?? sections[0];
        setActiveRepetition(Number(active.dataset.repetitionIndex));
      });
    }

    updateFromScroll();
    window.addEventListener("scroll", updateFromScroll, { passive: true });
    window.addEventListener("resize", updateFromScroll);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("scroll", updateFromScroll);
      window.removeEventListener("resize", updateFromScroll);
    };
  }, []);

  return (
    <div
      ref={workspaceRef}
      className="mt-8 grid items-start gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(24rem,0.78fr)] xl:grid-cols-[minmax(0,1fr)_minmax(28rem,0.85fr)]"
    >
      <section className="min-w-0">
        <div className="mb-5">
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
            Clasificación observacional
          </p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight">
            Patrones del movimiento
          </h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Al entrar en una repetición, el video se posiciona en el intervalo
            correspondiente para conservar la trazabilidad del juicio.
          </p>
        </div>
        <EvaluationForm
          assignment={assignment}
          onRepetitionFocus={setActiveRepetition}
        />
      </section>

      <aside className="order-first min-w-0 max-w-full max-lg:fixed max-lg:inset-x-3 max-lg:top-3 max-lg:z-30 lg:sticky lg:top-3 lg:z-20 lg:order-last">
        {followReached && !playerDismissed ? (
          <Card className="min-w-0 max-w-full overflow-hidden shadow-lg">
            <CardHeader className="flex flex-row items-start justify-between gap-3 py-3 lg:py-6">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <CardTitle>Video de revisión</CardTitle>
                  {activeRepetition ? (
                    <Badge variant="secondary">
                      Repetición {activeRepetition}
                    </Badge>
                  ) : (
                    <Badge variant="outline">Video completo</Badge>
                  )}
                </div>
                <CardDescription className="mt-1 hidden lg:block">
                  El reproductor permanece visible durante la clasificación.
                </CardDescription>
              </div>
              <Button
                type="button"
                size="icon-sm"
                variant="ghost"
                aria-label="Ocultar video de seguimiento"
                onClick={() => setPlayerDismissed(true)}
              >
                <EyeOffIcon aria-hidden="true" />
              </Button>
            </CardHeader>
            <CardContent className="pb-3 lg:pb-6">
              <ExpertReviewPlayer
                assignmentId={assignment.assignment_id}
                repetitions={repetitions}
                activeRepetition={activeRepetition}
                onRepetitionChange={setActiveRepetition}
                lockNavigationToActive
                showFullVideoOption={false}
              />
            </CardContent>
          </Card>
        ) : followReached && playerDismissed ? (
          <Button
            type="button"
            className="fixed right-4 bottom-4 shadow-lg"
            onClick={() => setPlayerDismissed(false)}
          >
            <EyeIcon aria-hidden="true" />
            Mostrar video
          </Button>
        ) : null}
      </aside>
    </div>
  );
}
