import { Injectable } from '@angular/core';

export type ThemeName = 'classic' | 'new';

interface RouteMapping {
  classicPattern: RegExp;
  newPattern: RegExp;
  classicTemplate: string;
  newTemplate: string;
  params: string[];
  productionReady: boolean;
  fallbackClassic: string;
  fallbackNew: string;
}

const ROUTE_MAPPINGS: RouteMapping[] = [
  {
    classicPattern: /^\/templates$/,
    newPattern: /^\/ui\/studio\/templates$/,
    classicTemplate: '/templates',
    newTemplate: '/ui/studio/templates',
    params: [],
    productionReady: true,
    fallbackClassic: '/templates',
    fallbackNew: '/ui/studio/templates',
  },
  {
    classicPattern: /^\/templates\/new$/,
    newPattern: /^\/ui\/studio\/wizard$/,
    classicTemplate: '/templates/new',
    newTemplate: '/ui/studio/wizard',
    params: [],
    productionReady: false,
    fallbackClassic: '/templates',
    fallbackNew: '/ui/studio/templates',
  },
  {
    classicPattern: /^\/designer\/([^/?]+)/,
    newPattern: /^\/ui\/studio\/designer\/([^/?]+)/,
    classicTemplate: '/designer/:pageId',
    newTemplate: '/ui/studio/designer/:pageId',
    params: ['pageId'],
    productionReady: false,
    fallbackClassic: '/templates',
    fallbackNew: '/ui/studio/templates',
  },
  {
    classicPattern: /^\/desk$/,
    newPattern: /^\/ui\/desk$/,
    classicTemplate: '/desk',
    newTemplate: '/ui/desk',
    params: [],
    productionReady: false,
    fallbackClassic: '/desk',
    fallbackNew: '/ui/desk',
  },
  {
    classicPattern: /^\/desk\/fill\/([^/?]+)/,
    newPattern: /^\/ui\/desk\/fill\/([^/?]+)/,
    classicTemplate: '/desk/fill/:templateId',
    newTemplate: '/ui/desk/fill/:templateId',
    params: ['templateId'],
    productionReady: false,
    fallbackClassic: '/desk',
    fallbackNew: '/ui/desk',
  },
  {
    classicPattern: /^\/admin\/analytics/,
    newPattern: /^\/ui\/admin\/analytics/,
    classicTemplate: '/admin/analytics',
    newTemplate: '/ui/admin/analytics',
    params: [],
    productionReady: false,
    fallbackClassic: '/admin/analytics',
    fallbackNew: '/ui/admin/analytics',
  },
  {
    classicPattern: /^\/desk\/customers$/,
    newPattern: /^\/ui\/desk\/customers$/,
    classicTemplate: '/desk/customers',
    newTemplate: '/ui/desk/customers',
    params: [],
    productionReady: false,
    fallbackClassic: '/desk/customers',
    fallbackNew: '/ui/desk/customers',
  },
  {
    classicPattern: /^\/desk\/customers\/([^/?]+)/,
    newPattern: /^\/ui\/desk\/customers\/([^/?]+)/,
    classicTemplate: '/desk/customers/:id',
    newTemplate: '/ui/desk/customers/:id',
    params: ['id'],
    productionReady: false,
    fallbackClassic: '/desk/customers',
    fallbackNew: '/ui/desk/customers',
  },
  {
    classicPattern: /^\/desk\/history/,
    newPattern: /^\/ui\/desk\/history/,
    classicTemplate: '/desk/history',
    newTemplate: '/ui/desk/history',
    params: [],
    productionReady: false,
    fallbackClassic: '/desk',
    fallbackNew: '/ui/desk',
  },
  {
    classicPattern: /^\/admin$/,
    newPattern: /^\/ui\/admin/,
    classicTemplate: '/admin',
    newTemplate: '/ui/admin/analytics',
    params: [],
    productionReady: false,
    fallbackClassic: '/admin',
    fallbackNew: '/ui/admin/analytics',
  },
];

const STORAGE_KEY = 'fc_theme_preference';

@Injectable({ providedIn: 'root' })
export class ThemePreferenceService {
  getPreference(): ThemeName {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'new' ? 'new' : 'classic';
  }

  setPreference(theme: ThemeName): void {
    localStorage.setItem(STORAGE_KEY, theme);
  }

  mapRouteToTheme(currentUrl: string, target: ThemeName, userRole: string): string {
    const urlPath = currentUrl.split('?')[0];

    for (const mapping of ROUTE_MAPPINGS) {
      if (target === 'new') {
        const match = urlPath.match(mapping.classicPattern);
        if (match) {
          if (!mapping.productionReady) {
            return mapping.fallbackNew;
          }
          return this.buildUrl(mapping.newTemplate, mapping.params, match.slice(1));
        }
      } else {
        const match = urlPath.match(mapping.newPattern);
        if (match) {
          return this.buildUrl(mapping.classicTemplate, mapping.params, match.slice(1));
        }
      }
    }

    return this.getDefaultRoute(target, userRole);
  }

  getDefaultRoute(theme: ThemeName, userRole: string): string {
    if (theme === 'new') {
      switch (userRole) {
        case 'operator':
        case 'branch_manager':
          return '/ui/desk';
        default:
          return '/ui/studio/templates';
      }
    }

    switch (userRole) {
      case 'operator':
      case 'branch_manager':
        return '/desk';
      case 'designer':
      case 'admin':
      default:
        return '/templates';
    }
  }

  private buildUrl(template: string, paramNames: string[], values: string[]): string {
    let url = template;
    paramNames.forEach((name, i) => {
      if (values[i]) {
        url = url.replace(`:${name}`, values[i]);
      }
    });
    return url;
  }
}
