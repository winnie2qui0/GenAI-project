import io
import uuid
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.listing import Listing
from app.models.product_cluster import ProductCluster
from app.models.scoring_result import ScoringResult

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{request_id}/export")
async def export_report(
    request_id: uuid.UUID,
    format: str = Query(..., pattern="^(pdf|excel)$"),
    db: AsyncSession = Depends(get_db),
):
    score_result = await db.execute(
        select(ScoringResult, Listing, ProductCluster)
        .join(Listing, ScoringResult.listing_id == Listing.id)
        .join(ProductCluster, ScoringResult.cluster_id == ProductCluster.id)
        .where(ScoringResult.request_id == request_id)
        .order_by(ScoringResult.rank)
    )
    rows = score_result.all()

    if not rows:
        raise HTTPException(status_code=404, detail="No results found for this request")

    if format == "excel":
        return _export_excel(rows, request_id)
    else:
        return _export_pdf(rows, request_id)


def _export_excel(rows: list[Any], request_id: uuid.UUID) -> StreamingResponse:
    import xlsxwriter

    buf = io.BytesIO()
    workbook = xlsxwriter.Workbook(buf, {"in_memory": True})
    ws = workbook.add_worksheet("Comparison")

    header_fmt = workbook.add_format({"bold": True, "bg_color": "#4472C4", "font_color": "#FFFFFF"})
    headers = [
        "Rank", "Product", "Source", "Cluster", "Price (USD)", "Lead Days",
        "Rating", "Reviews", "Price Score", "Delivery Score", "Rating Score",
        "Trust Score", "Final Score", "Anomalies", "URL",
    ]
    for col, h in enumerate(headers):
        ws.write(0, col, h, header_fmt)

    for row_idx, (sr, listing, cluster) in enumerate(rows, start=1):
        ws.write(row_idx, 0, sr.rank)
        ws.write(row_idx, 1, listing.title[:100])
        ws.write(row_idx, 2, listing.source)
        ws.write(row_idx, 3, cluster.canonical_name[:80])
        ws.write(row_idx, 4, float(listing.price_normalized_usd or 0))
        ws.write(row_idx, 5, listing.lead_time_days or "N/A")
        ws.write(row_idx, 6, float(listing.rating) if listing.rating else "N/A")
        ws.write(row_idx, 7, listing.review_count or 0)
        ws.write(row_idx, 8, float(sr.price_score))
        ws.write(row_idx, 9, float(sr.delivery_score))
        ws.write(row_idx, 10, float(sr.rating_score))
        ws.write(row_idx, 11, float(sr.trust_score))
        ws.write(row_idx, 12, float(sr.final_score))
        anomaly_count = len(sr.anomalies or [])
        ws.write(row_idx, 13, anomaly_count)
        ws.write(row_idx, 14, listing.url[:200])

    ws.set_column(1, 1, 40)
    ws.set_column(14, 14, 50)
    workbook.close()
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=procurement_{request_id}.xlsx"},
    )


def _export_pdf(rows: list[Any], request_id: uuid.UUID) -> StreamingResponse:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Procurement Comparison Report", styles["Title"]))
    elements.append(Paragraph(f"Request ID: {request_id}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    data = [["Rank", "Source", "Price USD", "Days", "Rating", "Final Score", "Anomalies"]]
    for sr, listing, cluster in rows[:20]:
        data.append([
            str(sr.rank),
            listing.source,
            f"${float(listing.price_normalized_usd or 0):.2f}",
            str(listing.lead_time_days or "?"),
            str(float(listing.rating) if listing.rating else "N/A"),
            f"{float(sr.final_score):.1f}",
            str(len(sr.anomalies or [])),
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EBF3FF")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(table)
    doc.build(elements)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=procurement_{request_id}.pdf"},
    )
