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
  lockNavigationToActive?: boolean;
  showFullVideoOption?: boolean;
};

export function ExpertReviewPlayer({
  assignmentId,
  repetitions = [],
  activeRepetition = null,
  onRepetitionChange,
  lockNavigationToActive = false,
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
  }, [selected]);

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
    if (video.currentTime >= selected.end_seconds) {
      video.pause();
      video.currentTime = selected.end_seconds;
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
          <Badge variant="outline">
            Repetición {selected.repetition_index}
          </Badge>
          <span className="font-mono">
            {selected.start_seconds.toFixed(2)}–{selected.end_seconds.toFixed(2)} s
          </span>
        </div>
      ) : null}
      {repetitions.length > 0 ? (
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
