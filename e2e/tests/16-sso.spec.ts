import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '16-sso';

test.describe('16. SSO Configuration', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('16.1 IdP Configuration', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/sso', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '16.1-idp-config', testInfo);
  });

  test('16.2 Domain Verification', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/sso/domains', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '16.2-domain-verification', testInfo);
  });

  test('16.3 Attribute Mappings', async ({ page }, testInfo) => {
    await navigateTo(page, '/admin/sso/mappings', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '16.3-attribute-mappings', testInfo);
  });
});
