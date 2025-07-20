
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db import get_db
from app.models.stateModel import ProcessedData

router = APIRouter()

@router.get("/foreign-domestic")
async def delivery_type_breakdown(
    month: str = Query(..., description="e.g., 'March-2025'"),
    db: AsyncSession = Depends(get_db)
):
    
    # domestic_fields = sum([
    #     ProcessedData.small_env_dom,
    #     ProcessedData.large_env_dom,
    #     ProcessedData.small_packet_dom,
    #     ProcessedData.post_card_dom,
    #     ProcessedData.printed_paper_dom,
    #     ProcessedData.articles_of_blind_dom,
    # ])

    # foreign_fields = sum([
    #     ProcessedData.small_env_for,
    #     ProcessedData.large_env_for,
    #     ProcessedData.small_sacket_for,
    #     ProcessedData.post_card_for,
    #     ProcessedData.printed_paper_for,
    #     ProcessedData.articles_of_Blind_for,
    # ])

    # # By state
    # query = (
    #     select(
    #         ProcessedData.state,
    #         func.sum(domestic_fields).label("domestic"),
    #         func.sum(foreign_fields).label("foreign")
    #     )
    #     .where(ProcessedData.month == month)
    #     .group_by(ProcessedData.state)
    #     .order_by(ProcessedData.state)
    # )
    from sqlalchemy import select, func

    domestic_sum = sum([
        func.coalesce(ProcessedData.small_env_dom, 0),
        func.coalesce(ProcessedData.large_env_dom, 0),
        func.coalesce(ProcessedData.small_packet_dom, 0),
        func.coalesce(ProcessedData.post_card_dom, 0),
        func.coalesce(ProcessedData.printed_paper_dom, 0),
        func.coalesce(ProcessedData.articles_of_blind_dom, 0),
    ])

    foreign_sum = sum([
        func.coalesce(ProcessedData.small_env_for, 0),
        func.coalesce(ProcessedData.large_env_for, 0),
        func.coalesce(ProcessedData.small_sacket_for, 0),
        func.coalesce(ProcessedData.post_card_for, 0),
        func.coalesce(ProcessedData.printed_paper_for, 0),
        func.coalesce(ProcessedData.articles_of_Blind_for, 0),
    ])
    query = (
        select(
        ProcessedData.state,
        func.sum(domestic_sum).label("domestic"),
        func.sum(foreign_sum).label("foreign")
    )
    .where(ProcessedData.month == month)
    .group_by(ProcessedData.state)
    .order_by(ProcessedData.state)
    )


    result = await db.execute(query)
    data = result.all()

    # Calculate overall total
    total_domestic = sum(row[1] for row in data)
    total_foreign = sum(row[2] for row in data)
    total_mail = total_domestic+total_foreign

    return {
        "states": [
            {"state": row[0], "domestic": row[1], "foreign": row[2]}
            for row in data
        ],
        "total": [{
            "count": total_domestic,
             "name":"domestic",
             "fill" :"#190379"
            },
            {
             "count": total_mail,
             "name":"total",
             "fill" :"#E9F0F3"
            },
            {"count": total_foreign,
             "name":"foreign",
             "fill" :"#ECD051"
        }]
    }
