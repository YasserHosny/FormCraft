import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '08-template-governance';

test.describe('8. Admin Console — Template Governance', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('8.1 Template Governance List', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/templates', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '8.1-governance-list', testInfo);

    // Try status filter
    const statusSelect = page.locator('mat-select').first();
    if (await statusSelect.isVisible()) {
      await statusSelect.click();
      await waitForAngular(page);
      await snap(page, S, '8.1-status-filter-open', testInfo);
      await page.keyboard.press('Escape');
    }
  });

  test('8.2 Review Queue', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/reviews', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '8.2-review-queue', testInfo);

    // Capture filter bar
    const filterBar = page.locator('.filter-bar').first();
    if (await filterBar.isVisible()) {
      await snap(page, S, '8.2-review-queue-filters', testInfo);
    }
  });

  test('8.3 Governance Dashboard', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/governance', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '8.3-governance-dashboard', testInfo);

    // Capture metric cards
    const metricCards = page.locator('.metric-card, mat-card');
    const count = await metricCards.count();
    if (count > 0) {
      await snap(page, S, '8.3-governance-metrics', testInfo);
    }
  });

  test('8.4 Template Feedback Overview', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/template-feedback', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '8.4-template-feedback-overview', testInfo);
  });
});
