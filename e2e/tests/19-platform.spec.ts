import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '19-platform';

test.describe('19. Platform Console', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('19.1 Platform Dashboard', async ({ page }, testInfo) => {
    await navigateTo(page, '/platform', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '19.1-platform-dashboard', testInfo);
  });

  test('19.2 Organization List', async ({ page }, testInfo) => {
    await navigateTo(page, '/platform/organizations', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '19.2-org-list', testInfo);
  });

  test('19.3 Create Organization', async ({ page }, testInfo) => {
    await navigateTo(page, '/platform/organizations/new', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '19.3-create-org', testInfo);
  });
});
