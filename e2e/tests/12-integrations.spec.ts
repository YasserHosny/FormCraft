import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '12-integrations';

test.describe('12. Admin Console — Integrations', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('12.1 API Credentials', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/integrations', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '12.1-api-credentials', testInfo);
  });

  test('12.2 Webhooks', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/webhooks', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '12.2-webhooks', testInfo);
  });
});
