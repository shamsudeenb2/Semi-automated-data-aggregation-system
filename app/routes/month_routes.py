from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db import get_db
from app.models.stateModel import ProcessedData

router = APIRouter()

@router.get("/months")
async def get_unique_states(db: AsyncSession = Depends(get_db)):
    query = select(ProcessedData.month).distinct()
    result = await db.execute(query)
    states = [row[0] for row in result.fetchall()]
    return {"states": states}
