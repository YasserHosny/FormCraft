import { test, expect } from '@playwright/test';
import { login, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const directions = [
  { lang: 'ar', dir: 'rtl' },
  { lang: 'en', dir: 'ltr' },
];

test.describe('51. Responsive RTL/LTR', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
    await page.setViewportSize({ width: 360, height: 740 });
  });

  for (const direction of directions) {
    test(`mobile shell and data views align in ${direction.dir}`, async ({ page }, testInfo) => {
      await page.evaluate((lang) => localStorage.setItem('formcraft_language', lang), direction.lang);
      await page.reload();
      await waitForAngular(page);
      await navigateTo(page, '/desk', testInfo);
      await waitForSpinner(page);

      const actualDir = await page.locator('[dir]').first().getAttribute('dir');
      expect(actualDir || await page.evaluate(() => document.documentElement.dir)).toBe(direction.dir);

      const pageOverflows = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
      expect(pageOverflows).toBeFalsy();
    });
  }

  test('language switch recalculates mobile direction without reload', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk', testInfo);
    await waitForSpinner(page);

    const before = await page.locator('[dir]').first().getAttribute('dir');
    await page.locator('button[mat-icon-button]').filter({ hasText: 'account_circle' }).click();
    await page.locator('button[mat-menu-item]').filter({ hasText: /English|العربية/ }).click();
    await waitForAngular(page);
    const after = await page.locator('[dir]').first().getAttribute('dir');

    expect(after).not.toBe(before);
  });
});
