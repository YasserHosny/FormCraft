import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '03-canvas-editor';

test.describe('3. Design Studio — Canvas Editor', () => {
  let templateId: string;

  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);

    // Get first template ID via API
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    const res = await page.request.get('/api/templates', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const body = await res.json();
    const templates = body.data || body;
    if (templates.length > 0) {
      templateId = templates[0].id;
    }
  });

  test('3.1 Element Palette and Canvas', async ({ page }, testInfo) => {
    if (!templateId) { test.skip(); return; }
    await navigateTo(page, `/designer/${templateId}`, testInfo);
    await page.waitForTimeout(3000); // Canvas rendering
    await snap(page, S, '3.1-canvas-with-palette', testInfo);

    // Click on a palette item to add element
    const paletteItem = page.locator('.palette-item, mat-list-item[draggable="true"]').first();
    if (await paletteItem.isVisible()) {
      await paletteItem.click();
      await waitForAngular(page);
      await page.waitForTimeout(1000);
      await snap(page, S, '3.1-element-added', testInfo);
    }
  });

  test('3.2 Properties Panel', async ({ page }, testInfo) => {
    if (!templateId) { test.skip(); return; }
    await navigateTo(page, `/designer/${templateId}`, testInfo);
    await page.waitForTimeout(3000);

    // Click on canvas to select an element (click center of canvas area)
    const canvas = page.locator('canvas, .konva-stage, .canvas-area').first();
    if (await canvas.isVisible()) {
      const box = await canvas.boundingBox();
      if (box) {
        await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
        await waitForAngular(page);
        await page.waitForTimeout(500);
      }
    }
    await snap(page, S, '3.2-properties-panel', testInfo);
  });

  test('3.3 Toolbar and Status', async ({ page }, testInfo) => {
    if (!templateId) { test.skip(); return; }
    await navigateTo(page, `/designer/${templateId}`, testInfo);
    await page.waitForTimeout(3000);

    // Capture the toolbar with status badge
    await snap(page, S, '3.3-toolbar-status-badge', testInfo);
  });

  test('3.4 Version History Panel', async ({ page }, testInfo) => {
    if (!templateId) { test.skip(); return; }
    await navigateTo(page, `/designer/${templateId}`, testInfo);
    await page.waitForTimeout(3000);

    // Look for version history button/tab
    const versionBtn = page.locator('button:has-text("Version"), button:has-text("الإصدار"), button:has(mat-icon:text("history"))').first();
    if (await versionBtn.isVisible()) {
      await versionBtn.click();
      await waitForAngular(page);
      await snap(page, S, '3.4-version-history', testInfo);
    } else {
      await snap(page, S, '3.4-canvas-no-version-btn', testInfo);
    }
  });

  test('3.5 Feedback Panel', async ({ page }, testInfo) => {
    if (!templateId) { test.skip(); return; }
    await navigateTo(page, `/designer/${templateId}`, testInfo);
    await page.waitForTimeout(3000);

    const feedbackBtn = page.locator('button:has-text("Feedback"), button:has-text("ملاحظات"), button:has(mat-icon:text("feedback"))').first();
    if (await feedbackBtn.isVisible()) {
      await feedbackBtn.click();
      await waitForAngular(page);
      await snap(page, S, '3.5-feedback-panel', testInfo);
    } else {
      await snap(page, S, '3.5-canvas-no-feedback-btn', testInfo);
    }
  });

  test('3.6 Print Settings Panel', async ({ page }, testInfo) => {
    if (!templateId) { test.skip(); return; }
    await navigateTo(page, `/designer/${templateId}`, testInfo);
    await page.waitForTimeout(3000);

    const printBtn = page.locator('button:has-text("Print"), button:has-text("طباعة"), button:has(mat-icon:text("print"))').first();
    if (await printBtn.isVisible()) {
      await printBtn.click();
      await waitForAngular(page);
      await snap(page, S, '3.6-print-settings', testInfo);
    } else {
      await snap(page, S, '3.6-canvas-no-print-btn', testInfo);
    }
  });
});
