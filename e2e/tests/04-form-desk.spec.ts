import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '04-form-desk';

test.describe('4. Form Desk — Daily Operations', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('4.1 Operator Dashboard', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '4.1-dashboard', testInfo);

    // Capture search bar area
    const searchInput = page.locator('input[matinput]').first();
    if (await searchInput.isVisible()) {
      await snap(page, S, '4.1-dashboard-search-area', testInfo);
    }
  });

  test('4.2 Dashboard Filters', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk', testInfo);
    await waitForSpinner(page);

    // Try category filter
    const categorySelect = page.locator('mat-select').first();
    if (await categorySelect.isVisible()) {
      await categorySelect.click();
      await waitForAngular(page);
      await snap(page, S, '4.2-filter-dropdown-open', testInfo);
      await page.keyboard.press('Escape');
    }

    // Try search
    const searchInput = page.locator('input[matinput]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('test');
      await waitForAngular(page);
      await snap(page, S, '4.2-search-results', testInfo);

      // Clear
      await searchInput.clear();
      await waitForAngular(page);
    }
  });

  test('4.3 Form Filler', async ({ page }, testInfo) => {
    // Get a template ID that has pages
    const token = await page.evaluate(() => {
      return localStorage.getItem('access_token');
    });

    await navigateTo(page, '/desk', testInfo);
    await waitForSpinner(page);

    // Get first published template, or any template
    const res = await page.request.get('/api/templates', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const body = await res.json();
    const templates = body.data || body;

    if (templates.length === 0) {
      await snap(page, S, '4.3-no-templates', testInfo);
      return;
    }

    const tmpl = templates[0];
    await navigateTo(page, `/desk/fill/${tmpl.id}`, testInfo);
    await waitForSpinner(page);
    await page.waitForTimeout(2000);
    await snap(page, S, '4.3-form-filler-loaded', testInfo);

    // Capture toolbar
    const toolbar = page.locator('fc-form-toolbar, .form-toolbar').first();
    if (await toolbar.isVisible()) {
      await snap(page, S, '4.3-form-toolbar', testInfo);
    }
  });

  test('4.4 Submission History', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk/history', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '4.4-history-list', testInfo);

    // Try filters
    const searchInput = page.locator('input[matinput]').first();
    if (await searchInput.isVisible()) {
      await snap(page, S, '4.4-history-filters', testInfo);
    }

    // Check empty state
    const emptyState = page.locator('.history-empty, :text("No submissions")').first();
    if (await emptyState.isVisible()) {
      await snap(page, S, '4.4-history-empty-state', testInfo);
    }
  });
});
