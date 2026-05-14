import io
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Listing, ProcurementRequest, ProductCluster, ScoringResult


router = APIRouter(tags=["report"])


@router.get("/{request_id}/export")
def export_report(
    request_id: str,
    export_format: str = Query(..., alias="format"),
    db: Session = Depends(get_db),
):
    rid = uuid.UUID(request_id)
    row = db.get(ProcurementRequest, rid)
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")

    clusters = db.query(ProductCluster).filter(ProductCluster.request_id == rid).all()
    rows: list[dict] = []
    for c in clusters:
        scores = (
            db.query(ScoringResult)
            .filter(ScoringResult.cluster_id == c.id)
            .order_by(ScoringResult.rank.asc())
            .all()
        )
        for s in scores:
            lst = db.get(Listing, s.listing_id)
            if not lst:
                continue
            rows.append(
                {
                    "cluster": c.canonical_name,
                    "rank": int(s.rank),
                    "source": lst.source,
                    "title": lst.title,
                    "price": float(lst.price),
                    "currency": lst.currency,
                    "price_usd": float(lst.price_normalized_usd) if lst.price_normalized_usd else None,
                    "final_score": float(s.final_score),
                    "url": lst.url,
                }
            )

    fmt = export_format.lower()
    if fmt == "excel":
        import pandas as pd

        df = pd.DataFrame(rows)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="results")
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="procurement-{request_id}.xlsx"'},
        )

    if fmt == "pdf":
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 8, f"Procurement report — {request_id}", ln=True)
        pdf.cell(0, 8, f"Generated (UTC): {datetime.utcnow().isoformat()}Z", ln=True)
        pdf.ln(4)
        for r in rows[:200]:
            line = (
                f"#{r['rank']} {r['source']} | {r['title'][:80]} | "
                f"{r['price']} {r['currency']} | score {r['final_score']}"
            )
            pdf.multi_cell(0, 6, line)
            pdf.ln(1)
        data = pdf.output(dest="S")
        if isinstance(data, str):
            data = data.encode("latin-1")
        buf = io.BytesIO(data)
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="procurement-{request_id}.pdf"'},
        )

    raise HTTPException(status_code=400, detail="format must be pdf or excel")
