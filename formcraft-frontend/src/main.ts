import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';

const loadRuntimeConfig = async () => {
  try {
    const response = await fetch('/assets/runtime-config.json', { cache: 'no-store' });
    if (!response.ok) return;
    const config = await response.json();
    
    // Store the full runtime configuration
    (window as any).FC_RUNTIME_CONFIG = config;
    
    // Maintain backward compatibility
    if (config?.devLocalImport === true) {
      (window as any).FC_DEV_LOCAL_IMPORT = true;
    }
    
    // Also set Supabase config to window for backward compatibility
    if (config?.supabase) {
      (window as any).SUPABASE_URL = config.supabase.url;
      (window as any).SUPABASE_ANON_KEY = config.supabase.anonKey;
      (window as any).SUPABASE_SERVICE_KEY = config.supabase.serviceRoleKey;
      (window as any).SUPABASE_JWT_SECRET = config.supabase.jwtSecret;
    }
  } catch {
    // Ignore missing runtime config in production builds.
  }
};

loadRuntimeConfig()
  .finally(() => {
    platformBrowserDynamic()
      .bootstrapModule(AppModule)
      .catch((err) => console.error(err));
  });
