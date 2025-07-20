# import pandas as pd
# from io import BytesIO

# def process_excel_file(file_content, filename):
#     try:
#         # Read the Excel file
#         df = pd.read_excel(BytesIO(file_content))

#         # Example processing
#         # Perform data cleaning, validation, and formatting here
#         print(f"Processing file: {filename}")
#         print(df.head())

#         # Save to database and CSV
#         # Implement database logic here

#     except Exception as e:
#         print(f"Error processing {filename}: {e}")


# import pandas as pd
# from io import BytesIO

# def process_excel_file(file_content, filename): # type: ignore
#     print("Start extracting xlsx file content")
#     try:
#         df = pd.read_excel(BytesIO(file_content)) # type: ignore
#         # Convert DataFrame to a string representation
#         print("Completed extracting xlsx file content")
#         return df.to_csv(index=False)
#     except Exception as e:
#         print(f"Error processing {filename}: {e}")
#         return ""

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.stateModel import ProcessedData
from fastapi import UploadFile
from imap_tools import MailAttachment
from app.notifications import notify_frontend
from app.utils.validate_excel_file import validate_and_clean_excel_sheet
from io import BytesIO
from sqlalchemy import select,and_

SHEET_NAMES = ["postmen", "counter", "PMB", "Boxes"]

async def process_excel_file(file:UploadFile | bytes, uploaded_type: str,state:str, month:str, db: AsyncSession):
    print("processed function variables")
    print(f"state: {state}, month: {month}")
    # year_month = convert_month_name_to_yyyymm(month)
    statement = select(ProcessedData).where(and_(ProcessedData.state == state,ProcessedData.month ==month )).limit(1)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    if user:
        print("it is true")
        return "state and month already exist"


    # xls = pd.ExcelFile(file.file)
    
    if uploaded_type == "email":
        xls = pd.ExcelFile(BytesIO(file))
    
    if uploaded_type =="uploaded":
        content = await file.read()
        xls = pd.ExcelFile(BytesIO(content))   

    
    for sheet in SHEET_NAMES:
        if sheet not in xls.sheet_names:
            continue

        df = pd.read_excel(xls, sheet_name=sheet, header=None)
        try:
            clean_df = validate_and_clean_excel_sheet(df)
        except ValueError as e:
            print(f"Skipping sheet '{sheet}': {e}")
            continue

        # df.rename(columns=lambda col: col.strip(), inplace=True)
        # df.rename(columns=COLUMN_MAPPING, inplace=True)

        print("sheets",sheet)
        print("validation result",clean_df)
        for _, row in clean_df.iterrows():
            if not row.get("postoffices") or not row.get("small_env_dom"):
                continue

            new_data = ProcessedData(
                state=state,
                month=month,
                postoffice=row.get('postoffices'),
                sheet_name=sheet,
                small_env_dom=row.get("small_env_dom"),
                small_env_for=row.get("small_env_for"),
                large_env_dom=row.get("large_env_dom"),
                large_env_for=row.get("large_env_for"),
                post_card_dom=row.get("post_card_dom"),
                post_card_for=row.get("post_card_for"),
                small_packet_dom=row.get("small_packet_dom"),
                small_sacket_for=row.get("small_sacket_for"),
                printed_paper_dom=row.get("printed_paper_dom"),
                printed_paper_for=row.get("printed_paper_for"),
                articles_of_blind_dom=row.get("articles_of_blind_dom"),
                articles_of_Blind_for=row.get("articles_of_Blind_for"),
                uploaded_type=uploaded_type,
            )
            db.add(new_data)
           
    await db.commit()

    print("Sending notification")
    return "File processed successfully"


from datetime import datetime

# def convert_month_name_to_yyyymm(month_name: str) -> str:
#     try:
#         # Parse the full month name using current year
#         dt = datetime.strptime(month_name.strip(), "%B")
#         return f"{datetime.now().year}-{dt.month:02d}"  # Format as YYYY-MM
#     except ValueError:
#         raise ValueError(f"Invalid month name: {month_name}")

