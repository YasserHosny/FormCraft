import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '15-retention';

test.describe('15. Data Retention', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('15.1 Retention Policies', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/retention/policies', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '15.1-retention-policies', testInfo);
  });

  test('15.2 Retention Jobs', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/retention/jobs', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '15.2-retention-jobs', testInfo);
  });

  test('15.3 Legal Holds', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/retention/legal-holds', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '15.3-legal-holds', testInfo);
  });

  test('15.4 Disposal Manifests', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/retention/manifests', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '15.4-disposal-manifests', testInfo);
  });
});
