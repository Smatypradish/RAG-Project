from typing import List, Dict, Any
from app.models import SourceEvidence, ConflictInfo

def resolve_conflict(chunk_a: SourceEvidence, chunk_b: SourceEvidence) -> Dict[str, Any]:
    if chunk_a.status == 'active' and chunk_b.status != 'active':
        return {"winner": chunk_a, "loser": chunk_b, "reason": "Winner is active, loser is not."}
    if chunk_b.status == 'active' and chunk_a.status != 'active':
        return {"winner": chunk_b, "loser": chunk_a, "reason": "Winner is active, loser is not."}
        
    if chunk_a.effective_date > chunk_b.effective_date:
        return {"winner": chunk_a, "loser": chunk_b, "reason": "Winner is more recent."}
    if chunk_b.effective_date > chunk_a.effective_date:
        return {"winner": chunk_b, "loser": chunk_a, "reason": "Winner is more recent."}
        
    if chunk_a.authority_level > chunk_b.authority_level:
        return {"winner": chunk_a, "loser": chunk_b, "reason": "Winner has higher authority."}
    if chunk_b.authority_level > chunk_a.authority_level:
        return {"winner": chunk_b, "loser": chunk_a, "reason": "Winner has higher authority."}
        
    return {"winner": chunk_a, "loser": chunk_b, "reason": "Tie-break (arbitrary)"}

def detect_conflicts(ranked_chunks: List[SourceEvidence]) -> List[ConflictInfo]:
    conflicts = []
    doc_ids = set()
    active_chunks = [c for c in ranked_chunks if c.status == 'active']
    
    for i, chunk_a in enumerate(active_chunks):
        if chunk_a.document_id in doc_ids:
            continue
        doc_ids.add(chunk_a.document_id)
        
        for chunk_b in active_chunks[i+1:]:
            if chunk_a.document_id != chunk_b.document_id:
                if chunk_a.relevance_score > 0.5 and chunk_b.relevance_score > 0.5:
                    res = resolve_conflict(chunk_a, chunk_b)
                    conflict = ConflictInfo(
                        topic=chunk_a.section,
                        source_a=chunk_a,
                        source_b=chunk_b,
                        resolution=f"Use document {res['winner'].document_name}",
                        explanation=res['reason']
                    )
                    conflicts.append(conflict)
                    break
    return conflicts
