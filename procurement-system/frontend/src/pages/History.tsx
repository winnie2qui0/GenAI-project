import React, { useMemo } from "react";
import { Link } from "react-router-dom";

export const History: React.FC = () => {
  const ids = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem("procurement_history") || "[]") as string[];
    } catch {
      return [];
    }
  }, []);

  return (
    <div className="layout">
      <div className="card">
        <h2 style={{ marginTop: 0 }}>歷史紀錄（本機）</h2>
        <p style={{ color: "#475569" }}>此頁使用瀏覽器 localStorage 保存最近處理過的 request_id。</p>
        {ids.length === 0 ? (
          <p>尚無紀錄。</p>
        ) : (
          <ul>
            {ids.map((id) => (
              <li key={id}>
                <Link to={`/procurement/${id}`}>{id}</Link>
              </li>
            ))}
          </ul>
        )}
        <div style={{ marginTop: 12 }}>
          <Link to="/">回首頁</Link>
        </div>
      </div>
    </div>
  );
};
