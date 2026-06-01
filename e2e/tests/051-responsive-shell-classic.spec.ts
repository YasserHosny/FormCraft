import { test, expect } from '@playwright/test';
import { isNewTheme, login, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const viewports = [
  { name: 'phone', width: 360, height: 740 },
  { name: 'tablet', width: 768, height: 1024 },
];

const languages = [
  { name: 'rtl', lang: 'ar' },
  { name: 'ltr', lang: 'en' },
];

test.describe('51. Responsive Classic Shell', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    test.skip(isNewTheme(testInfo), 'Classic shell responsive checks run only in the classic project');
    await login(page, testInfo);
  });

  for (const viewport of viewports) {
    for (const language of languages) {
      test(`classic shell adapts at ${viewport.name} in ${language.name}`, async ({ page }, testInfo) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.evaluate((lang) => localStorage.setItem('formcraft_language', lang), language.lang);
        await page.reload();
        await waitForAngular(page);
        await navigateTo(page, '/desk', testInfo);
        await waitForSpinner(page);

        await expect(page.locator('.mobile-menu-button')).toBeVisible();
        await expect(page.locator('.global-search-bar')).toBeHidden();

        if (viewport.name === 'phone') {
          const drawer = page.locator('.mobile-mode-drawer');
          await page.locator('.mobile-menu-button').click();
          await expect(drawer).toHaveClass(/open/);
          await expect(page.locator('.drawer-mode-tab').first()).toBeVisible();

          await page.keyboard.press('Escape');
          await expect(drawer).not.toHaveClass(/open/);

          await page.locator('.mobile-menu-button').click();
          await page.locator('.mobile-drawer-backdrop').click();
          await expect(drawer).not.toHaveClass(/open/);
        } else {
          await expect(page.locator('.mode-tabs')).toBeVisible();
          await expect(page.locator('.mode-tab-label').first()).toBeHidden();
        }
      });
    }
  }

  test('profile and language controls remain reachable on phone', async ({ page }, testInfo) => {
    await page.setViewportSize({ width: 360, height: 740 });
    await navigateTo(page, '/desk', testInfo);
    await waitForSpinner(page);

    await page.locator('button[mat-icon-button]').filter({ hasText: 'account_circle' }).click();
    await expect(page.locator('.mat-mdc-menu-panel')).toBeVisible();
    await page.locator('button[mat-menu-item]').filter({ hasText: /English|العربية/ }).click();
    await waitForAngular(page);
  });
});
