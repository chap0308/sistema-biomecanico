"use client";

import { useRef } from "react";

import { Button } from "@/components/ui/button";
import type { ExpertRepetition } from "@/types/squat-expert";

type ExpertReviewPlayerProps = {
  assignmentId: string;
  repetitions?: ExpertRepetition[];
};

export function ExpertReviewPlayer({
  assignmentId,
  repetitions = [],
}: ExpertReviewPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  function playRepetition(repetition: ExpertRepetition) {
    const video = videoRef.current;
    if (!video) {
      return;
    }
    video.currentTime = repetition.start_seconds;
    void video.play();
  }

  return (
    <div className="space-y-3">
      <div className="overflow-hidden rounded-xl border bg-slate-950">
        <video
          ref={videoRef}
          className="aspect-video w-full object-contain"
          controls
          preload="metadata"
          src={`/api/squat/expert/assignments/${assignmentId}/video`}
        >
          Tu navegador no admite la reproducción de video.
        </video>
      </div>
      {repetitions.length > 0 ? (
        <div className="flex flex-wrap gap-2" aria-label="Navegar por repeticiones">
          {repetitions.map((repetition) => (
            <Button
              key={repetition.repetition_index}
              type="button"
              variant="outline"
              size="sm"
              onClick={() => playRepetition(repetition)}
            >
              Repetición {repetition.repetition_index}
            </Button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
