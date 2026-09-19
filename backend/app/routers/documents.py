import os
import shutil
import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.config import get_settings
from app.database import DocumentRecord, get_db
from app.models import DocumentResponse
from app.services.document_processor import (
    chunk_text,
    extract_text_from_docx,
    extract_text_from_pdf,
    extract_text_from_txt,
)
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(require_admin)],
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
VALID_STATUSES = {"active", "superseded", "withdrawn"}
ALLOWED_CATEGORIES = {"academic", "examination", "hostel", "admission", "general"}


def _safe_storage_name(original_name: str) -> str:
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload PDF, DOCX, TXT, or MD.",
        )
    return f"{uuid.uuid4().hex}{ext}"


def _validate_metadata(
    category: str,
    authority_level: int,
    status: str,
    effective_date: date,
    expiry_date: Optional[date],
) -> None:
    if category.lower() not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}.",
        )
    if not 1 <= authority_level <= 5:
        raise HTTPException(status_code=400, detail="Authority level must be between 1 and 5.")
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}.",
        )
    if expiry_date is not None and expiry_date <= effective_date:
        raise HTTPException(status_code=400, detail="Expiry date must be after the effective date.")


def _validate_references(
    db: Session, parent_document_id: Optional[int], supersedes_document_id: Optional[int]
) -> None:
    for label, ref_id in (
        ("Parent", parent_document_id),
        ("Superseded", supersedes_document_id),
    ):
        if ref_id is not None and not db.query(DocumentRecord).filter(DocumentRecord.id == ref_id).first():
            raise HTTPException(status_code=400, detail=f"{label} document id {ref_id} does not exist.")


def _extract_pages(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    return extract_text_from_txt(file_path)


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    authority_level: int = Form(...),
    version: str = Form(...),
    effective_date: date = Form(...),
    expiry_date: date = Form(None),
    status: str = Form("active"),
    parent_document_id: int = Form(None),
    supersedes_document_id: int = Form(None),
    revision_reason: str = Form(None),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    original_name = os.path.basename(file.filename or "").strip()
    if not original_name:
        raise HTTPException(status_code=400, detail="File name is missing.")

    storage_name = _safe_storage_name(original_name)
    _validate_metadata(category, authority_level, status, effective_date, expiry_date)
    _validate_references(db, parent_document_id, supersedes_document_id)

    file_path = os.path.join(UPLOAD_DIR, storage_name)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    written = 0
    try:
        with open(file_path, "wb") as buffer:
            while True:
                block = file.file.read(1024 * 1024)
                if not block:
                    break
                written += len(block)
                if written > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds the {settings.max_upload_size_mb} MB limit.",
                    )
                buffer.write(block)
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise

    doc_record = DocumentRecord(
        file_name=storage_name,
        original_name=original_name,
        category=category.lower(),
        authority_level=authority_level,
        version=version,
        effective_date=effective_date,
        expiry_date=expiry_date,
        status=status,
        parent_document_id=parent_document_id,
        supersedes_document_id=supersedes_document_id,
        revision_reason=revision_reason,
        file_path=file_path,
    )

    try:
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        if supersedes_document_id:
            old_doc = db.query(DocumentRecord).filter(
                DocumentRecord.id == supersedes_document_id
            ).first()
            if old_doc:
                old_doc.status = "superseded"
                db.commit()

        pages_text = _extract_pages(file_path)
        if not pages_text:
            raise HTTPException(
                status_code=422,
                detail="No readable text could be extracted from the file.",
            )

        chunks = chunk_text(
            pages_text,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
            doc_id=doc_record.id,
            doc_name=doc_record.original_name,
        )
        doc_record.total_chunks = len(chunks)
        db.commit()

        if chunks:
            emb_service = EmbeddingService()
            embeddings = emb_service.embed_texts([c["chunk_text"] for c in chunks])
            vec_store = VectorStoreService()
            vec_store.add_chunks(doc_record.id, chunks, embeddings)
    except Exception as exc:
        db.rollback()
        existing = db.get(DocumentRecord, doc_record.id) if doc_record.id else None
        if existing:
            db.delete(existing)
            db.commit()
        if os.path.exists(file_path):
            os.remove(file_path)
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Document processing failed: {exc}")

    return doc_record

@router.get("", response_model=List[DocumentResponse], include_in_schema=False)
@router.get("/", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return db.query(DocumentRecord).order_by(DocumentRecord.upload_date.desc()).all()


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(doc_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}.",
        )
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.status = status
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    vec_store = VectorStoreService()
    vec_store.delete_document(doc_id)

    db.delete(doc)
    db.commit()

    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    return {"detail": "Document deleted"}
