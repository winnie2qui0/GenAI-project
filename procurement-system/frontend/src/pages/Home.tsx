import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ProcurementForm } from "../components/ProcurementForm";
import { createRequest } from "../services/api";
import type { ParsedItem } from "../services/types";

function normalizeItems(items: ParsedItem[]): ParsedItem[] {
  return items.map((it) => ({
    product_name: it.product_name,
    brand: it.brand ?? null,
    model: it.model ?? null,
    quantity: it.quantity ?? 1,
    max_price: it.max_price ?? null,
    currency: it.currency || "USD",
    max_lead_time_days: it.max_lead_time_days ?? null,
    moq_acceptable: it.moq_acceptable ?? 1,
    specs: it.specs ?? null,
  }));
}

export const Home: React.FC = () => {
  const nav = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (text: string, file?: File) => {
    setError(null);
    try {
      const res = await createRequest(text, file);
      nav(`/procurement/${res.request_id}`, { state: { items: normalizeItems(res.parsed_items) } });
    } catch (e) {
      setError(e instanceof Error ? e.message : "建立需求失敗");
    }
  };

  return (
    <div className="layout">
      <div className="card">
        <h1 style={{ marginTop: 0 }}>AI 採購比價（MVP）</h1>
        <p style={{ color: "#475569" }}>上傳清單或以自然語言描述需求；系統會解析、爬取多平台並以可稽核的規則評分。</p>
        <ProcurementForm onSubmit={onSubmit} />
        {error && <p style={{ color: "#b91c1c", marginTop: 12 }}>{error}</p>}
      </div>
    </div>
  );
};
