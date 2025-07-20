# app/celery.py
from celery import Celery
import asyncio
from app.utils.db import SessionLocal
from app.email_handler import process_emails

celery_app = Celery(
    "autocollate",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "check-email-every-5-minute": {
        "task": "app.celery.check_email",
        "schedule": 300,  # every 10 minutes
    }
}

@celery_app.task
def check_email():
    async def _check():
        async with SessionLocal() as db:
            await process_emails(db)

    try:
        asyncio.run(_check())
        print("✅ Email check completed")
    except Exception as e:
        print(f"❌ Error during email check: {e}")
