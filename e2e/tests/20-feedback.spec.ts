import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '20-feedback';

test.describe('20. Feedback', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('20.1 Feedback Widget', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk', testInfo);
    await waitForSpinner(page);

    const feedbackBtn = page.locator('button:has-text("Feedback"), .feedback-fab, [mattooltip*="Feedback"]').first();
    if (await feedbackBtn.isVisible()) {
      await snap(page, S, '20.1-feedback-widget-visible', testInfo);
      await feedbackBtn.click();
      await waitForAngular(page);
      await snap(page, S, '20.1-feedback-widget-open', testInfo);
    } else {
      await snap(page, S, '20.1-no-feedback-widget', testInfo);
    }
  });

  test('20.2 My Feedback', async ({ page }, testInfo) => {
    await navigateTo(page, '/feedback', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '20.2-my-feedback', testInfo);
  });

  test('20.3 Feedback Admin Dashboard', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/feedback', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '20.3-feedback-admin-dashboard', testInfo);
  });
});
