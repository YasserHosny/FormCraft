import { test, expect } from '@playwright/test';
import { isNewTheme, login, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const routes = [
  { name: 'templates', path: '/templates' },
  { name: 'analytics', path: '/admin/analytics' },
  { name: 'profile', path: '/auth/profile' },
];

test.describe('51. Responsive Secondary Pages', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  for (const route of routes) {
    test(`${route.name} fits phone viewport`, async ({ page }, testInfo) => {
      await page.setViewportSize({ width: 360, height: 740 });
      await navigateTo(page, route.path, testInfo);
      await waitForSpinner(page);
      await waitForAngular(page);

      await expect(page.locator('body')).toBeVisible();
      const pageOverflows = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
      expect(pageOverflows).toBeFalsy();
    });
  }

  test('new designer shows mobile unavailable state', async ({ page }, testInfo) => {
    test.skip(!isNewTheme(testInfo), 'Designer mobile guard applies to the new theme designer');
    await page.setViewportSize({ width: 360, height: 740 });
    await navigateTo(page, '/designer/demo', testInfo);
    await waitForAngular(page);

    await expect(page.locator('.mobile-unavailable')).toBeVisible();
  });
});
