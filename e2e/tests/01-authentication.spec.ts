import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, ADMIN_USER } from './helpers';

const S = '01-authentication';

test.describe('1. Authentication & Access', () => {
  test('1.1 User Login', async ({ page }, testInfo) => {
    await page.goto('/auth/login');
    await page.waitForLoadState('networkidle');
    await snap(page, S, '1.1-login-page', testInfo);

    await login(page, testInfo);
    await snap(page, S, '1.1-after-login-dashboard', testInfo);
  });

  test('1.2 Language Toggle', async ({ page }, testInfo) => {
    await login(page, testInfo);

    // Find language toggle button
    const langToggle = page.locator('button:has(mat-icon:text("language")), button:has-text("EN"), button:has-text("AR"), [mattooltip*="language" i], [mattooltip*="اللغة"]').first();

    if (await langToggle.isVisible()) {
      await snap(page, S, '1.2-before-toggle', testInfo);
      await langToggle.click();
      await waitForAngular(page);
      await snap(page, S, '1.2-after-toggle', testInfo);

      // Toggle back
      const langToggle2 = page.locator('button:has(mat-icon:text("language")), button:has-text("EN"), button:has-text("AR")').first();
      if (await langToggle2.isVisible()) {
        await langToggle2.click();
        await waitForAngular(page);
      }
    } else {
      await snap(page, S, '1.2-no-toggle-found', testInfo);
    }
  });

  test('1.3 User Profile', async ({ page }, testInfo) => {
    await login(page, testInfo);
    await navigateTo(page, '/auth/profile', testInfo);
    await snap(page, S, '1.3-profile-page', testInfo);
  });
});
