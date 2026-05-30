import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '24-notifications';

test.describe('24. Notifications', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('24.1 Notification Bell', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk', testInfo);
    await waitForSpinner(page);

    const bell = page.locator('button[mattooltip*="Notification"], button mat-icon:has-text("notifications"), .notification-bell').first();
    if (await bell.isVisible()) {
      await snap(page, S, '24.1-notification-bell', testInfo);
      await bell.click();
      await waitForAngular(page);
      await snap(page, S, '24.1-notification-dropdown', testInfo);
    } else {
      await snap(page, S, '24.1-no-notification-bell', testInfo);
    }
  });

  test('24.2 Notification List', async ({ page }, testInfo) => {
    await navigateTo(page, '/notifications', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '24.2-notification-list', testInfo);
  });
});
