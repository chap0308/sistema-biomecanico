"use client";

import { useRef, useState } from "react";
import { CirclePlayIcon, LocateFixedIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import type {
  SquatEventCapture,
  SquatRepetition,
} from "@/types/squat-case-report";
import type { SquatCaseExplanation } from "@/types/squat-explanation";

import { ExplanationWorkspace } from "./explanation-workspace";

type AnalysisPlayerProps = {
  assetUrl: string;
  captures: SquatEventCapture[];
  posterUrl?: string;
  repetitions: SquatRepetition[];
  explanation?: SquatCaseExplanation | null;
};

const eventLabels = {
  inicio_descenso: "Inicio",
  maxima_profundidad: "Profundidad",
  final_ascenso: "Final",
} as const;

export function AnalysisPlayer({
  assetUrl,
  captures,
  posterUrl,
  repetitions,
  explanation,
}: AnalysisPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [activeRepetition, setActiveRepetition] = useState(
    repetitions[0]?.repetition_index ?? 1,
  );
  const [currentTime, setCurrentTime] = useState(0);
  const selectedEvents = captures.filter(
    (capture) => capture.repetition_index === activeRepetition,
  );

  function seek(timestamp: number) {
    if (!videoRef.current) return;
    videoRef.current.currentTime = timestamp;
    void videoRef.current.play();
  }

  return (
    <div>
      <div className="overflow-hidden rounded-xl border bg-slate-950 shadow-sm">
        <video
          ref={videoRef}
          className="aspect-video w-full object-contain"
          controls
          poster={posterUrl}
          preload="metadata"
          src={assetUrl}
          onTimeUpdate={(event) =>
            setCurrentTime(event.currentTarget.currentTime)
          }
        >
          Tu navegador no admite la reproducción de video.
        </video>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className="mr-1 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          Repetición
        </span>
        {repetitions.map((repetition) => (
          <Button
            key={repetition.repetition_index}
            size="sm"
            variant={
              activeRepetition === repetition.repetition_index
                ? "default"
                : "outline"
            }
            onClick={() => {
              setActiveRepetition(repetition.repetition_index);
              seek(repetition.start_seconds);
            }}
          >
            {repetition.repetition_index}
          </Button>
        ))}
      </div>

      <div className="mt-3 grid gap-2 sm:grid-cols-3">
        {selectedEvents.map((capture) => (
          <button
            key={`${capture.repetition_index}-${capture.event}`}
            className="group flex items-center gap-3 rounded-lg border bg-card px-3 py-2 text-left transition-colors hover:border-primary/45 hover:bg-accent/45"
            type="button"
            onClick={() => seek(capture.timestamp_seconds)}
          >
            {capture.event === "maxima_profundidad" ? (
              <LocateFixedIcon
                className="size-4 text-primary"
                aria-hidden="true"
              />
            ) : (
              <CirclePlayIcon
                className="size-4 text-muted-foreground group-hover:text-primary"
                aria-hidden="true"
              />
            )}
            <span>
              <span className="block text-xs font-medium">
                {eventLabels[capture.event]}
              </span>
              <span className="font-mono text-[11px] text-muted-foreground">
                {capture.timestamp_seconds.toFixed(2)} s
              </span>
            </span>
          </button>
        ))}
      </div>

      {explanation ? (
        <ExplanationWorkspace
          activeRepetition={activeRepetition}
          currentTime={currentTime}
          explanation={explanation}
        />
      ) : null}
    </div>
  );
}
