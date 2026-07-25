import { expect, type Locator } from "@playwright/test";

export async function expectPlayableVideo(video: Locator) {
  await expect(video).toBeVisible();
  await video.evaluate((element: HTMLVideoElement) => {
    element.muted = true;
    element.load();
  });

  await expect
    .poll(
      () => video.evaluate((element: HTMLVideoElement) => element.readyState),
      { timeout: 30_000 },
    )
    .toBeGreaterThanOrEqual(2);

  const state = await video.evaluate(async (element: HTMLVideoElement) => {
    await element.play();
    const target = Math.min(1, element.duration / 2);
    await new Promise<void>((resolve, reject) => {
      const timeout = window.setTimeout(
        () => reject(new Error("Video seek timed out")),
        10_000,
      );
      element.addEventListener(
        "seeked",
        () => {
          window.clearTimeout(timeout);
          resolve();
        },
        { once: true },
      );
      element.currentTime = target;
    });
    element.pause();
    return {
      currentTime: element.currentTime,
      duration: element.duration,
      error: element.error?.message ?? null,
      readyState: element.readyState,
      videoHeight: element.videoHeight,
      videoWidth: element.videoWidth,
    };
  });
  expect(state.error).toBeNull();
  expect(state.readyState).toBeGreaterThanOrEqual(2);
  expect(state.currentTime).toBeGreaterThan(0);
  expect(state.duration).toBeGreaterThan(0);
  expect(state.videoHeight).toBeGreaterThan(0);
  expect(state.videoWidth).toBeGreaterThan(0);
}
