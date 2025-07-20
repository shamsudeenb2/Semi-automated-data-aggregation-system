# from celery import shared_task
# import asyncio
# from app.utils.db import SessionLocal
# from app.email_handler import process_emails

# @shared_task(name="app.tasks.check_email")
# def check_email():
#     async def _check():
#         async with SessionLocal() as db:
#             await process_emails(db)

#     try:
#         print("Running Celery email check task...")
#         asyncio.run(_check())
#         print("✅ Email processing task completed.")
#     except Exception as e:
#         print(f"❌ Error in Celery check_email task: {e}")
