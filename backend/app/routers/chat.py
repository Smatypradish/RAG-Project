from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import ChatRequest, ChatResponse
from app.database import get_db
from app.services.rag_pipeline import process_query

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    return process_query(request.question, db, request.session_id)
