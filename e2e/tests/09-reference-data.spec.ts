import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '09-reference-data';

test.describe('9. Admin Console — Reference Data', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('9.1 Reference Data Lists', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/reference-data', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '9.1-reference-data-list', testInfo);
  });

  test('9.2 Create Reference Entry', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/reference-data', testInfo);
    await waitForSpinner(page);

    const addBtn = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first();
    if (await addBtn.isVisible()) {
      await addBtn.click();
      await waitForAngular(page);
      await snap(page, S, '9.2-create-reference-entry', testInfo);
      await page.keyboard.press('Escape');
    }
  });
});
