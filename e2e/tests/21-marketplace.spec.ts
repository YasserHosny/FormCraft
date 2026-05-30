import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '21-marketplace';

test.describe('21. Template Marketplace', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('21.1 Browse Marketplace', async ({ page }, testInfo) => {
    await navigateTo(page, '/marketplace', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '21.1-marketplace-browse', testInfo);
  });

  test('21.2 Marketplace Filters', async ({ page }, testInfo) => {
    await navigateTo(page, '/marketplace', testInfo);
    await waitForSpinner(page);

    const searchInput = page.locator('input[matinput], input[placeholder*="Search"]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('form');
      await waitForAngular(page);
      await snap(page, S, '21.2-marketplace-search', testInfo);
    }
  });

  test('21.3 Publish to Marketplace', async ({ page }, testInfo) => {
    await navigateTo(page, '/marketplace/publish', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '21.3-marketplace-publish', testInfo);
  });
});
