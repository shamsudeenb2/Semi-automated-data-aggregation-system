# from sqlalchemy import Column, Integer, String, Text, DateTime
# from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(55), nullable=False)
    phone_number = Column(Integer, unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    username = Column(String(55), unique=True, nullable=False)
    role = Column(String(55), nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    

class ProcessedData(Base):
    __tablename__ = "processed_data"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, nullable=False)
    postoffice =Column(String, nullable=False)
    month = Column(String, nullable=False)
    sheet_name = Column(String, nullable=False)
    small_env_dom = Column(Integer)
    small_env_for = Column(Integer)
    large_env_dom = Column(Integer)
    large_env_for = Column(Integer)
    small_packet_dom= Column(Integer)
    small_sacket_for= Column(Integer)
    post_card_dom= Column(Integer)
    post_card_for= Column(Integer)
    printed_paper_dom= Column(Integer)
    printed_paper_for= Column(Integer)
    articles_of_blind_dom= Column(Integer)
    articles_of_Blind_for= Column(Integer)

    uploaded_type = Column(String, nullable=False )
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
