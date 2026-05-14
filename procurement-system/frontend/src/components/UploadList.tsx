import React from "react";
import { FileSpreadsheet } from "lucide-react";

export const UploadList: React.FC<{ onPick: (f: File) => void }> = ({ onPick }) => (
  <div className="card">
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <FileSpreadsheet size={18} />
      <strong>清單上傳</strong>
    </div>
    <p style={{ color: "#475569", fontSize: 14 }}>可選擇檔案後交由父層處理（示範元件）。</p>
    <input type="file" accept=".xlsx,.csv" onChange={(e) => e.target.files?.[0] && onPick(e.target.files[0])} />
  </div>
);
