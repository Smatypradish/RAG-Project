import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import get_db, DocumentRecord
from app.models import DocumentResponse
from app.services.document_processor import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt, chunk_text
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    db: Session = Depends(get_db)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    doc_record = DocumentRecord(
        file_name=file.filename,
        original_name=file.filename,
        category=category,
        authority_level=authority_level,
        version=version,
        effective_date=effective_date,
        expiry_date=expiry_date,
        status=status,
        parent_document_id=parent_document_id,
        supersedes_document_id=supersedes_document_id,
        revision_reason=revision_reason,
        file_path=file_path
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)
    
    if supersedes_document_id:
        old_doc = db.query(DocumentRecord).filter(DocumentRecord.id == supersedes_document_id).first()
        if old_doc:
            old_doc.status = "superseded"
            db.commit()
            
    if file.filename.lower().endswith(".pdf"):
        pages_text = extract_text_from_pdf(file_path)
    elif file.filename.lower().endswith(".docx"):
        pages_text = extract_text_from_docx(file_path)
    elif file.filename.lower().endswith((".txt", ".md")):
        pages_text = extract_text_from_txt(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or TXT.")
        
    chunks = chunk_text(pages_text, doc_id=doc_record.id, doc_name=doc_record.original_name)
    doc_record.total_chunks = len(chunks)
    db.commit()
    
    if chunks:
        emb_service = EmbeddingService()
        embeddings = emb_service.embed_texts([c['chunk_text'] for c in chunks])
        vec_store = VectorStoreService()
        vec_store.add_chunks(doc_record.id, chunks, embeddings)
        
    return doc_record

@router.get("/", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return db.query(DocumentRecord).all()

@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(doc_id: int, status: str = Form(...), db: Session = Depends(get_db)):
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
    return {"detail": "Document deleted"}
