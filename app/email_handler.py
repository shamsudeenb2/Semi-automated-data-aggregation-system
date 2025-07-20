# import os
# import imaplib
# import email
# from imap_tools import MailBox, AND
# from app.data_processor import process_excel_file

# EMAIL_HOST = os.getenv("EMAIL_HOST")
# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASS = os.getenv("EMAIL_PASS")
# EMAIL_FOLDER = os.getenv("EMAIL_FOLDER", "INBOX")

# def process_emails():
#     with MailBox(EMAIL_HOST).login(EMAIL_USER, EMAIL_PASS) as mailbox:
#         # Fetch all unseen emails with attachments
#         for msg in mailbox.fetch(AND(seen=False)):
#             for att in msg.attachments:
#                 if att.filename.endswith(".xlsx"):
#                     process_excel_file(att.payload, att.filename)

import os
from imap_tools.mailbox import MailBox
from imap_tools.query import AND
from sqlalchemy.ext.asyncio import AsyncSession
from app.data_processing import process_excel_file 
# from app.models.stateModel import ProcessedData
# from app.notifications import notify_frontend
# import hashlib


EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FOLDER = os.getenv("EMAIL_FOLDER", "INBOX")

# fetched_ids = set()

async def process_emails(db: AsyncSession):
    print("Checking emails...")
    with MailBox("imap.gmail.com").login("kabirusproject@gmail.com", "ludn jqcc jjrc bwmy") as mailbox:
        print("email login")
        for msg in mailbox.fetch(AND(seen=False)):
            # hash_id = hashlib.sha256(msg.uid.encode()).hexdigest()
            # if hash_id in fetched_ids:
            #     continue
            # fetched_ids.add(hash_id)
            print("email login",msg.date)
            # Extract state and month from the subject
            subject = msg.subject.strip()
            state, month = parse_subject(subject)
            print("Completed extracting State and Month from email subject",state,month)

            attachment = msg.attachments[0]  # or loop through all attachments if needed
            file_bytes = attachment.payload
            # Process each attachment
            print("Start extracting xlsx file attachment")
            user = await process_excel_file(file_bytes,"email",state, month, db)
            print("file extracted and processed",user)
            # for att in msg.attachments:
            #     if att.filename.endswith(".xlsx"):
            #         content = process_excel_file(att.payload,"email",db)

            #         # Insert into database
            #         print("Inserting into database")
            #         new_data = ProcessedData(
            #             state=state,
            #             month=month,
            #             content=content
            #         )
            #         db.add(new_data)
            #         await db.commit()

            #         print("Completed insertion into database")
            #         # Notify frontend
                    

def parse_subject(subject: str):
    # Example: "Kano - January"
    print("Stating extracting State and Month from email subject",subject)
    parts = subject.split(" ")
    if len(parts) == 2:
        state, month = parts[0].strip(), parts[1].strip()
        return state, month
    return "Unknown", "Unknown"

# celery --app=app.celery_worker worker --concurrency=1 --loglevel=DEBUG
