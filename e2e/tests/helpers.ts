import { Page, TestInfo, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// ── Credentials ──────────────────────────────────────────────
export const ADMIN_USER = {
  email: 'yasser2006_6@yahoo.com',
  password: 'FormCraft@2026',
};

// ── Theme helpers ───────────────────────────────────────────
export function isNewTheme(testInfo: TestInfo): boolean {
  return testInfo.project.name === 'new-theme';
}

const CLASSIC_TO_NEW: [RegExp, string][] = [
  [/^\/templates\/new$/, '/ui/studio/wizard'],
  [/^\/templates$/, '/ui/studio/templates'],
  [/^\/designer\/(.+)$/, '/ui/studio/designer/$1'],
  [/^\/desk\/fill\/(.+)$/, '/ui/desk/fill/$1'],
  [/^\/desk\/customers\/new$/, '/ui/desk/customers/new'],
  [/^\/desk\/customers\/(.+)$/, '/ui/desk/customers/$1'],
  [/^\/desk\/customers$/, '/ui/desk/customers'],
  [/^\/desk\/history$/, '/ui/desk/history'],
  [/^\/desk\/queue\/new$/, '/ui/desk/queue/new'],
  [/^\/desk\/queue$/, '/ui/desk/queue'],
  [/^\/desk$/, '/ui/desk'],
  [/^\/admin\/analytics$/, '/ui/admin/analytics'],
  [/^\/admin\/reviews$/, '/ui/admin/reviews'],
  [/^\/admin\/governance$/, '/ui/admin/governance'],
  [/^\/admin\/settings$/, '/ui/admin/settings'],
  [/^\/admin\/users$/, '/ui/admin/users'],
  [/^\/admin\/departments$/, '/ui/admin/departments'],
  [/^\/admin\/(.+)$/, '/ui/admin/$1'],
  [/^\/analytics\/(.+)$/, '/ui/admin/analytics'],
  [/^\/reports\/(.+)$/, '/ui/admin/$1'],
  [/^\/feedback$/, '/ui/desk'],
  [/^\/marketplace\/(.+)$/, '/ui/studio/templates'],
  [/^\/marketplace$/, '/ui/studio/templates'],
  [/^\/digital-signatures\/(.+)$/, '/ui/desk'],
  [/^\/digital-signatures$/, '/ui/desk'],
  [/^\/notifications$/, '/ui/desk'],
  [/^\/platform\/(.+)$/, '/platform/$1'],
  [/^\/platform$/, '/platform'],
];

function mapRoute(classicPath: string): string {
  for (const [pattern, replacement] of CLASSIC_TO_NEW) {
    if (pattern.test(classicPath)) {
      return classicPath.replace(pattern, replacement);
    }
  }
  return '/ui/studio/templates';
}

// ── Screenshot output ────────────────────────────────────────
const SCREENSHOT_ROOT = path.resolve(__dirname, '..', 'screenshots');

function screenshotDir(section: string, theme: string): string {
  const dir = path.join(SCREENSHOT_ROOT, theme, section);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

export async function snap(
  page: Page,
  section: string,
  name: string,
  testInfo?: TestInfo,
): Promise<void> {
  const theme = testInfo?.project.name === 'new-theme' ? 'new-theme' : 'classic';
  const dir = screenshotDir(section, theme);
  const file = path.join(dir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
}

// ── Angular Router helper ───────────────────────────────────
// page.goto() causes a full page reload which breaks Angular's
// in-memory auth state (loadProfile() fails synchronously during
// the AuthService constructor due to HTTP pipeline timing).
// Instead we use Angular's client-side Router for navigation.

async function exposeAngularRouter(page: Page): Promise<void> {
  const hasRouter = await page.evaluate(() => !!(window as any).__pw_router);
  if (hasRouter) return;

  await page.evaluate(() => {
    const ng = (window as any).ng;
    if (!ng) return;
    const outlet = document.querySelector('router-outlet');
    if (!outlet) return;
    const directives = ng.getDirectives(outlet);
    const outletDir = directives?.[0];
    const rootInjector = outletDir?.parentContexts?.rootInjector;
    if (!rootInjector?.records) return;

    rootInjector.records.forEach((_: any, key: any) => {
      if (key?.name === '_Router') {
        try {
          const inst = rootInjector.get(key);
          if (inst && typeof inst.navigate === 'function') {
            (window as any).__pw_router = inst;
          }
        } catch {}
      }
    });
  });
}

async function angularNavigate(page: Page, routePath: string): Promise<void> {
  await exposeAngularRouter(page);

  const segments = routePath.split('/').filter(Boolean);

  await page.evaluate(async (segs: string[]) => {
    const router = (window as any).__pw_router;
    if (!router) throw new Error('Angular Router not found');
    await router.navigate(['/' + segs.join('/')]);
  }, segments);
}

// ── Auth helpers ─────────────────────────────────────────────

export async function login(
  page: Page,
  credsOrTestInfo?: typeof ADMIN_USER | TestInfo,
  testInfo?: TestInfo,
): Promise<void> {
  let creds = ADMIN_USER;
  let info: TestInfo | undefined;

  if (credsOrTestInfo && 'project' in credsOrTestInfo) {
    info = credsOrTestInfo;
  } else if (credsOrTestInfo) {
    creds = credsOrTestInfo as typeof ADMIN_USER;
    info = testInfo;
  }

  await page.goto('/auth/login');
  await page.waitForLoadState('networkidle');

  if (info && isNewTheme(info)) {
    await page.evaluate(() => {
      localStorage.setItem('fc_theme_preference', 'new');
    });
  }

  const emailInput = page.locator('input[type="email"], input[formcontrolname="email"], input[name="email"]').first();
  const passwordInput = page.locator('input[type="password"]').first();

  await emailInput.waitFor({ state: 'visible', timeout: 15_000 });
  await emailInput.fill(creds.email);
  await passwordInput.fill(creds.password);

  await page.locator('button[type="submit"], button:has-text("Login"), button:has-text("تسجيل")').first().click();

  await page.waitForURL((url) => !url.pathname.includes('/auth/login'), {
    timeout: 20_000,
  });
  await page.waitForLoadState('networkidle');
}

// Wait for Angular to settle after navigation
export async function waitForAngular(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);
}

// Navigate using Angular's client-side router.
// Maps routes when running under new-theme project.
export async function navigateTo(
  page: Page,
  routePath: string,
  testInfo?: TestInfo,
): Promise<void> {
  const target = testInfo && isNewTheme(testInfo) ? mapRoute(routePath) : routePath;
  await angularNavigate(page, target);
  await waitForAngular(page);
}

// Wait for a Material spinner to disappear
export async function waitForSpinner(page: Page): Promise<void> {
  const spinner = page.locator('mat-spinner, mat-progress-spinner, mat-progress-bar');
  if (await spinner.count() > 0) {
    await spinner.first().waitFor({ state: 'hidden', timeout: 30_000 }).catch(() => {});
  }
}
