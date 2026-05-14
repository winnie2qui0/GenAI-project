import React from "react";
import type { ProcurementResults } from "../services/types";

export const ComparisonTable: React.FC<{ data: ProcurementResults | null }> = ({ data }) => {
  if (!data) return null;
  return (
    <div className="card" style={{ marginTop: 16 }}>
      <h3 style={{ marginTop: 0 }}>比價結果</h3>
      {data.clusters.map((c) => (
        <div key={c.cluster_id} style={{ marginBottom: 18 }}>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>
            {c.canonical_name}{" "}
            <span className="badge" style={{ marginLeft: 8 }}>
              信心：{c.confidence}
            </span>
          </div>
          <div style={{ overflowX: "auto" }}>
            <table className="table">
              <thead>
                <tr>
                  <th>排名</th>
                  <th>來源</th>
                  <th>價格</th>
                  <th>USD</th>
                  <th>交期（天）</th>
                  <th>評分</th>
                  <th>總分</th>
                  <th>連結</th>
                </tr>
              </thead>
              <tbody>
                {c.ranked_listings.map((l) => (
                  <tr key={l.listing_id}>
                    <td>{l.rank}</td>
                    <td>{l.source}</td>
                    <td>
                      {l.price} {l.currency}
                    </td>
                    <td>{l.price_usd ?? "—"}</td>
                    <td>{l.delivery_days ?? "—"}</td>
                    <td>{l.rating ?? "—"}</td>
                    <td>{l.final_score.toFixed(2)}</td>
                    <td>
                      <a href={l.url} target="_blank" rel="noreferrer">
                        開啟
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
};
