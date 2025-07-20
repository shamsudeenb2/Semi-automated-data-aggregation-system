from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db import get_db
from app.models.stateModel import ProcessedData
from app.utils.aggregation import coalesced_sum

router = APIRouter()

@router.get("/files/months-summary")
async def get_state_summary_by_month(
    state: str,
    db: AsyncSession = Depends(get_db)
):
   
    # Fields to sum
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
    
     query = select(
        ProcessedData.month,
        func.sum(total_mail_expr).label("total_items")
     ).where(
        ProcessedData.state == state
     ).group_by(ProcessedData.month).order_by(ProcessedData.month)
     
     result = await db.execute(query)
     data = result.all()
     
     return [{"name": row[0], "totalQty": row[1]} for row in data]
