from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.utils.db import get_db
from app.models.stateModel import ProcessedData
from app.utils.aggregation import coalesced_sum # This handles summing nullable fields

router = APIRouter()

@router.get("/mail-summary")
async def get_mail_summary(db: AsyncSession = Depends(get_db)):
    # Get current month and year in your format
    now = datetime.now()
    current_month = now.strftime("%B-%Y")  # e.g., "July-2025"
    current_year = now.strftime("%Y")

    # All mail volume fields
    mail_fields = [
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
    total_mail_expr = coalesced_sum(mail_fields)

    # This month
    this_month_query = select(func.sum(total_mail_expr)).where(ProcessedData.month == current_month)
    this_month_result = await db.execute(this_month_query)
    total_this_month = this_month_result.scalar() or 0

    # This year
    this_year_query = select(func.sum(total_mail_expr)).where(ProcessedData.month.like(f"%-{current_year}"))
    this_year_result = await db.execute(this_year_query)
    total_this_year = this_year_result.scalar() or 0

    # Via email
    email_query = select(func.sum(total_mail_expr)).where(ProcessedData.uploaded_type == "email")
    email_result = await db.execute(email_query)
    total_via_email = email_result.scalar() or 0

    # Via upload
    upload_query = select(func.sum(total_mail_expr)).where(ProcessedData.uploaded_type == "uploaded")
    upload_result = await db.execute(upload_query)
    total_via_upload = upload_result.scalar() or 0

    return {
        "total_this_month": total_this_month,
        "total_this_year": total_this_year,
        "total_via_email": total_via_email,
        "total_via_upload": total_via_upload,
    }
