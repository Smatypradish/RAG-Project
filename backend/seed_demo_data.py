import os
import sys
from datetime import date

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, SessionLocal, DocumentRecord
from app.services.document_processor import extract_text_from_txt, chunk_text
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService

def seed():
    print("Initializing Database...")
    init_db()
    db = SessionLocal()
    
    # Check if already seeded
    count = db.query(DocumentRecord).count()
    if count > 0:
        print(f"Database already contains {count} documents. Resetting database and ChromaDB...")
        db.query(DocumentRecord).delete()
        db.commit()
    
    vec_store = VectorStoreService()
    emb_service = EmbeddingService()
    
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sample_documents")
    
    docs_to_seed = [
        {
            "filename": "academic_regulations_2024.txt",
            "original_name": "Academic Regulations 2024-2025 (v1.0)",
            "category": "academic",
            "authority_level": 5,
            "version": "v1.0",
            "effective_date": date(2024, 7, 1),
            "status": "superseded",
            "parent_document_id": None,
            "supersedes_document_id": None,
            "revision_reason": None,
        },
        {
            "filename": "academic_regulations_2026.txt",
            "original_name": "Revised Academic Regulations 2026-2027 (v2.0)",
            "category": "academic",
            "authority_level": 5,
            "version": "v2.0",
            "effective_date": date(2026, 7, 1),
            "status": "active",
            "parent_document_id": None,
            "supersedes_document_id": 1,  # Will link to doc 1
            "revision_reason": "Deadline extended to September 15, updated attendance and scholarship thresholds",
        },
        {
            "filename": "exam_circular_fall_2026.txt",
            "original_name": "Controller of Examinations Circular - Fall 2026",
            "category": "examination",
            "authority_level": 4,
            "version": "v1.0",
            "effective_date": date(2026, 8, 5),
            "status": "active",
            "parent_document_id": None,
            "supersedes_document_id": None,
            "revision_reason": None,
        }
    ]
    
    for idx, doc_meta in enumerate(docs_to_seed, start=1):
        file_path = os.path.join(sample_dir, doc_meta["filename"])
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue
            
        print(f"\nProcessing [{idx}/3]: {doc_meta['original_name']}...")
        pages_text = extract_text_from_txt(file_path)
        
        doc_record = DocumentRecord(
            file_name=doc_meta["filename"],
            original_name=doc_meta["original_name"],
            category=doc_meta["category"],
            authority_level=doc_meta["authority_level"],
            version=doc_meta["version"],
            effective_date=doc_meta["effective_date"],
            status=doc_meta["status"],
            parent_document_id=doc_meta["parent_document_id"],
            supersedes_document_id=doc_meta["supersedes_document_id"],
            revision_reason=doc_meta["revision_reason"],
            file_path=file_path
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        
        chunks = chunk_text(pages_text, chunk_size=800, overlap=150, doc_id=doc_record.id, doc_name=doc_record.original_name)
        doc_record.total_chunks = len(chunks)
        db.commit()
        
        print(f" -> Generated {len(chunks)} chunks. Creating Sentence-Transformers embeddings...")
        embeddings = emb_service.embed_texts([c['chunk_text'] for c in chunks])
        
        print(" -> Storing in ChromaDB...")
        vec_store.add_chunks(doc_record.id, chunks, embeddings)
        print(f" -> Successfully ingested Document #{doc_record.id}")

    db.close()
    print("\n[SUCCESS] Seed completed successfully! All 3 demo documents are indexed.")

if __name__ == "__main__":
    seed()
