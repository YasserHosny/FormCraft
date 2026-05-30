import { test, expect } from '@playwright/test';
import { login, snap, navigateTo, waitForAngular, waitForSpinner } from './helpers';

const S = '05-customers';

test.describe('5. Form Desk — Customers', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    await login(page, testInfo);
  });

  test('5.1 Customer List', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk/customers', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '5.1-customer-list', testInfo);
  });

  test('5.2 Create New Customer', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk/customers/new', testInfo);
    await waitForSpinner(page);
    await snap(page, S, '5.2-new-customer-form-empty', testInfo);

    // Fill the form
    const nameAr = page.locator('input[name="name_ar"]').first();
    if (await nameAr.isVisible()) {
      await nameAr.fill('أحمد محمد');
    }

    const nameEn = page.locator('input[name="name_en"]').first();
    if (await nameEn.isVisible()) {
      await nameEn.fill('Ahmed Mohamed');
    }

    const identifier = page.locator('input[name="identifier"]').first();
    if (await identifier.isVisible()) {
      await identifier.fill('29001011234567');
    }

    const phone = page.locator('input[name="contact_phone"]').first();
    if (await phone.isVisible()) {
      await phone.fill('+201001234567');
    }

    const email = page.locator('input[name="contact_email"]').first();
    if (await email.isVisible()) {
      await email.fill('ahmed@example.com');
    }

    await snap(page, S, '5.2-new-customer-form-filled', testInfo);
  });

  test('5.3 Customer Search', async ({ page }, testInfo) => {
    await navigateTo(page, '/desk/customers', testInfo);
    await waitForSpinner(page);

    const searchInput = page.locator('input[matinput], input[placeholder*="Search"]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('Ahmed');
      await waitForAngular(page);
      await snap(page, S, '5.3-customer-search-results', testInfo);
    }
  });
});
