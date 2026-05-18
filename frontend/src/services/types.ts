export interface ProcurementItem {
  product_name: string;
  brand?: string;
  model?: string;
  quantity: number;
  max_price?: number;
  currency: string;
  max_lead_time_days?: number;
  moq_acceptable: number;
}

export interface ScoreBreakdown {
  price_score: number;
  delivery_score: number;
  rating_score: number;
  trust_score: number;
}

export interface AnomalyFlag {
  type: string;
  severity: 'info' | 'warning' | 'error';
  message: string;
}

export interface RankedListing {
  rank: number;
  listing_id: string;
  source: string;
  title: string;
  price: number;
  currency: string;
  price_usd?: number;
  delivery_days?: number;
  rating?: number;
  review_count?: number;
  moq: number;
  seller_name?: string;
  final_score: number;
  score_breakdown: ScoreBreakdown;
  anomalies: AnomalyFlag[];
  llm_explanation?: string;
  url: string;
}

export interface ClusterResult {
  cluster_id: string;
  canonical_name: string;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  matching_method?: string;
  ranked_listings: RankedListing[];
}

export interface ProcurementRequestResponse {
  request_id: string;
  parsed_items: ProcurementItem[];
  status: string;
  created_at: string;
}

export interface StatusResponse {
  status: 'pending' | 'crawling' | 'matching' | 'scoring' | 'completed' | 'failed';
  progress: {
    platforms_crawled?: number;
    total_platforms?: number;
    listings_found?: number;
    clusters_created?: number;
  };
}

export interface ResultsResponse {
  request_id: string;
  clusters: ClusterResult[];
}

export type DecisionAction = 'accept' | 'override' | 're_search' | 'reject';
