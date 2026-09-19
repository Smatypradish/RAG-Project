from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ChatRequest, ChatResponse
from app.services.rag_pipeline import process_query

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        return process_query(request.question.strip(), db, request.session_id)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The assistant could not process this question. Please try again.",
        ) from exc
