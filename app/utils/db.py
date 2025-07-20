from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine("postgresql+asyncpg://postgres:1234@localhost:5432/autocollate_db", echo=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with SessionLocal() as session:
        yield session


# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# import os

# DATABASE_URL = os.getenv("DATABASE_URL")

# engine = create_async_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base = declarative_base()

# async def get_db():
#     async with SessionLocal() as session:
#         yield session
