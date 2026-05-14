import React from "react";
import type { ProcurementStatus } from "../services/types";

export const CrawlProgressView: React.FC<{ status: ProcurementStatus | null }> = ({ status }) => {
  if (!status) return null;
  const p = status.progress;
  return (
    <div className="card" style={{ marginTop: 16 }}>
      <h3 style={{ marginTop: 0 }}>處理進度</h3>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span className="badge">狀態：{status.status}</span>
        <span className="badge">
          平台 {p.platforms_crawled}/{p.total_platforms}
        </span>
        <span className="badge">刊登數：{p.listings_found}</span>
        <span className="badge">群組數：{p.clusters_created}</span>
      </div>
    </div>
  );
};
