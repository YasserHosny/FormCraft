import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '22-digital-signatures';

test.describe('22. Digital Signatures', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('22.1 Signature Requests', async ({ page }, testInfo) => {
    await navigateTo(page, '/digital-signatures', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '22.1-signature-requests', testInfo);
  });

  test('22.2 Create Signature Request', async ({ page }, testInfo) => {
    await navigateTo(page, '/digital-signatures/new', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '22.2-create-signature-request', testInfo);
  });

  test('22.3 Signature Workflow Config', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/digital-signatures', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '22.3-signature-workflow-config', testInfo);
  });

  test('22.4 Signature Evidence Log', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/digital-signatures/evidence', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '22.4-signature-evidence-log', testInfo);
  });
});
