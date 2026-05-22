import { Environment } from './environment.interface';

export const getDevLocalImportEnabled = (): boolean => false;

export const environment: Environment = {
  production: true,
  apiBaseUrl: '/api',
  apiUrl: '/api',
  get supabaseUrl() {
    const runtimeConfig = (window as any).FC_RUNTIME_CONFIG;
    if (runtimeConfig?.supabase?.url) {
      return runtimeConfig.supabase.url;
    }
    return (window as any).SUPABASE_URL || '';
  },
  get supabaseAnonKey() {
    const runtimeConfig = (window as any).FC_RUNTIME_CONFIG;
    if (runtimeConfig?.supabase?.anonKey) {
      return runtimeConfig.supabase.anonKey;
    }
    return (window as any).SUPABASE_ANON_KEY || '';
  },
};
