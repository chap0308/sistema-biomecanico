import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AnalysisPlayer } from "./analysis-player";

describe("AnalysisPlayer", () => {
  it("pauses the video at maximum depth for visual inspection", () => {
    const pause = vi
      .spyOn(HTMLMediaElement.prototype, "pause")
      .mockImplementation(() => undefined);

    render(
      <AnalysisPlayer
        assetUrl="/overlay.mp4"
        captures={[
          {
            repetition_index: 1,
            event: "maxima_profundidad",
            frame_index: 30,
            timestamp_seconds: 1.25,
            relative_path: "captures/peak.jpg",
          },
        ]}
        repetitions={[
          {
            repetition_index: 1,
            start_frame: 0,
            peak_depth_frame: 30,
            end_frame: 60,
            start_seconds: 0,
            peak_depth_seconds: 1.25,
            end_seconds: 2.5,
            descent_duration_seconds: 1.25,
            ascent_duration_seconds: 1.25,
            total_duration_seconds: 2.5,
            peak_hip_midpoint_y: 0.7,
            valid_frames_percentage: 100,
          },
        ]}
      />,
    );

    const video = document.querySelector("video");
    expect(video).not.toBeNull();

    fireEvent.click(screen.getByRole("button", { name: /profundidad/i }));

    expect(video?.currentTime).toBe(1.25);
    expect(pause).toHaveBeenCalledOnce();
    pause.mockRestore();
  });
});
