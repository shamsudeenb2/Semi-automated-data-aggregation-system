from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.stateModel import ProcessedData
import pandas as pd
from app.utils.db import get_db
from io import StringIO
from datetime import datetime

router = APIRouter()

@router.get("/download-report/")
async def download_report(
    start_month: str = Query(..., description="Start month in YYYY-MM format"),
    end_month: str = Query(..., description="End month in YYYY-MM format"),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Convert to comparable string for filtering (or use date if needed)
        start = datetime.strptime(start_month, "%B-%Y")
        end = datetime.strptime(end_month, "%B-%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM.")

    stmt = select(ProcessedData).where(ProcessedData.month >= start_month, ProcessedData.month <= end_month)
    result = await db.execute(stmt)
    records = result.scalars().all()

    if not records:
        raise HTTPException(status_code=404, detail="No data found for the given month range.")
    
    print(start, end)
    # Convert to DataFrame
    df = pd.DataFrame([{
        "state": r.state,
        "month": r.month,
        "sheet_name": r.sheet_name,
        "postoffice":r.postoffice,
        "small_env_dom": r.small_env_dom,
        "small_env_for": r.small_env_for,
        "large_env_dom": r.large_env_dom,
        "large_env_for": r.large_env_for,
        "post_card_dom": r.post_card_dom,
        "post_card_for": r.post_card_for,
        "small_packet_dom": r.small_packet_dom,
        "small_packet_for": r.small_sacket_for,
        "printed_paper_dom": r.printed_paper_dom,
        "printed_paper_for": r.printed_paper_for,
        "articles_of_blind_dom": r.articles_of_blind_dom,
        "articles_of_Blind_for": r.articles_of_Blind_for,
        "uploaded_type": r.uploaded_type,
    } for r in records])

    # Convert to CSV
    buffer = StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    filename = f"report_{start_month}_to_{end_month}.csv"
    return StreamingResponse(buffer, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })
