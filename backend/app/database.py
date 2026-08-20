import os
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./rag_chatbot.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DocumentRecord(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String, index=True)
    original_name = Column(String)
    category = Column(String)
    authority_level = Column(Integer)
    version = Column(String)
    effective_date = Column(Date)
    expiry_date = Column(Date, nullable=True)
    status = Column(String, default="active")
    parent_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    supersedes_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    revision_reason = Column(String, nullable=True)
    uploaded_by = Column(String, default="admin")
    upload_date = Column(DateTime, default=datetime.utcnow)
    total_chunks = Column(Integer, default=0)
    file_path = Column(String)

class QueryLog(Base):
    __tablename__ = "query_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question = Column(String)
    answer = Column(String)
    classification = Column(String)
    confidence_score = Column(Float)
    sources_used = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
