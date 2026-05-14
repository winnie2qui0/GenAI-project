import React from "react";
import type { ParsedItem } from "../services/types";

export const ParamConfirmation: React.FC<{
  items: ParsedItem[];
  onChange: (next: ParsedItem[]) => void;
}> = ({ items, onChange }) => {
  const update = (idx: number, patch: Partial<ParsedItem>) => {
    const next = items.map((it, i) => (i === idx ? { ...it, ...patch } : it));
    onChange(next);
  };

  return (
    <div className="card" style={{ marginTop: 16 }}>
      <h3 style={{ marginTop: 0 }}>參數確認</h3>
      <p style={{ color: "#475569", fontSize: 14 }}>請確認或調整 LLM 解析欄位，再送出以啟動爬蟲。</p>
      {items.map((it, idx) => (
        <div key={idx} style={{ borderTop: idx ? "1px solid #e2e8f0" : undefined, paddingTop: 12, marginTop: 12 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <label>
              品名
              <input
                style={{ width: "100%", marginTop: 6, padding: 8, borderRadius: 8, border: "1px solid #cbd5e1" }}
                value={it.product_name}
                onChange={(e) => update(idx, { product_name: e.target.value })}
              />
            </label>
            <label>
              數量
              <input
                type="number"
                style={{ width: "100%", marginTop: 6, padding: 8, borderRadius: 8, border: "1px solid #cbd5e1" }}
                value={it.quantity}
                onChange={(e) => update(idx, { quantity: Number(e.target.value) })}
              />
            </label>
            <label>
              品牌
              <input
                style={{ width: "100%", marginTop: 6, padding: 8, borderRadius: 8, border: "1px solid #cbd5e1" }}
                value={it.brand || ""}
                onChange={(e) => update(idx, { brand: e.target.value || null })}
              />
            </label>
            <label>
              型號
              <input
                style={{ width: "100%", marginTop: 6, padding: 8, borderRadius: 8, border: "1px solid #cbd5e1" }}
                value={it.model || ""}
                onChange={(e) => update(idx, { model: e.target.value || null })}
              />
            </label>
            <label>
              單價上限
              <input
                type="number"
                style={{ width: "100%", marginTop: 6, padding: 8, borderRadius: 8, border: "1px solid #cbd5e1" }}
                value={it.max_price ?? ""}
                onChange={(e) => update(idx, { max_price: e.target.value === "" ? null : Number(e.target.value) })}
              />
            </label>
            <label>
              幣別
              <input
                style={{ width: "100%", marginTop: 6, padding: 8, borderRadius: 8, border: "1px solid #cbd5e1" }}
                value={it.currency}
                onChange={(e) => update(idx, { currency: e.target.value })}
              />
            </label>
            <label>
              交期上限（天）
              <input
                type="number"
                style={{ width: "100%", marginTop: 6, padding: 8, borderRadius: 8, border: "1px solid #cbd5e1" }}
                value={it.max_lead_time_days ?? ""}
                onChange={(e) =>
                  update(idx, { max_lead_time_days: e.target.value === "" ? null : Number(e.target.value) })
                }
              />
            </label>
            <label>
              可接受 MOQ
              <input
                type="number"
                style={{ width: "100%", marginTop: 6, padding: 8, borderRadius: 8, border: "1px solid #cbd5e1" }}
                value={it.moq_acceptable}
                onChange={(e) => update(idx, { moq_acceptable: Number(e.target.value) })}
              />
            </label>
          </div>
        </div>
      ))}
    </div>
  );
};
