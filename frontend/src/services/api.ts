import axios from 'axios';
import type {
  ProcurementRequestResponse,
  ProcurementItem,
  StatusResponse,
  ResultsResponse,
  DecisionAction,
} from './types';

const api = axios.create({ baseURL: '/api' });

export async function createRequest(
  inputText: string,
  file?: File,
  userId = 'demo_user'
): Promise<ProcurementRequestResponse> {
  const form = new FormData();
  form.append('input_text', inputText);
  form.append('user_id', userId);
  if (file) form.append('file', file);
  const { data } = await api.post('/procurement/request', form);
  return data;
}

export async function confirmRequest(
  requestId: string,
  items: ProcurementItem[]
): Promise<void> {
  await api.post(`/procurement/${requestId}/confirm`, { items });
}

export async function getStatus(requestId: string): Promise<StatusResponse> {
  const { data } = await api.get(`/procurement/${requestId}/status`);
  return data;
}

export async function getResults(requestId: string): Promise<ResultsResponse> {
  const { data } = await api.get(`/procurement/${requestId}/results`);
  return data;
}

export async function recordDecision(
  requestId: string,
  action: DecisionAction,
  chosenListingId?: string,
  overrideReason?: string
): Promise<void> {
  await api.post(`/procurement/${requestId}/decision`, {
    action,
    chosen_listing_id: chosenListingId,
    override_reason: overrideReason,
  });
}

export function getExportUrl(requestId: string, format: 'pdf' | 'excel'): string {
  return `/api/procurement/${requestId}/export?format=${format}`;
}
