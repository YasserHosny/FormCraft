import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '17-ocr-onboarding';

test.describe('17. OCR Onboarding', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('17.1 Batch OCR List', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/ocr-onboarding', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '17.1-batch-ocr-list', testInfo);
  });

  test('17.2 Create OCR Batch', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/ocr-onboarding/new', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '17.2-create-ocr-batch', testInfo);
  });
});
