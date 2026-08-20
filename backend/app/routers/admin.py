from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import AdminStats, LoginRequest, LoginResponse
from app.database import get_db, DocumentRecord, QueryLog
from app.config import get_settings
from app.services.vector_store import VectorStoreService

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    settings = get_settings()
    if req.username == settings.admin_username and req.password == settings.admin_password:
        return {"token": "fake-jwt-token-123", "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/stats", response_model=AdminStats)
def get_stats(db: Session = Depends(get_db)):
    total_docs = db.query(DocumentRecord).count()
    active_docs = db.query(DocumentRecord).filter(DocumentRecord.status == "active").count()
    total_queries = db.query(QueryLog).count()
    
    vec_store = VectorStoreService()
    stats = vec_store.get_collection_stats()
    
    return AdminStats(
        total_documents=total_docs,
        active_documents=active_docs,
        total_chunks=stats.get("count", 0),
        total_queries=total_queries
    )
