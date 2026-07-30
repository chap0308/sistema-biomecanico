"use client";

import { useEffect, useRef } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { ExpertRepetition } from "@/types/squat-expert";

type ExpertReviewPlayerProps = {
  assignmentId: string;
  repetitions?: ExpertRepetition[];
  activeRepetition?: number | null;
  onRepetitionChange?: (repetitionIndex: number | null) => void;
  autoPlaySelected?: boolean;
  loopSelectedRepetition?: boolean;
  lockNavigationToActive?: boolean;
  showRepetitionNavigation?: boolean;
  showFullVideoOption?: boolean;
};

export function ExpertReviewPlayer({
  assignmentId,
  repetitions = [],
  activeRepetition = null,
  onRepetitionChange,
  autoPlaySelected = false,
  loopSelectedRepetition = false,
  lockNavigationToActive = false,
  showRepetitionNavigation = true,
  showFullVideoOption = true,
}: ExpertReviewPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const selected = repetitions.find(
    (repetition) => repetition.repetition_index === activeRepetition,
  );

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    video.pause();
    video.currentTime = selected?.start_seconds ?? 0;
    if (autoPlaySelected && video.offsetParent !== null) {
      video.muted = true;
      void video.play().catch(() => {
        // Autoplay can still be denied by browser or device policy.
      });
    }
  }, [autoPlaySelected, selected]);

  function playRepetition(repetition: ExpertRepetition) {
    onRepetitionChange?.(repetition.repetition_index);
    const video = videoRef.current;
    if (!video) return;
    video.currentTime = repetition.start_seconds;
    void video.play().catch(() => {
      // A quick repetition change can pause a pending play request.
    });
  }

  function keepInsideSelectedRepetition() {
    const video = videoRef.current;
    if (!video || !selected) return;
    if (video.currentTime < selected.start_seconds) {
      video.currentTime = selected.start_seconds;
    } else if (video.currentTime > selected.end_seconds) {
      video.currentTime = selected.end_seconds;
    }
  }

  function stopAtRepetitionEnd() {
    const video = videoRef.current;
    if (!video || !selected) return;
    const boundary = resolveRepetitionBoundary(
      video.currentTime,
      selected.start_seconds,
      selected.end_seconds,
      loopSelectedRepetition,
    );
    if (boundary === null) return;
    video.currentTime = boundary.time;
    if (boundary.pause) {
      video.pause();
    }
  }

  return (
    <div className="flex min-w-0 max-w-full flex-col gap-3">
      <div className="overflow-hidden rounded-xl border bg-slate-950">
        <video
          ref={videoRef}
          className="aspect-video w-full object-contain"
          controls
          playsInline
          preload="metadata"
          onSeeking={keepInsideSelectedRepetition}
          onTimeUpdate={stopAtRepetitionEnd}
          src={`/api/squat/expert/assignments/${assignmentId}/video`}
        >
          Tu navegador no admite la reproducción de video.
        </video>
      </div>
      {selected ? (
        <div className="flex items-center justify-between gap-3 text-xs text-muted-foreground">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline">
              Repetición {selected.repetition_index}
            </Badge>
            {loopSelectedRepetition ? (
              <Badge variant="secondary">Bucle del fragmento</Badge>
            ) : null}
          </div>
          <span className="shrink-0 whitespace-nowrap font-mono">
            {selected.start_seconds.toFixed(2)}–{selected.end_seconds.toFixed(2)} s
          </span>
        </div>
      ) : null}
      {showRepetitionNavigation && repetitions.length > 0 ? (
        <div
          className="flex w-full min-w-0 gap-2 overflow-x-auto pb-1"
          aria-label="Navegar por repeticiones"
        >
          {repetitions.map((repetition) => (
            <Button
              key={repetition.repetition_index}
              type="button"
              variant={
                activeRepetition === repetition.repetition_index
                  ? "default"
                  : "outline"
              }
              size="sm"
              className="shrink-0"
              disabled={
                lockNavigationToActive &&
                activeRepetition !== repetition.repetition_index
              }
              aria-pressed={
                activeRepetition === repetition.repetition_index
              }
              onClick={() => playRepetition(repetition)}
            >
              Repetición {repetition.repetition_index}
            </Button>
          ))}
          {showFullVideoOption ? (
            <Button
              type="button"
              variant={activeRepetition === null ? "default" : "outline"}
              size="sm"
              className="shrink-0"
              aria-pressed={activeRepetition === null}
              onClick={() => onRepetitionChange?.(null)}
            >
              Video completo
            </Button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

export function resolveRepetitionBoundary(
  currentTime: number,
  startTime: number,
  endTime: number,
  loop: boolean,
): { time: number; pause: boolean } | null {
  if (currentTime < endTime) return null;
  return loop
    ? { time: startTime, pause: false }
    : { time: endTime, pause: true };
}
