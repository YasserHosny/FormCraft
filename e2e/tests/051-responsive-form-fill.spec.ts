import { test, expect } from '@playwright/test';
import { login, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const viewports = [
  { name: 'phone', width: 360, height: 740 },
  { name: 'tablet', width: 768, height: 1024 },
];

test.describe('51. Responsive Form Fill', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  for (const viewport of viewports) {
    test(`form filling surface fits ${viewport.name}`, async ({ page }, testInfo) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await navigateTo(page, '/desk', testInfo);
      await waitForSpinner(page);

      const token = await page.evaluate(() => localStorage.getItem('access_token'));
      const res = await page.request.get('/api/templates', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const body = await res.json();
      const templates = body.data || body;
      test.skip(!templates.length, 'No templates available for responsive form-fill scenario');

      await navigateTo(page, `/desk/fill/${templates[0].id}`, testInfo);
      await waitForSpinner(page);
      await waitForAngular(page);

      await expect(page.locator('body')).toBeVisible();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
      expect(overflow).toBeFalsy();

      const submit = page.locator('button:has-text("إرسال"), button:has-text("Submit")').last();
      if (await submit.isVisible()) {
        await submit.click();
        await waitForAngular(page);
        const firstInvalidTop = await page.evaluate(() => {
          const invalid = document.querySelector('.ng-invalid, [aria-invalid="true"]');
          return invalid?.getBoundingClientRect().top ?? null;
        });
        expect(firstInvalidTop === null || (firstInvalidTop >= 0 && firstInvalidTop <= viewport.height)).toBeTruthy();
      }
    });
  }
});
