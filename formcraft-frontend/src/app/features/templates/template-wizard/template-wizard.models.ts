export interface WizardState {
  stepIndex: number;
  basicInfo: {
    name: string;
    description: string;
    category: string;
    tags: string[];
  };
  locale: {
    language: 'ar' | 'en';
    country: 'EG' | 'SA' | 'AE';
    currency: string;
  };
  pageSetup: {
    pageSize: 'A4' | 'A3' | 'Letter' | 'Legal' | 'Custom';
    customWidthMm?: number;
    customHeightMm?: number;
    orientation: 'portrait' | 'landscape';
    margins: {
      top: number;
      bottom: number;
      left: number;
      right: number;
    };
  };
  startingPoint: {
    type: 'blank' | 'clone' | 'ocr' | 'package';
    cloneTemplateId?: string;
    packageFile?: File;
  };
  createdAt: string;
}

export const DEFAULT_WIZARD_STATE: WizardState = {
  stepIndex: 0,
  basicInfo: {
    name: '',
    description: '',
    category: '',
    tags: [],
  },
  locale: {
    language: 'ar',
    country: 'EG',
    currency: 'EGP',
  },
  pageSetup: {
    pageSize: 'A4',
    orientation: 'portrait',
    margins: {
      top: 10,
      bottom: 10,
      left: 10,
      right: 10,
    },
  },
  startingPoint: {
    type: 'blank',
  },
  createdAt: new Date().toISOString(),
};

export interface OrgCategory {
  id: string;
  name: string;
  is_system_default: boolean;
}

export interface ClonePreview {
  template_id: string;
  name: string;
  thumbnail_url: string | null;
  page_count: number;
  element_count: number;
  reference_binding_warnings: any[];
}

export interface PackageImportPreview {
  name: string;
  page_count: number;
  element_count: number;
  formcraft_version: string;
  version_compatible: boolean;
  version_warning: string | null;
  missing_bindings: any[];
  can_import: boolean;
}
