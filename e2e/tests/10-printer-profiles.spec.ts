import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '10-printer-profiles';

test.describe('10. Admin Console — Printer Profiles', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('10.1 Printer Profile List', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/printer-profiles', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '10.1-printer-profile-list', testInfo);
  });

  test('10.2 Create Printer Profile', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/printer-profiles/new', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '10.2-create-printer-profile', testInfo);
  });
});
