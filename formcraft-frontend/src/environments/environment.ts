export const getDevLocalImportEnabled = (): boolean => {
  if (typeof window === 'undefined') return false;
  const devLocalImport = (window as any).FC_DEV_LOCAL_IMPORT === true;
  if (!devLocalImport) return false;
  const automationFlag = (window as any).FC_AUTOMATION === true;
  const queryFlag = new URLSearchParams(window.location.search).get('automation') === '1';
  return automationFlag || queryFlag;
};

export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:8000/api',
};
