export interface ModeConfig {
  id: 'studio' | 'desk' | 'admin';
  routePrefix: string;
  defaultRoute: string;
  labelKey: string;
  icon: string;
  permittedRoles: string[];
}

export const MODES: ModeConfig[] = [
  {
    id: 'studio',
    routePrefix: '/studio',
    defaultRoute: '/studio/templates',
    labelKey: 'modes.studio',
    icon: 'design_services',
    permittedRoles: ['admin', 'designer'],
  },
  {
    id: 'desk',
    routePrefix: '/desk',
    defaultRoute: '/desk',
    labelKey: 'modes.desk',
    icon: 'assignment',
    permittedRoles: ['admin', 'designer', 'operator', 'viewer'],
  },
  {
    id: 'admin',
    routePrefix: '/admin',
    defaultRoute: '/admin/feedback',
    labelKey: 'modes.admin',
    icon: 'admin_panel_settings',
    permittedRoles: ['admin'],
  },
];

export const ROLE_DEFAULT_MODE: Record<string, string> = {
  admin: 'admin',
  designer: 'studio',
  operator: 'desk',
  viewer: 'desk',
};