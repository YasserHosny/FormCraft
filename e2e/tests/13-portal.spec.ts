import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '13-portal';

test.describe('13. Admin Console — Public Portal', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('13.1 Portal Configuration', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/portal', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '13.1-portal-config', testInfo);
  });

  test('13.2 Portal Forms', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/portal/forms', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '13.2-portal-forms', testInfo);
  });

  test('13.3 Portal Submissions', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/portal/submissions', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '13.3-portal-submissions', testInfo);
  });
});
