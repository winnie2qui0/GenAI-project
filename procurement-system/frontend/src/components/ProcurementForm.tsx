import React, { useState } from "react";
import { Send } from "lucide-react";

interface ProcurementFormProps {
  onSubmit: (input: string, file?: File) => void;
}

export const ProcurementForm: React.FC<ProcurementFormProps> = ({ onSubmit }) => {
  const [textInput, setTextInput] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(textInput, file || undefined);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">描述採購需求（自然語言）</label>
        <textarea
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          placeholder="例：需要 500 組 HP CF410A 碳粉，單價上限 USD 40，交期 2 天內"
          style={{ width: "100%", padding: 12, borderRadius: 10, border: "1px solid #cbd5e1", minHeight: 120 }}
          rows={4}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">或上傳 Excel / CSV</label>
        <input type="file" accept=".xlsx,.csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      </div>

      <button type="submit" className="btn btn-primary" style={{ width: "100%" }}>
        <Send size={16} />
        開始比價
      </button>
    </form>
  );
};
