import { test, expect } from '@playwright/test';
import { isNewTheme, login, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const viewports = [
  { name: 'phone', width: 360, height: 740 },
  { name: 'tablet', width: 768, height: 1024 },
];

const languages = [
  { name: 'rtl', lang: 'ar', dir: 'rtl' },
  { name: 'ltr', lang: 'en', dir: 'ltr' },
];

test.describe('51. Responsive New Theme Shell', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    test.skip(!isNewTheme(testInfo), 'New shell responsive checks run only in the new-theme project');
    await login(page, testInfo);
  });

  for (const viewport of viewports) {
    for (const language of languages) {
      test(`new shell adapts at ${viewport.name} in ${language.name}`, async ({ page }, testInfo) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.evaluate((lang) => localStorage.setItem('formcraft_language', lang), language.lang);
        await page.reload();
        await waitForAngular(page);
        await navigateTo(page, '/desk', testInfo);
        await waitForSpinner(page);

        await expect(page.locator('.layout-wrapper')).toHaveAttribute('dir', language.dir);
        await expect(page.locator('.fc-menu-btn')).toBeVisible();
        await expect(page.locator('.fc-toolbar-search-wrap')).toBeHidden();

        if (viewport.name === 'phone') {
          const sidebar = page.locator('.fc-sidebar');
          await expect(sidebar).not.toHaveClass(/open/);

          await page.locator('.fc-menu-btn').click();
          await expect(sidebar).toHaveClass(/open/);
          await expect(page.locator('.fc-sidebar-backdrop')).toHaveClass(/open/);

          await page.keyboard.press('Escape');
          await expect(sidebar).not.toHaveClass(/open/);

          await page.locator('.fc-menu-btn').click();
          await page.locator('.fc-sidebar-backdrop').click();
          await expect(sidebar).not.toHaveClass(/open/);
        } else {
          await expect(page.locator('.fc-sidebar')).toBeVisible();
          await expect(page.locator('.fc-side-link').first()).toBeVisible();
        }
      });
    }
  }

  test('language switch remains reachable from the drawer', async ({ page }, testInfo) => {
    await page.setViewportSize({ width: 360, height: 740 });
    await navigateTo(page, '/desk', testInfo);
    await waitForSpinner(page);

    await page.locator('.fc-menu-btn').click();
    await page.locator('.sidebar-footer').click();
    await waitForAngular(page);

    await expect(page.locator('.layout-wrapper')).toHaveAttribute('dir', /^(rtl|ltr)$/);
    await expect(page.locator('.fc-sidebar')).not.toHaveClass(/open/);
  });
});
