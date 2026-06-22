export type BillingPurpose = 'subscription_tier' | 'seats' | 'ocr_batch' | 'marketplace_template';
export type BillingPurchaseStatus = 'created' | 'requires_action' | 'succeeded' | 'failed' | 'refunded' | 'cancelled';

export interface BillingTierOption {
  tier: string;
  amount_minor: number | null;
  currency: string;
  available: boolean;
  unavailable_reason_key?: string | null;
  is_current: boolean;
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

// F059 — Recurring subscription billing models

export type SubscriptionStatus = 'active' | 'past_due' | 'cancelled';
export type BillingInterval = 'monthly' | 'annual';

export interface SubscriptionResponse {
  id: string;
  org_id: string;
  tier: string;
  billing_interval: BillingInterval;
  status: SubscriptionStatus;
  current_period_start: string;
  current_period_end: string;
  next_renewal_amount_minor: number;
  currency: string;
  scheduled_downgrade_tier: string | null;
  cancel_at_period_end: boolean;
  failed_payment_count: number;
  provider_subscription_id?: string | null;
}

export interface CreateSubscriptionRequest {
  tier: string;
  billing_interval: BillingInterval;
  return_url: string;
}

export interface CreateSubscriptionResponse {
  subscription_id: string;
  status: string;
  checkout: BillingCheckoutToken | null;
}

export interface UpgradeSubscriptionRequest {
  tier: string;
}

export interface UpgradeSubscriptionResponse {
  subscription_id: string;
  previous_tier: string;
  new_tier: string;
  proration_amount_minor: number;
  currency: string;
  status: SubscriptionStatus;
}

export interface ScheduleDowngradeRequest {
  tier: string;
}

export interface DowngradeScheduleResponse {
  subscription_id: string;
  current_tier: string;
  scheduled_downgrade_tier: string | null;
  effective_date?: string | null;
}

export interface CancelSubscriptionResponse {
  subscription_id: string;
  tier: string;
  cancel_at_period_end: boolean;
  period_end: string;
}

export interface ReactivateSubscriptionResponse {
  subscription_id: string;
  tier: string;
  cancel_at_period_end: boolean;
  next_renewal_date: string;
}

export interface PortalUrlResponse {
  portal_url: string;
  expires_at: string;
}
