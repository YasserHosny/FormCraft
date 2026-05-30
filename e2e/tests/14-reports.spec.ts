import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '14-reports';

test.describe('14. Reports', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('14.1 Transaction Register', async ({ page }, testInfo) => {
    await navigateTo(page, '/reports/transaction-register', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '14.1-transaction-register', testInfo);
  });

  test('14.2 Reconciliation Report', async ({ page }, testInfo) => {
    await navigateTo(page, '/reports/reconciliation', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '14.2-reconciliation', testInfo);
  });

  test('14.3 Period Summary', async ({ page }, testInfo) => {
    await navigateTo(page, '/reports/period-summary', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '14.3-period-summary', testInfo);
  });

  test('14.4 Beneficiary Report', async ({ page }, testInfo) => {
    await navigateTo(page, '/reports/beneficiary', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '14.4-beneficiary', testInfo);
  });

  test('14.5 Void & Reprint Report', async ({ page }, testInfo) => {
    await navigateTo(page, '/reports/void-reprint', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '14.5-void-reprint', testInfo);
  });

  test('14.6 Signatory Report', async ({ page }, testInfo) => {
    await navigateTo(page, '/reports/signatory', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '14.6-signatory', testInfo);
  });

  test('14.7 Report Builder', async ({ page }, testInfo) => {
    await navigateTo(page, '/reports/builder', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '14.7-report-builder', testInfo);
  });

  test('14.8 Report Schedules', async ({ page }, testInfo) => {
    await navigateTo(page, '/reports/schedules', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '14.8-report-schedules', testInfo);
  });
});
