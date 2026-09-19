import hmac
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import issue_token, require_admin
from app.config import get_settings
from app.database import DocumentRecord, QueryLog, get_db
from app.models import AdminStats, LoginRequest, LoginResponse
from app.services.vector_store import VectorStoreService

logger = logging.getLogger("admin")
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    settings = get_settings()
    # Fail closed: refuse all logins when no admin password is configured.
    if not settings.admin_password:
        logger.warning("Login attempt rejected: ADMIN_PASSWORD is not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin login is disabled until ADMIN_PASSWORD is configured.",
        )
    valid_user = hmac.compare_digest(req.username.strip(), settings.admin_username)
    valid_pass = hmac.compare_digest(req.password, settings.admin_password)
    if not (valid_user and valid_pass):
        logger.info(
            "Failed login for username=%r (expected %r)",
            req.username, settings.admin_username,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    logger.info("Admin login successful for %r", settings.admin_username)
    return LoginResponse(
        token=issue_token(settings.admin_username),
        message="Login successful",
    )


@router.get("/stats", response_model=AdminStats)
def get_stats(db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    total_docs = db.query(DocumentRecord).count()
    active_docs = db.query(DocumentRecord).filter(DocumentRecord.status == "active").count()
    total_queries = db.query(QueryLog).count()

    vec_store = VectorStoreService()
    stats = vec_store.get_collection_stats()

    return AdminStats(
        total_documents=total_docs,
        active_documents=active_docs,
        total_chunks=stats.get("count", 0),
        total_queries=total_queries,
    )

