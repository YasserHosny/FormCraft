export interface Customer {
  id: string;
  org_id: string;
  name_ar: string;
  name_en: string | null;
  identifier_type: string;
  identifier: string;
  contact_phone: string | null;
  contact_email: string | null;
  address: string | null;
  custom_fields: Record<string, any> | null;
  is_active: boolean;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface CustomerCreate {
  name_ar: string;
  name_en?: string;
  identifier_type: string;
  identifier: string;
  contact_phone?: string;
  contact_email?: string;
  address?: string;
  custom_fields?: Record<string, any>;
}

export interface CustomerUpdate {
  name_ar?: string;
  name_en?: string;
  identifier_type?: string;
  identifier?: string;
  contact_phone?: string;
  contact_email?: string;
  address?: string;
  custom_fields?: Record<string, any>;
  is_active?: boolean;
}

export interface CustomerListResponse {
  items: Customer[];
  total: number;
  page: number;
  page_size: number;
}

export interface CustomerSearchParams {
  page?: number;
  page_size?: number;
  search?: string;
  is_active?: boolean;
  sort_by?: string;
  sort_order?: string;
}

export interface AutoPopulateMapping {
  element_key: string;
  value: any;
  source: string;
}

export interface CustomerFieldMapping {
  element_key: string;
  customer_field: string;
}

export interface CustomerMergeRequest {
  source_customer_id: string;
  target_customer_id: string;
}
