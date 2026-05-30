import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '11-data-export';

test.describe('11. Admin Console — Data Export', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('11.1 Export Dashboard', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/data-export', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '11.1-export-dashboard', testInfo);
  });

  test('11.2 Export Schedules', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/data-export/schedules', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '11.2-export-schedules', testInfo);
  });
});
