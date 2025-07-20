from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db import get_db
from app.models.stateModel import ProcessedData
from app.utils.aggregation import coalesced_sum

router = APIRouter()

@router.get("/postoffices-by-state-month")
async def get_postoffices_by_state_month(
    state: str = Query(..., description="e.g., 'Lagos'"),
    month: str = Query(..., description="e.g., 'March-2025'"),
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
            ProcessedData.postoffice,
            func.sum(total_mail_expr).label("total_items")
        )
        .where(ProcessedData.state == state, ProcessedData.month == month)
        .group_by(ProcessedData.postoffice)
        .order_by(ProcessedData.postoffice)
    )

    result = await db.execute(query)
    data = result.all()

    return [{"name": row[0], "totalQty": row[1]} for row in data]
