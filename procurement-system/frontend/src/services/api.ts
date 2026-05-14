import type { ParsedItem, ProcurementResults, ProcurementStatus, RequestCreated } from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "";

async function parseJson(res: Response) {
  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(text || `HTTP ${res.status}`);
  }
}

export async function createRequest(inputText: string, file?: File): Promise<RequestCreated> {
  if (file) {
    const fd = new FormData();
    fd.append("input_text", inputText);
    fd.append("input_file", file);
    const res = await fetch(`${API_BASE}/api/procurement/request`, { method: "POST", body: fd });
    if (!res.ok) throw new Error((await parseJson(res)).detail || res.statusText);
    return parseJson(res);
  }
  const res = await fetch(`${API_BASE}/api/procurement/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input_text: inputText }),
  });
  if (!res.ok) throw new Error((await parseJson(res)).detail || res.statusText);
  return parseJson(res);
}

export async function getRequestSummary(requestId: string) {
  const res = await fetch(`${API_BASE}/api/procurement/${requestId}/summary`);
  if (!res.ok) throw new Error((await parseJson(res)).detail || res.statusText);
  return parseJson(res);
}

export async function confirmRequest(requestId: string, items: ParsedItem[]) {
  const res = await fetch(`${API_BASE}/api/procurement/${requestId}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items }),
  });
  if (!res.ok) throw new Error((await parseJson(res)).detail || res.statusText);
  return parseJson(res);
}

export async function getStatus(requestId: string): Promise<ProcurementStatus> {
  const res = await fetch(`${API_BASE}/api/procurement/${requestId}/status`);
  if (!res.ok) throw new Error((await parseJson(res)).detail || res.statusText);
  return parseJson(res);
}

export async function getResults(requestId: string): Promise<ProcurementResults> {
  const res = await fetch(`${API_BASE}/api/procurement/${requestId}/results`);
  if (!res.ok) throw new Error((await parseJson(res)).detail || res.statusText);
  return parseJson(res);
}

export async function submitDecision(
  requestId: string,
  body: { action: "accept" | "override" | "re_search" | "reject"; chosen_listing_id?: string; override_reason?: string },
) {
  const res = await fetch(`${API_BASE}/api/procurement/${requestId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error((await parseJson(res)).detail || res.statusText);
  return parseJson(res);
}

export function exportUrl(requestId: string, format: "pdf" | "excel") {
  return `${API_BASE}/api/procurement/${requestId}/export?format=${format}`;
}
