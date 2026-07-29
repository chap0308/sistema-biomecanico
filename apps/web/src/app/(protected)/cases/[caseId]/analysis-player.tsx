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
  technicalAssetUrl?: string;
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
  technicalAssetUrl,
}: AnalysisPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const preservedTimeRef = useRef(0);
  const restoringSourceRef = useRef(false);
  const [activeRepetition, setActiveRepetition] = useState(
    repetitions[0]?.repetition_index ?? 1,
  );
  const [currentTime, setCurrentTime] = useState(0);
  const [videoMode, setVideoMode] = useState<"pose" | "technical">("pose");
  const selectedEvents = captures.filter(
    (capture) => capture.repetition_index === activeRepetition,
  );

  function seek(timestamp: number, autoplay = true) {
    if (!videoRef.current) return;
    videoRef.current.currentTime = timestamp;
    preservedTimeRef.current = timestamp;
    setCurrentTime(timestamp);
    if (autoplay) {
      void videoRef.current.play();
      return;
    }
    videoRef.current.pause();
  }

  function selectRepetition(repetitionIndex: number, autoplay: boolean) {
    const repetition = repetitions.find(
      (item) => item.repetition_index === repetitionIndex,
    );
    if (!repetition) return;
    setActiveRepetition(repetitionIndex);
    seek(repetition.start_seconds, autoplay);
  }

  function synchronizeRepetition(timestamp: number) {
    if (repetitions[0] && timestamp < repetitions[0].start_seconds) {
      setActiveRepetition(repetitions[0].repetition_index);
      return;
    }
    for (let index = repetitions.length - 1; index >= 0; index -= 1) {
      if (timestamp >= repetitions[index].start_seconds) {
        setActiveRepetition(repetitions[index].repetition_index);
        return;
      }
    }
  }

  function changeVideoMode(mode: "pose" | "technical") {
    preservedTimeRef.current = videoRef.current?.currentTime ?? currentTime;
    restoringSourceRef.current = true;
    setVideoMode(mode);
  }

  return (
    <div>
      {technicalAssetUrl ? (
        <div className="mb-3 flex flex-wrap gap-2">
          <Button
            size="sm"
            variant={videoMode === "pose" ? "default" : "outline"}
            onClick={() => changeVideoMode("pose")}
          >
            Overlay de pose
          </Button>
          <Button
            size="sm"
            variant={videoMode === "technical" ? "default" : "outline"}
            onClick={() => changeVideoMode("technical")}
          >
            Overlay técnico
          </Button>
        </div>
      ) : null}
      <div className="overflow-hidden rounded-xl border bg-slate-950 shadow-sm">
        <video
          ref={videoRef}
          className="aspect-video w-full object-contain"
          controls
          poster={posterUrl}
          preload="metadata"
          src={
            videoMode === "technical" && technicalAssetUrl
              ? technicalAssetUrl
              : assetUrl
          }
          onLoadedMetadata={(event) => {
            event.currentTarget.currentTime = preservedTimeRef.current;
            setCurrentTime(preservedTimeRef.current);
            restoringSourceRef.current = false;
          }}
          onTimeUpdate={(event) => {
            if (restoringSourceRef.current) return;
            const timestamp = event.currentTarget.currentTime;
            preservedTimeRef.current = timestamp;
            setCurrentTime(timestamp);
            synchronizeRepetition(timestamp);
          }}
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
            aria-pressed={
              activeRepetition === repetition.repetition_index
            }
            onClick={() => {
              selectRepetition(repetition.repetition_index, true);
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
            onClick={() =>
              seek(
                capture.timestamp_seconds,
                capture.event !== "maxima_profundidad",
              )
            }
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
          onRepetitionChange={(repetitionIndex) =>
            selectRepetition(repetitionIndex, false)
          }
        />
      ) : null}
    </div>
  );
}
