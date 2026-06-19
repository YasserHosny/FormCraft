export type BillingPurpose = 'subscription_tier' | 'seats' | 'ocr_batch' | 'marketplace_template';
export type BillingPurchaseStatus = 'created' | 'requires_action' | 'succeeded' | 'failed' | 'refunded' | 'cancelled';

export interface BillingTierOption {
  tier: string;
  amount_minor: number | null;
  currency: string;
  available: boolean;
  unavailable_reason_key?: string | null;
}

export interface BillingAddonOption {
  purpose: BillingPurpose;
  unit_amount_minor: number | null;
  currency: string;
  min_quantity?: number | null;
  max_quantity?: number | null;
  available: boolean;
  unavailable_reason_key?: string | null;
}

export interface BillingOptionsResponse {
  currency: string;
  current_tier: string;
  tiers: BillingTierOption[];
  addons: BillingAddonOption[];
}

export interface BillingCheckoutToken {
  provider: 'paygateway';
  client_token: string;
  requires_action: boolean;
  expires_at?: string | null;
}

export interface BillingPurchaseCreateRequest {
  purpose: BillingPurpose;
  target: Record<string, unknown>;
  quantity?: number | null;
  return_url?: string | null;
}

export interface BillingPurchaseCreateResponse {
  purchase_id: string;
  status: BillingPurchaseStatus;
  amount_minor: number;
  currency: string;
  checkout: BillingCheckoutToken | null;
  message_key?: string | null;
}

export interface BillingPurchaseVerifyResponse {
  purchase_id: string;
  status: BillingPurchaseStatus;
  fulfilled: boolean;
  message_key?: string | null;
}

export interface BillingPurchase {
  id: string;
  organization_id: string;
  purpose: BillingPurpose;
  target: Record<string, unknown>;
  quantity?: number | null;
  amount_minor: number;
  currency: string;
  status: BillingPurchaseStatus;
  fulfilled_at?: string | null;
  created_at: string;
}

export interface BillingPurchaseListResponse {
  items: BillingPurchase[];
  next_cursor?: string | null;
}

export interface BillingRefundResponse {
  refund_id: string;
  purchase_id: string;
  status: 'requested' | 'succeeded' | 'failed';
  reversal_status: 'pending' | 'applied' | 'failed';
  amount_minor: number;
  currency: string;
  message_key: string;
}
