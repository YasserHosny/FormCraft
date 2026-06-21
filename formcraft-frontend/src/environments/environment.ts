import { Environment } from './environment.interface';

export const getDevLocalImportEnabled = (): boolean => {
  if (typeof window === 'undefined') return false;
  const devLocalImport = (window as any).FC_DEV_LOCAL_IMPORT === true;
  if (!devLocalImport) return false;
  const automationFlag = (window as any).FC_AUTOMATION === true;
  const queryFlag = new URLSearchParams(window.location.search).get('automation') === '1';
  return automationFlag || queryFlag;
};

export const environment: Environment = {
  production: false,
  apiBaseUrl: '/api',
  apiUrl: 'http://localhost:8000/api',
  get supabaseUrl() {
    const runtimeConfig = (window as any).FC_RUNTIME_CONFIG;
    if (runtimeConfig?.supabase?.url) {
      return runtimeConfig.supabase.url;
    }
    return (window as any).SUPABASE_URL || 'http://localhost:54321';
  },
  get supabaseAnonKey() {
    const runtimeConfig = (window as any).FC_RUNTIME_CONFIG;
    if (runtimeConfig?.supabase?.anonKey) {
      return runtimeConfig.supabase.anonKey;
    }
    return (window as any).SUPABASE_ANON_KEY || '';
  },
  get stripePublishableKey() {
    return (window as any).STRIPE_PUBLISHABLE_KEY ||
      'pk_test_51Tk4CzDTpg7yoNvm4Rl2SOLk3U5bFwFWDvhrN2gxkHLUwKuZYj0tyxYgdWR6JKwLPi6yeG57P7HnAfIyCgk93qum00MEtf4AN3';
  },
};
