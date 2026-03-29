export interface User {
  id: string;
  username: string;
  display_name: string;
  created_at: string;
}

export interface Item {
  id: string;
  name: string;
  category: Category;
  description: string | null;
  grade: string | null;
  purchase_price: number | null;
  purchase_date: string | null;
  catalog_ref: string | null;
  tags: string[];
  metadata: Record<string, unknown>;
  photos: string[];
  pinned_value: number | null;
  search_override: string | null;
  created_at: string;
  current_value: number | null;
  current_confidence: number | null;
  value_change_pct: number | null;
}

export type Category =
  | 'pokemon'
  | 'sports'
  | 'mtg'
  | 'coins'
  | 'sealed'
  | 'apparel'
  | 'other';

export const CATEGORIES: { value: Category; label: string }[] = [
  { value: 'pokemon', label: 'Pokémon' },
  { value: 'sports', label: 'Sports Cards' },
  { value: 'mtg', label: 'Magic: The Gathering' },
  { value: 'coins', label: 'Coins' },
  { value: 'sealed', label: 'Sealed Product' },
  { value: 'apparel', label: 'Apparel' },
  { value: 'other', label: 'Other' },
];

export interface Appraisal {
  id: string;
  item_id: string;
  price: number;
  currency: string;
  source: string;
  source_url: string | null;
  confidence: number;
  grade_specific: boolean;
  composite_price: number | null;
  composite_confidence: number | null;
  timestamp: string;
}

export interface Trove {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  item_count: number;
  total_value: number | null;
}

export interface PortfolioSnapshot {
  timestamp: string;
  total_value: number;
  item_count: number;
  confidence: number;
}

export interface PortfolioSummary {
  total_value: number | null;
  total_cost: number | null;
  total_gain: number | null;
  gain_pct: number | null;
  item_count: number;
  high_confidence_count: number;
  history: PortfolioSnapshot[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
