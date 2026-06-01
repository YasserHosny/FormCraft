import { test, expect } from '@playwright/test';
import { login, navigateTo, waitForAngular, waitForSpinner } from './helpers';

test.describe('51. Responsive Edge Cases', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
    await page.setViewportSize({ width: 360, height: 640 });
  });

  test('theme switching on mobile lands on a safe route', async ({ page }, testInfo) => {
    await navigateTo(page, '/designer/demo', testInfo);
    await waitForAngular(page);

    const themeSwitch = page.locator('.theme-switch-link, .fc-theme-switch').first();
    if (await themeSwitch.isVisible()) {
      await themeSwitch.click();
      await waitForAngular(page);
      await expect(page).not.toHaveURL(/designer/);
    }
  });

  test('long labels expose title text and orientation changes do not overflow', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk', testInfo);
    await waitForSpinner(page);

    const titledNav = page.locator('[title]').first();
    await expect(titledNav).toBeVisible();

    await page.setViewportSize({ width: 640, height: 360 });
    await waitForAngular(page);
    await page.setViewportSize({ width: 360, height: 640 });
    await waitForAngular(page);

    const pageOverflows = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    expect(pageOverflows).toBeFalsy();
  });
});
