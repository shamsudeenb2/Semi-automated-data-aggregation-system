
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import defaultdict
from datetime import datetime

from app.utils.db import get_db
from app.models.stateModel import ProcessedData
from app.utils.stateList import STATE_OFFICES

router = APIRouter()

@router.get("/missed-state")
async def get_missed_reports(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    sort_by: str = Query("state", pattern="^(state|missing_month)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    filter_state: str = Query(None),
    filter_month: str = Query(None),
):
    current_month_str = datetime.now().strftime("%B-%Y")
    result_all = await db.execute(select(ProcessedData.state, ProcessedData.month))
    all_records = result_all.fetchall()

    state_months = defaultdict(set)
    for state, month in all_records:
        state_months[state].add(month)

    all_months = sorted({record[1] for record in all_records if record[1] != current_month_str})

    missed_submissions = []
    for state in STATE_OFFICES:
        submitted = state_months.get(state, set())
        for month in all_months:
            if month not in submitted:
                missed_submissions.append({"state": state, "missing_month": month})

    if filter_state:
        missed_submissions = [r for r in missed_submissions if r["state"] == filter_state]
    if filter_month:
        missed_submissions = [r for r in missed_submissions if r["missing_month"] == filter_month]

    reverse = order == "desc"
    missed_submissions.sort(key=lambda x: x[sort_by], reverse=reverse)

    total = len(missed_submissions)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = missed_submissions[start:end]

    return {
        "missed_previous_months": paginated,
        "total_missed": total,
        "page": page,
        "page_size": page_size
    }
