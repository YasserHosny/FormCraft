import { ElementType } from './template.model';

export interface ElementDefault {
  type: ElementType;
  width_mm: number;
  height_mm: number;
  label_ar: string;
  label_en: string;
  icon: string;
}

export const ELEMENT_DEFAULTS: Record<ElementType, ElementDefault> = {
  text: { type: 'text', width_mm: 50, height_mm: 8, label_ar: 'نص', label_en: 'Text', icon: 'text_fields' },
  number: { type: 'number', width_mm: 40, height_mm: 8, label_ar: 'رقم', label_en: 'Number', icon: 'pin' },
  date: { type: 'date', width_mm: 40, height_mm: 8, label_ar: 'تاريخ', label_en: 'Date', icon: 'calendar_today' },
  currency: { type: 'currency', width_mm: 40, height_mm: 8, label_ar: 'عملة', label_en: 'Currency', icon: 'attach_money' },
  dropdown: { type: 'dropdown', width_mm: 50, height_mm: 8, label_ar: 'قائمة منسدلة', label_en: 'Dropdown', icon: 'arrow_drop_down_circle' },
  radio: { type: 'radio', width_mm: 50, height_mm: 8, label_ar: 'اختيار فردي', label_en: 'Radio', icon: 'radio_button_checked' },
  checkbox: { type: 'checkbox', width_mm: 50, height_mm: 8, label_ar: 'مربع اختيار', label_en: 'Checkbox', icon: 'check_box' },
  image: { type: 'image', width_mm: 40, height_mm: 40, label_ar: 'صورة', label_en: 'Image', icon: 'image' },
  qr: { type: 'qr', width_mm: 30, height_mm: 30, label_ar: 'رمز QR', label_en: 'QR Code', icon: 'qr_code' },
  barcode: { type: 'barcode', width_mm: 50, height_mm: 15, label_ar: 'باركود', label_en: 'Barcode', icon: 'barcode_reader' },
};
