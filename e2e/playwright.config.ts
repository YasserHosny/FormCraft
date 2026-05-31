import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  outputDir: './test-results',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: [['html', { open: 'never', outputFolder: './report' }]],
  use: {
    baseURL: 'http://localhost:80',
    screenshot: 'off',
    video: 'off',
    trace: 'off',
    headless: true,
    viewport: { width: 1440, height: 900 },
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
  },
  projects: [
    {
      name: 'classic',
      use: {
        browserName: 'chromium',
        executablePath: '/usr/bin/google-chrome',
        launchArgs: ['--no-sandbox', '--disable-gpu'],
      },
    },
    {
      name: 'new-theme',
      use: {
        browserName: 'chromium',
        executablePath: '/usr/bin/google-chrome',
        launchArgs: ['--no-sandbox', '--disable-gpu'],
      },
    },
  ],
});
