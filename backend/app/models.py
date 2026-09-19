from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional, List

class DocumentUploadMetadata(BaseModel):
    category: str
    authority_level: int
    version: str
    effective_date: date
    expiry_date: Optional[date] = None
    status: str = "active"
    parent_document_id: Optional[int] = None
    supersedes_document_id: Optional[int] = None
    revision_reason: Optional[str] = None

class DocumentResponse(BaseModel):
    id: int
    file_name: str
    original_name: str
    category: str
    authority_level: int
    version: str
    effective_date: date
    expiry_date: Optional[date]
    status: str
    parent_document_id: Optional[int]
    supersedes_document_id: Optional[int]
    revision_reason: Optional[str]
    uploaded_by: str
    upload_date: datetime
    total_chunks: int
    file_path: str
    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: Optional[str] = Field(default=None, max_length=100)

class SourceEvidence(BaseModel):
    document_name: str
    document_id: int
    page_number: int
    section: str
    chunk_text: str
    authority_level: int
    authority_label: str
    effective_date: str
    status: str
    relevance_score: float

class ConflictInfo(BaseModel):
    topic: str
    source_a: SourceEvidence
    source_b: SourceEvidence
    resolution: str
    explanation: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceEvidence]
    confidence_score: float
    classification: str
    conflicts: List[ConflictInfo]
    session_id: Optional[str]

class AdminStats(BaseModel):
    total_documents: int
    active_documents: int
    total_chunks: int
    total_queries: int

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    message: str
