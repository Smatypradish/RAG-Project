from datetime import date
from typing import List, Dict, Any
from app.database import DocumentRecord
from app.models import SourceEvidence

def calculate_reliability_score(chunk_result: Dict[str, Any], db_doc: DocumentRecord) -> float:
    raw_distance = chunk_result.get('distance', 1.5)
    
    # ChromaDB L2 distance normalization for all-MiniLM-L6-v2 (0.0 to 1.7 scale)
    semantic_relevance = max(0.0, min(1.0, 1.0 - (raw_distance / 1.6)))
    
    # Gating: If distance is very high (> 1.35), the chunk is out-of-domain
    if raw_distance > 1.35 or semantic_relevance < 0.20:
        return round(semantic_relevance * 0.15, 3)
        
    authority_normalized = min(5, max(1, db_doc.authority_level)) / 5.0
    
    validity_score = 0.0
    if db_doc.status == 'active':
        validity_score = 1.0
    elif db_doc.status == 'superseded':
        validity_score = 0.40
        
    recency_score = 0.5
    if db_doc.effective_date:
        days_old = (date.today() - db_doc.effective_date).days
        if days_old <= 365 * 2:
            recency_score = 1.0
        elif days_old <= 365 * 5:
            recency_score = 0.8
        else:
            recency_score = 0.5
            
    consistency_bonus = 1.0
    
    score = (semantic_relevance * 0.4) + (authority_normalized * 0.2) + (validity_score * 0.2) + (recency_score * 0.1) + (consistency_bonus * 0.1)
    return round(min(1.0, score), 3)

def classify_evidence(scored_chunks: List[SourceEvidence], conflict_info: List[Any]) -> str:
    if not scored_chunks:
        return "not_available"
        
    top_score = scored_chunks[0].relevance_score
    
    if top_score < 0.20:
        return "not_available"
    if top_score < 0.40:
        return "insufficient"
        
    active_sources = [c for c in scored_chunks if c.status == 'active' and c.relevance_score >= 0.35]
    
    if not active_sources:
        return "outdated"
        
    if conflict_info:
        return "conflicting"
        
    if top_score >= 0.55:
        return "verified"
        
    return "insufficient"

def filter_and_rank(chunks_with_metadata: List[Dict[str, Any]], db_session) -> List[SourceEvidence]:
    ranked = []
    for item in chunks_with_metadata:
        doc_id = item['metadata']['doc_id']
        db_doc = db_session.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
        
        if not db_doc or db_doc.status == 'withdrawn':
            continue
            
        score = calculate_reliability_score(item, db_doc)
        
        auth_labels = {1: "Committee", 2: "Department", 3: "Dean", 4: "Registrar", 5: "University"}
        
        evidence = SourceEvidence(
            document_name=db_doc.original_name,
            document_id=db_doc.id,
            page_number=item['metadata'].get('page_number', 1),
            section=item['metadata'].get('section_hint', 'General'),
            chunk_text=item['text'],
            authority_level=db_doc.authority_level,
            authority_label=auth_labels.get(db_doc.authority_level, "Unknown"),
            effective_date=str(db_doc.effective_date),
            status=db_doc.status,
            relevance_score=score
        )
        ranked.append(evidence)
        
    ranked.sort(key=lambda x: x.relevance_score, reverse=True)
    return ranked
