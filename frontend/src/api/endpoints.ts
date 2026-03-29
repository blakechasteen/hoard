import { api, setToken } from './client';
import type {
  Appraisal,
  Item,
  PortfolioSummary,
  TokenResponse,
  Trove,
  User,
} from '../types';

// --- Auth ---

export async function register(
  username: string,
  display_name: string,
  password: string,
  invite_code: string,
): Promise<string> {
  const res = await api.post<TokenResponse>('/auth/register', {
    username,
    display_name,
    password,
    invite_code,
  });
  setToken(res.access_token);
  return res.access_token;
}

export async function login(username: string, password: string): Promise<string> {
  const res = await api.post<TokenResponse>('/auth/login', { username, password });
  setToken(res.access_token);
  return res.access_token;
}

export async function getMe(): Promise<User> {
  return api.get<User>('/auth/me');
}

// --- Items ---

export async function listItems(category?: string): Promise<Item[]> {
  const params = category ? `?category=${category}` : '';
  return api.get<Item[]>(`/items${params}`);
}

export async function getItem(id: string): Promise<Item> {
  return api.get<Item>(`/items/${id}`);
}

export async function createItem(data: {
  name: string;
  category: string;
  description?: string;
  grade?: string;
  purchase_price?: number;
  purchase_date?: string;
  catalog_ref?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
  search_override?: string;
}): Promise<Item> {
  return api.post<Item>('/items', data);
}

export async function updateItem(
  id: string,
  data: Partial<Item>,
): Promise<Item> {
  return api.patch<Item>(`/items/${id}`, data);
}

export async function deleteItem(id: string): Promise<void> {
  return api.delete(`/items/${id}`);
}

// --- Appraisals ---

export async function listAppraisals(
  itemId: string,
  days = 365,
): Promise<Appraisal[]> {
  return api.get<Appraisal[]>(`/items/${itemId}/appraisals?days=${days}`);
}

export async function createAppraisal(
  itemId: string,
  data: {
    price: number;
    source?: string;
    source_url?: string;
    confidence?: number;
    grade_specific?: boolean;
  },
): Promise<Appraisal> {
  return api.post<Appraisal>(`/items/${itemId}/appraisals`, data);
}

// --- Troves ---

export async function listTroves(): Promise<Trove[]> {
  return api.get<Trove[]>('/troves');
}

export async function createTrove(data: {
  name: string;
  description?: string;
  item_ids?: string[];
}): Promise<Trove> {
  return api.post<Trove>('/troves', data);
}

// --- Portfolio ---

export async function getPortfolioSummary(days = 365): Promise<PortfolioSummary> {
  return api.get<PortfolioSummary>(`/portfolio/summary?days=${days}`);
}
