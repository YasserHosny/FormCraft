import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '06-batch-operations';

test.describe('6. Form Desk — Batch Operations', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('6.1 Batch Queue List', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk/queue', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '6.1-batch-queue-list', testInfo);
  });

  test('6.2 Batch Create Wizard', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk/queue/new', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '6.2-batch-wizard-step1-template', testInfo);
  });
});
