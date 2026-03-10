export type TemplateStatus = 'draft' | 'published';
export type ElementType = 'text' | 'number' | 'date' | 'currency' | 'dropdown' | 'radio' | 'checkbox' | 'image' | 'qr' | 'barcode';
export type Country = 'EG' | 'SA' | 'AE';
export type Language = 'ar' | 'en';
export type Direction = 'rtl' | 'ltr' | 'auto';
export type Role = 'admin' | 'designer' | 'operator' | 'viewer';

export interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  status: TemplateStatus;
  version: number;
  language: Language;
  country: Country;
  created_at: string;
  updated_at: string;
  created_by: string;
  pages: Page[];
}

export interface Page {
  id: string;
  template_id: string;
  width_mm: number;
  height_mm: number;
  background_asset: string | null;
  sort_order: number;
  elements: Element[];
}

export interface Element {
  id: string;
  page_id: string;
  type: ElementType;
  key: string;
  label_ar: string;
  label_en: string;
  x_mm: number;
  y_mm: number;
  width_mm: number;
  height_mm: number;
  validation: Record<string, unknown>;
  formatting: Record<string, unknown>;
  required: boolean;
  direction: Direction;
  sort_order: number;
}
