from sqlalchemy.orm import Session
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.verification_engine import filter_and_rank, classify_evidence
from app.services.conflict_detector import detect_conflicts
from app.services.llm_service import LLMService
from app.models import ChatResponse
from app.database import QueryLog

def process_query(question: str, db_session: Session, session_id: str = None) -> ChatResponse:
    emb_service = EmbeddingService()
    vec_store = VectorStoreService()
    llm = LLMService()
    
    query_emb = emb_service.embed_query(question)
    raw_chunks = vec_store.search(query_emb, top_k=5)
    ranked_evidence = filter_and_rank(raw_chunks, db_session)
    conflicts = detect_conflicts(ranked_evidence)
    classification = classify_evidence(ranked_evidence, conflicts)
    
    context_str = ""
    for ev in ranked_evidence[:3]:
        context_str += f"[Doc: {ev.document_name} | Auth: {ev.authority_label} | Date: {ev.effective_date} | Status: {ev.status}]\n{ev.chunk_text}\n\n"
        
    conflicts_str = "\n".join([f"Conflict: {c.topic}, Resolution: {c.resolution}" for c in conflicts])
    
    answer = "The required information was not found in the available documents."
    if ranked_evidence:
        answer = llm.generate(question, context_str, conflicts_str)
        
    top_score = ranked_evidence[0].relevance_score if ranked_evidence else 0.0
    
    response = ChatResponse(
        answer=answer,
        sources=ranked_evidence[:3],
        confidence_score=top_score,
        classification=classification,
        conflicts=conflicts,
        session_id=session_id
    )
    
    log = QueryLog(
        question=question,
        answer=answer,
        classification=classification,
        confidence_score=top_score,
        sources_used=",".join([str(e.document_id) for e in ranked_evidence[:3]])
    )
    db_session.add(log)
    db_session.commit()
    
    return response
