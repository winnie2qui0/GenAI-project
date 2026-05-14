export type ParsedItem = {
  product_name: string;
  brand?: string | null;
  model?: string | null;
  quantity: number;
  max_price?: number | null;
  currency: string;
  max_lead_time_days?: number | null;
  moq_acceptable: number;
  specs?: Record<string, unknown> | null;
};

export type RequestCreated = {
  request_id: string;
  parsed_items: ParsedItem[];
  status: string;
};

export type CrawlProgress = {
  platforms_crawled: number;
  total_platforms: number;
  listings_found: number;
  clusters_created: number;
};

export type ProcurementStatus = {
  status: string;
  progress: CrawlProgress;
};

export type ScoreBreakdown = {
  price_score: number;
  delivery_score: number;
  rating_score: number;
  trust_score: number;
};

export type ListingRanked = {
  rank: number;
  listing_id: string;
  source: string;
  price: number;
  currency: string;
  price_usd?: number | null;
  delivery_days?: number | null;
  rating?: number | null;
  final_score: number;
  score_breakdown: ScoreBreakdown;
  anomalies: Array<Record<string, unknown>>;
  llm_explanation?: string | null;
  url: string;
};

export type ClusterResult = {
  cluster_id: string;
  canonical_name: string;
  confidence: string;
  ranked_listings: ListingRanked[];
};

export type ProcurementResults = {
  request_id: string;
  clusters: ClusterResult[];
};
