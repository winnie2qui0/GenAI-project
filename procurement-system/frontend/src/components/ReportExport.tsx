import React from "react";
import { exportUrl } from "../services/api";

export const ReportExport: React.FC<{ requestId: string }> = ({ requestId }) => (
  <div className="card" style={{ marginTop: 16, display: "flex", gap: 12, flexWrap: "wrap" }}>
    <a className="btn btn-secondary" href={exportUrl(requestId, "excel")}>
      匯出 Excel
    </a>
    <a className="btn btn-secondary" href={exportUrl(requestId, "pdf")}>
      匯出 PDF
    </a>
  </div>
);
