from fastapi import APIRouter, Depends
from sqlalchemy import select, func, extract,distinct
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.utils.db import get_db
from app.models.stateModel import ProcessedData

router = APIRouter()

@router.get("/files/count-by-type")
async def count_files_by_type_this_year(db: AsyncSession = Depends(get_db)):
    now = datetime.now()
    current_year = now.year
    current_month = now.month

# Count distinct states via upload this year
    upload_query = select(func.count(distinct(ProcessedData.state))).where( 
        ProcessedData.uploaded_type == "uploaded",
        extract("year", ProcessedData.uploaded_at) == current_year
    )
    upload_result = await db.execute(upload_query)
    upload_count = upload_result.scalar()

    # Count distinct states via email this year
    email_query = select(func.count(distinct(ProcessedData.state))).where(
        ProcessedData.uploaded_type == "email",
        extract("year", ProcessedData.uploaded_at) == current_year
    )
    email_result = await db.execute(email_query)
    email_count = email_result.scalar()

    # Count distinct states submitted this year
    total_year_query = select(func.count(distinct(ProcessedData.state))).where(
        extract("year", ProcessedData.uploaded_at) == current_year
    )
    total_year_result = await db.execute(total_year_query)
    total_this_year = total_year_result.scalar()

    # Count distinct states submitted this month
    total_month_query = select(func.count(distinct(ProcessedData.state))).where(
        extract("year", ProcessedData.uploaded_at) == current_year,
        extract("month", ProcessedData.uploaded_at) == current_month
    )
    total_month_result = await db.execute(total_month_query)
    total_this_month = total_month_result.scalar()


    return {
        "upload_count": upload_count,
        "email_count": email_count,
        "total_this_year": total_this_year,
        "total_this_month": total_this_month
        }

