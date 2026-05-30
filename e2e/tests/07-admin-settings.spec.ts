import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '07-admin-settings';

test.describe('7. Admin Console — Organization Settings', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('7.1 Organization Settings', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/settings', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '7.1-org-settings', testInfo);
  });

  test('7.2 Departments & Branches', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/departments', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '7.2-departments', testInfo);
  });

  test('7.3 User Management', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/users', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '7.3-user-management', testInfo);
  });

  test('7.4 Invitations', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/invitations', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '7.4-invitations', testInfo);
  });
});
