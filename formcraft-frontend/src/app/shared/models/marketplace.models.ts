export type MarketplacePriceType = 'free' | 'premium';
export type MarketplaceListingStatus =
  | 'draft'
  | 'submitted'
  | 'approved'
  | 'rejected'
  | 'active'
  | 'suspended'
  | 'archived';

export interface MarketplaceListing {
  id: string;
  template_id: string;
  publisher_org_id: string;
  publisher_org_name?: string;
  name: string;
  description: string;
  tags: string[];
  preview_image_urls: string[];
  compliance_badges: string[];
  category: string;
  country: string;
  language: string;
  quality_score: number;
  price_type: MarketplacePriceType;
  price_amount?: number | null;
  currency: string;
  status: MarketplaceListingStatus;
  review_status: string;
  download_count: number;
  average_rating?: number | null;
  review_count: number;
  published_version: number;
}

export interface MarketplaceListResponse {
  items: MarketplaceListing[];
  total: number;
  page: number;
  page_size: number;
}

export interface MarketplaceListingDetail extends MarketplaceListing {
  template_preview: Record<string, unknown>;
  sample_pdf_url?: string | null;
  dependency_warnings: string[];
}

export interface MarketplaceImportResponse {
  import_id: string;
  template_id: string;
  remapping_status: string;
  disabled_dependency_warnings: string[];
}

export interface MarketplaceTransactionResponse {
  transaction_id: string;
  payment_status: string;
  amount: number;
  currency: string;
  publisher_share: number;
  platform_share: number;
}

export interface MarketplaceReview {
  id: string;
  listing_id: string;
  consumer_org_id: string;
  reviewer_id: string;
  import_id: string;
  rating: number;
  review_text: string;
  verified_import: boolean;
  status: string;
}
