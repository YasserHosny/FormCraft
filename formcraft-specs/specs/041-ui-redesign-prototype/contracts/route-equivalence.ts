/**
 * Route Equivalence Mapper Contract
 *
 * ThemePreferenceService exposes these interfaces for bidirectional
 * theme switching with context preservation.
 */

export type ThemeName = 'classic' | 'new';

export interface ThemePreferenceService {
  /** Get the persisted theme preference, defaults to 'classic' */
  getPreference(): ThemeName;

  /** Persist theme preference to localStorage */
  setPreference(theme: ThemeName): void;

  /**
   * Map the current URL to its equivalent in the target theme.
   * Extracts route params (:pageId, :templateId) and query params,
   * maps them per the Route Equivalence Matrix.
   *
   * @param currentUrl - Current router URL (e.g., '/templates', '/ui/desk/fill/abc-123')
   * @param target - Target theme to switch to
   * @param userRole - Current user's role, used for safe fallback selection
   * @returns Target URL in the other theme
   */
  mapRouteToTheme(currentUrl: string, target: ThemeName, userRole: string): string;

  /**
   * Get the role-appropriate default landing page for a theme.
   *
   * @param theme - Target theme
   * @param userRole - Current user's role
   * @returns Default landing URL for that theme+role combination
   */
  getDefaultRoute(theme: ThemeName, userRole: string): string;
}

/**
 * Route Equivalence Matrix (bidirectional mapping)
 *
 * Each entry defines a Classic↔New route pair with optional param extraction.
 */
export interface RouteMapping {
  classic: string;       // Classic URL pattern (e.g., '/templates', '/designer/:pageId')
  new: string;           // New URL pattern (e.g., '/ui/studio/templates', '/ui/studio/designer/:pageId')
  params?: string[];     // Named params to preserve (e.g., ['pageId', 'templateId'])
  productionReady: boolean; // Whether the New route is production-ready
  fallbackClassic: string;  // Safe fallback in Classic if target unavailable
  fallbackNew: string;      // Safe fallback in New if target unavailable
}
