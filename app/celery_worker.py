# from celery import Celery
# import asyncio
# from app.utils.db import SessionLocal
# from app.email_handler import process_emails


# # celery_app = Celery(
# #     "autocollate",
# #     broker="redis://127.0.0.1:6379/0",  # Change this
# #     backend="redis://127.0.0.1:6379/0"
# # )
# celery_app = Celery(
#     "autocollate",
#     broker="memory://",
#     backend="rpc://"
# )

# celery_app.conf.beat_schedule = {
#     "check-email-every-10-minute": {
#         "task": "celery_app.tasks.check_email",
#         "schedule":600,  # 12 hours
#     }
# }

# celery_app.conf.timezone = "UTC"


# @celery_app.task
# def check_email():
#     async def _check():
#         async with SessionLocal() as db:
#             await process_emails(db)

#     print("celery task ...")
#     try:
#         asyncio.run(_check())
#         print("Email processing task completed successfully.")
#     except Exception as e:
#         print(f"Error in check_email task: {e}")

# # @celery_app.task
# # def check_email():
# #     from app.main import app
# #     # print("Email processing task completed.")
# #     with app.container.get(AsyncSession)() as db:
# #         try:
# #             # Process emails and insert data
# #             db.run_until_complete(process_emails(db))
# #             print("Email processing task completed successfully.")
# #         except Exception as e:
# #             print(f"Error in check_email task: {e}")
            
# if __name__ == "__main__":
#     print("Starting Celery Worker...")
#     celery_app.start()


# # from celery import Celery
# # from sqlalchemy.ext.asyncio import AsyncSession
# # from app.db import get_db
# # from app.email_handler import process_emails

# # # Initialize Celery
# # celery_app = Celery("tasks", broker="redis://redis:6379/0")

# # @celery_app.task
# # def check_email():
# #     """
# #     Task to check emails and process attachments.
# #     This function will be scheduled to run twice a day.
# #     """
# #     from app.main import app

# #     # Create an application context to use the DB session
# #     with app.container.get(AsyncSession)() as db:
# #         # Run the email processing function
# #         db.run_until_complete(process_emails(db))

# #     print("Email processing task completed.")


# from celery import Celery

# celery_app = Celery(
#     "autocollate",
#     broker="redis://127.0.0.1:6379/0",  # Or use docker container name like "redis://redis:6379/0"
#     backend="redis://127.0.0.1:6379/0"
# )

# celery_app.autodiscover_tasks(["app"])
# celery_app.conf.timezone = "UTC"

# celery_app.conf.beat_schedule = {
#     "check-email-every-10-minutes": {
#         "task": "app.tasks.check_email",  # Update to correct module path
#         "schedule": 600.0,  # 10 minutes
#     },
# }

# app/celery.py
# from celery import Celery
# import asyncio
# from app.utils.db import SessionLocal
# from app.email_handler import process_emails

# celery_app = Celery(
#     "autocollate",
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/0"
# )

# celery_app.conf.timezone = "UTC"

# celery_app.conf.beat_schedule = {
#     "check-email-every-10-minute": {
#         "task": "app.celery.check_email",
#         "schedule": 600,  # every 10 minutes
#     }
# }

# @celery_app.task
# def check_email():
#     async def _check():
#         async with SessionLocal() as db:
#             await process_emails(db)

#     try:
#         asyncio.run(_check())
#         print("✅ Email check completed")
#     except Exception as e:
#         print(f"❌ Error during email check: {e}")

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.celery import celery_app

if __name__ == "__main__":
    celery_app.worker_main(argv=["worker", "--loglevel=info"])
