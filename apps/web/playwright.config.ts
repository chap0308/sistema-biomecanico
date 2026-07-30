import { defineConfig, devices } from "@playwright/test";

const hasAuthenticatedTests = Boolean(
  process.env.SQUAT_E2E_EMAIL && process.env.SQUAT_E2E_PASSWORD,
);
const hasExpertTests = Boolean(
  process.env.SQUAT_E2E_EXPERT_EMAIL &&
    process.env.SQUAT_E2E_EXPERT_PASSWORD &&
    process.env.SQUAT_E2E_EXPERT_ASSIGNMENT_ID,
);
const recordVideo = process.env.SQUAT_E2E_RECORD_VIDEO === "1";
const demoMode = process.env.SQUAT_E2E_DEMO === "1";

export default defineConfig({
  testDir: "./e2e",
  timeout: 90_000,
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  reporter: "html",
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "on-first-retry",
    video: recordVideo || demoMode ? "on" : "retain-on-failure",
    launchOptions: demoMode ? { slowMo: 350 } : undefined,
  },
  webServer: {
    command: "npm run dev",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    {
      name: "chromium-public",
      testMatch: /home\.spec\.ts/,
      use: { ...devices["Desktop Chrome"] },
    },
    ...(hasAuthenticatedTests
      ? [
          {
            name: "auth-setup",
            testMatch: /(^|[\\/])auth\.setup\.ts$/,
          },
          {
            name: "chromium-authenticated",
            dependencies: ["auth-setup"],
            testMatch: [
              /auth\.spec\.ts/,
              /case-intake\.spec\.ts/,
              /case-analysis\.spec\.ts/,
              /case-results\.spec\.ts/,
              /case-comparison\.spec\.ts/,
              /case-assignments\.spec\.ts/,
              /responsive-accessibility\.spec\.ts/,
            ],
            use: {
              ...devices["Desktop Chrome"],
              storageState: "playwright/.auth/investigator.json",
            },
          },
        ]
      : []),
    ...(hasExpertTests
      ? [
          {
            name: "expert-auth-setup",
            testMatch: /(^|[\\/])expert-auth\.setup\.ts$/,
          },
          {
            name: "chromium-expert",
            dependencies: ["expert-auth-setup"],
            testMatch: /expert-evaluation\.spec\.ts/,
            use: {
              ...devices["Desktop Chrome"],
              storageState: "playwright/.auth/expert.json",
            },
          },
        ]
      : []),
  ],
});
