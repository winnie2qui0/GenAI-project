import React, { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { ComparisonTable } from "../components/ComparisonTable";
import { CrawlProgressView } from "../components/CrawlProgress";
import { ParamConfirmation } from "../components/ParamConfirmation";
import { RecommendationCard } from "../components/RecommendationCard";
import { ReportExport } from "../components/ReportExport";
import { confirmRequest, getRequestSummary, getResults, getStatus, submitDecision } from "../services/api";
import type { ParsedItem, ProcurementResults, ProcurementStatus } from "../services/types";

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

export const ProcurementDetail: React.FC = () => {
  const { id } = useParams();
  const location = useLocation();
  const initialItems = (location.state as { items?: ParsedItem[] } | null)?.items;

  const [items, setItems] = useState<ParsedItem[] | null>(initialItems || null);
  const [status, setStatus] = useState<ProcurementStatus | null>(null);
  const [results, setResults] = useState<ProcurementResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [chosen, setChosen] = useState<string>("");

  const requestId = id || "";

  useEffect(() => {
    if (!requestId || items) return;
    let cancelled = false;
    void (async () => {
      try {
        const s = await getRequestSummary(requestId);
        if (cancelled) return;
        const pi = s.parsed_items as ParsedItem[] | { items: ParsedItem[] };
        const arr = Array.isArray(pi) ? pi : pi.items;
        setItems(normalizeItems(arr));
      } catch {
        // 若無法載入，保留為 null，讓畫面提示重新建立需求
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [requestId, items]);

  useEffect(() => {
    if (!requestId) return;
    let timer: ReturnType<typeof setInterval> | undefined;
    const tick = async () => {
      try {
        const s = await getStatus(requestId);
        setStatus(s);
        if (s.status === "completed") {
          const r = await getResults(requestId);
          setResults(r);
          if (timer) window.clearInterval(timer);
        }
        if (s.status === "failed") {
          setError("處理失敗，請查看後端日誌。");
          if (timer) window.clearInterval(timer);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "讀取狀態失敗");
      }
    };
    timer = window.setInterval(tick, 1500);
    void tick();
    return () => {
      if (timer) window.clearInterval(timer);
    };
  }, [requestId]);

  const firstExplanation = useMemo(() => {
    const c = results?.clusters?.[0];
    const top = c?.ranked_listings?.find((x) => x.rank === 1);
    return top?.llm_explanation || c?.ranked_listings?.[0]?.llm_explanation;
  }, [results]);

  const onConfirm = async () => {
    if (!items) return;
    setError(null);
    try {
      await confirmRequest(requestId, items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "確認失敗");
    }
  };

  const onDecision = async (action: "accept" | "override" | "re_search" | "reject") => {
    setError(null);
    try {
      await submitDecision(requestId, { action, chosen_listing_id: chosen || undefined });
      const raw = localStorage.getItem("procurement_history");
      let prev: string[] = [];
      try {
        prev = raw ? (JSON.parse(raw) as string[]) : [];
      } catch {
        prev = [];
      }
      const next = [requestId, ...prev.filter((x) => x !== requestId)].slice(0, 20);
      localStorage.setItem("procurement_history", JSON.stringify(next));
      alert("已記錄決策（audit_log）");
    } catch (e) {
      setError(e instanceof Error ? e.message : "決策失敗");
    }
  };

  if (!requestId) return <div className="layout">缺少 request id</div>;
  if (!items) {
    return (
      <div className="layout">
        <div className="card">
          <p>找不到解析結果狀態。請從首頁重新建立需求。</p>
          <Link to="/">回首頁</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="layout">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
        <Link to="/">← 回首頁</Link>
        <Link to="/history">歷史紀錄</Link>
      </div>

      <ParamConfirmation items={items} onChange={setItems} />
      <div style={{ marginTop: 12, display: "flex", gap: 12, flexWrap: "wrap" }}>
        <button className="btn btn-primary" type="button" onClick={onConfirm}>
          確認參數並開始爬取
        </button>
      </div>

      <CrawlProgressView status={status} />
      <ComparisonTable data={results} />
      <RecommendationCard markdown={firstExplanation} />
      {status?.status === "completed" && <ReportExport requestId={requestId} />}

      {status?.status === "completed" && results && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3 style={{ marginTop: 0 }}>決策紀錄</h3>
          <label style={{ display: "block", marginBottom: 8 }}>
            選擇 listing_id（可從表格複製）
            <input
              style={{ width: "100%", marginTop: 6, padding: 10, borderRadius: 10, border: "1px solid #cbd5e1" }}
              value={chosen}
              onChange={(e) => setChosen(e.target.value)}
              placeholder="例如：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            />
          </label>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <button className="btn btn-secondary" type="button" onClick={() => onDecision("accept")}>
              採納系統建議（accept）
            </button>
            <button className="btn btn-secondary" type="button" onClick={() => onDecision("override")}>
              覆寫（override）
            </button>
            <button className="btn btn-secondary" type="button" onClick={() => onDecision("reject")}>
              拒絕（reject）
            </button>
          </div>
        </div>
      )}

      {error && <p style={{ color: "#b91c1c", marginTop: 12 }}>{error}</p>}
    </div>
  );
};
