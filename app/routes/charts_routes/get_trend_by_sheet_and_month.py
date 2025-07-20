from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db import get_db
from app.models.stateModel import ProcessedData
from app.utils.aggregation import coalesced_sum

router = APIRouter()


@router.get("/sheet-usage-trend")
async def get_sheet_usage_trend(
    state: str = Query(..., description="e.g., 'Kano'"),
    db: AsyncSession = Depends(get_db)
):
    fields = [
        ProcessedData.small_env_dom,
        ProcessedData.small_env_for,
        ProcessedData.large_env_dom,
        ProcessedData.large_env_for,
        ProcessedData.small_packet_dom,
        ProcessedData.small_sacket_for,
        ProcessedData.post_card_dom,
        ProcessedData.post_card_for,
        ProcessedData.printed_paper_dom,
        ProcessedData.printed_paper_for,
        ProcessedData.articles_of_blind_dom,
        ProcessedData.articles_of_Blind_for,
    ]

    total_mail_expr = coalesced_sum(fields)

    query = (
        select(
            ProcessedData.month,
            ProcessedData.sheet_name,
            func.sum(total_mail_expr).label("total_items")
        )
        .where(ProcessedData.state == state)
        .group_by(ProcessedData.month, ProcessedData.sheet_name)
        .order_by(ProcessedData.month, ProcessedData.sheet_name)
    )

    result = await db.execute(query)
    rows = result.all()

    # Aggregation
    month_totals = {}
    sheet_totals = {}
    grand_total = 0

    for month, sheet_name, total_items in rows:
        count = total_items or 0
        grand_total += count

        if month not in month_totals:
            month_totals[month] = 0
        month_totals[month] += count

        if sheet_name not in sheet_totals:
            sheet_totals[sheet_name] = 0
        sheet_totals[sheet_name] += count

    # Response format
    month_response = [
        {
            "name": month,
            "totalForMonth": total,
            "total": grand_total
        }
        for month, total in month_totals.items()
    ]

    sheet_response = [
        {
            "name": sheet,
            "totalForSheet": total,
            "total": grand_total
        }
        for sheet, total in sheet_totals.items()
    ]

    return {
        "month": month_response,
        "sheet_name": sheet_response
    }

