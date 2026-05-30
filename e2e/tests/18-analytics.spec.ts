import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '18-analytics';

test.describe('18. Analytics', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('18.1 Field Analytics', async ({ page }, testInfo) => {
    await navigateTo(page, '/analytics/fields', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '18.1-field-analytics', testInfo);
  });

  test('18.2 Operator Analytics', async ({ page }, testInfo) => {
    await navigateTo(page, '/analytics/operators', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '18.2-operator-analytics', testInfo);
  });

  test('18.3 Compliance Analytics', async ({ page }, testInfo) => {
    await navigateTo(page, '/analytics/compliance', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '18.3-compliance-analytics', testInfo);
  });

  test('18.4 Template Usage', async ({ page }, testInfo) => {
    await navigateTo(page, '/analytics/template-usage', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '18.4-template-usage', testInfo);
  });
});
