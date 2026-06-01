import { test, expect } from '@playwright/test';
import { login, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const viewports = [
  { name: 'phone', width: 360, height: 740 },
  { name: 'tablet', width: 768, height: 1024 },
];

const routes = [
  { name: 'dashboard', path: '/desk' },
  { name: 'history', path: '/desk/history' },
  { name: 'customers', path: '/desk/customers' },
];

test.describe('51. Responsive Data Views', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  for (const viewport of viewports) {
    for (const route of routes) {
      test(`${route.name} has no page overflow at ${viewport.name}`, async ({ page }, testInfo) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await navigateTo(page, route.path, testInfo);
        await waitForSpinner(page);
        await waitForAngular(page);

        await expect(page.locator('body')).toBeVisible();
        const pageOverflows = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
        expect(pageOverflows).toBeFalsy();
      });
    }
  }
});
