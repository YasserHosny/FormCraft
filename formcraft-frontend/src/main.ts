import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';

const loadRuntimeConfig = async () => {
  try {
    const response = await fetch('/assets/runtime-config.json', { cache: 'no-store' });
    if (!response.ok) return;
    const config = await response.json();
    if (config?.devLocalImport === true) {
      (window as any).FC_DEV_LOCAL_IMPORT = true;
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
