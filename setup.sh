#!/bin/bash

# Project name
PROJECT_NAME="autocollate-backend"

echo "Creating project structure for $PROJECT_NAME..."

# Create base directories
mkdir -p $PROJECT_NAME/{app,app/templates,app/static,app/schemas}
mkdir -p $PROJECT_NAME/{config,logs}
mkdir -p $PROJECT_NAME/{data,tests}

# Create essential files
touch $PROJECT_NAME/.env
touch $PROJECT_NAME/Dockerfile
touch $PROJECT_NAME/docker-compose.yml
touch $PROJECT_NAME/requirements.txt

# Create app files
cat << EOF > $PROJECT_NAME/app/__init__.py
# This file indicates that the app directory is a package.
EOF

cat << EOF > $PROJECT_NAME/app/main.py
import uvicorn
from fastapi import FastAPI
from app.db import engine
from app.models import Base

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def read_root():
    return {"message": "AutoCollate System Backend is Running"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
EOF

cat << EOF > $PROJECT_NAME/app/db.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session
EOF

cat << EOF > $PROJECT_NAME/app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ProcessedData(Base):
    __tablename__ = "processed_data"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, nullable=False)
    month = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
EOF

cat << EOF > $PROJECT_NAME/app/email_handler.py
import os
from imap_tools import MailBox, AND
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.data_processor import process_excel_file
from app.models import ProcessedData

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FOLDER = os.getenv("EMAIL_FOLDER", "INBOX")

async def process_emails(db: AsyncSession):
    with MailBox(EMAIL_HOST).login(EMAIL_USER, EMAIL_PASS) as mailbox:
        for msg in mailbox.fetch(AND(seen=False)):
            state, month = parse_subject(msg.subject.strip())
            for att in msg.attachments:
                if att.filename.endswith(".xlsx"):
                    content = process_excel_file(att.payload, att.filename)

                    new_data = ProcessedData(
                        state=state,
                        month=month,
                        content=content
                    )
                    db.add(new_data)
                    await db.commit()

def parse_subject(subject):
    parts = subject.split("-")
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return "Unknown", "Unknown"
EOF

cat << EOF > $PROJECT_NAME/app/data_processor.py
import pandas as pd
from io import BytesIO

def process_excel_file(file_content, filename):
    try:
        df = pd.read_excel(BytesIO(file_content))
        return df.to_csv(index=False)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return ""
EOF

cat << EOF > $PROJECT_NAME/requirements.txt
fastapi
uvicorn
sqlalchemy
asyncpg
pandas
openpyxl
imap-tools
EOF

cat << EOF > $PROJECT_NAME/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat << EOF > $PROJECT_NAME/docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: autocollate_db
    ports:
      - "5432:5432"

  backend:
    build: .
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/autocollate_db
      - EMAIL_HOST=imap.example.com
      - EMAIL_USER=email@example.com
      - EMAIL_PASS=yourpassword
      - EMAIL_FOLDER=INBOX
    ports:
      - "8000:8000"
EOF

cat << EOF > $PROJECT_NAME/.env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/autocollate_db
EMAIL_HOST=imap.example.com
EMAIL_USER=email@example.com
EMAIL_PASS=yourpassword
EMAIL_FOLDER=INBOX
EOF

echo "Project structure created successfully!"

echo "Next steps:"
echo "1. Navigate to the project directory: cd $PROJECT_NAME"
echo "2. Start the services: docker-compose up --build"
echo "3. Access the backend at http://localhost:8000"

#make the script executable 
# chmod +x setup.sh

#run the script
#./setup.sh

