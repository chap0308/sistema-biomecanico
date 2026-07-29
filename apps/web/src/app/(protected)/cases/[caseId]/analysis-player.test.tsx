import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AnalysisPlayer } from "./analysis-player";

describe("AnalysisPlayer", () => {
  it("pauses the video at maximum depth for visual inspection", () => {
    const pause = vi
      .spyOn(HTMLMediaElement.prototype, "pause")
      .mockImplementation(() => undefined);

    const { container } = render(
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

    const video = container.querySelector("video");
    expect(video).not.toBeNull();

    fireEvent.click(screen.getByRole("button", { name: /profundidad/i }));

    expect(video?.currentTime).toBe(1.25);
    expect(pause).toHaveBeenCalledOnce();
    pause.mockRestore();
  });

  it("synchronizes the active repetition with video time", () => {
    const { container } = render(
      <AnalysisPlayer
        assetUrl="/overlay.mp4"
        captures={[]}
        repetitions={[
          repetition(1, 0, 2),
          repetition(2, 3, 5),
        ]}
      />,
    );

    const video = container.querySelector("video");
    expect(video).not.toBeNull();

    video!.currentTime = 3.2;
    fireEvent.timeUpdate(video!);

    expect(
      screen.getByRole("button", { name: "2", pressed: true }),
    ).toBeInTheDocument();
  });

  it("preserves time when switching between overlay videos", () => {
    const { container } = render(
      <AnalysisPlayer
        assetUrl="/overlay.mp4"
        technicalAssetUrl="/analysis-overlay.mp4"
        captures={[]}
        repetitions={[repetition(1, 0, 5)]}
      />,
    );
    const video = container.querySelector("video");
    expect(video).not.toBeNull();
    video!.currentTime = 3.2;
    fireEvent.timeUpdate(video!);

    fireEvent.click(
      screen.getByRole("button", { name: "Overlay técnico" }),
    );
    video!.currentTime = 0;
    fireEvent.loadedMetadata(video!);

    expect(video?.currentTime).toBe(3.2);
  });
});

function repetition(index: number, start: number, end: number) {
  return {
    repetition_index: index,
    start_frame: start * 30,
    peak_depth_frame: ((start + end) / 2) * 30,
    end_frame: end * 30,
    start_seconds: start,
    peak_depth_seconds: (start + end) / 2,
    end_seconds: end,
    descent_duration_seconds: (end - start) / 2,
    ascent_duration_seconds: (end - start) / 2,
    total_duration_seconds: end - start,
    peak_hip_midpoint_y: 0.7,
    valid_frames_percentage: 100,
  };
}
