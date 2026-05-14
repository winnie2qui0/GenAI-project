import React from "react";

export const RecommendationCard: React.FC<{ markdown?: string | null }> = ({ markdown }) => {
  if (!markdown) return null;
  return (
    <div className="card" style={{ marginTop: 16 }}>
      <h3 style={{ marginTop: 0 }}>LLM 建議說明</h3>
      <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", margin: 0, color: "#0f172a" }}>{markdown}</pre>
    </div>
  );
};
