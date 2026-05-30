import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '23-batch-schedules';

test.describe('23. Batch Schedules', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('23.1 Schedule List', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/batch-schedules', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '23.1-schedule-list', testInfo);
  });

  test('23.2 Create Schedule', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/batch-schedules/new', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '23.2-create-schedule', testInfo);
  });
});
