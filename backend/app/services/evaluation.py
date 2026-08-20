from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.verification_engine import filter_and_rank, classify_evidence
from app.services.conflict_detector import detect_conflicts
from app.services.llm_service import LLMService

def evaluate_retrieval(expected_doc_ids: List[int], retrieved_chunks: List[Any]) -> Dict[str, float]:
    """Computes Recall@K, Precision@K, and MRR@K."""
    if not retrieved_chunks:
        return {"recall@k": 0.0, "precision@k": 0.0, "mrr": 0.0}
    
    retrieved_doc_ids = [c.document_id for c in retrieved_chunks]
    hits = len(set(expected_doc_ids) & set(retrieved_doc_ids))
    
    recall = hits / len(expected_doc_ids) if expected_doc_ids else 0.0
    precision = hits / len(retrieved_doc_ids) if retrieved_doc_ids else 0.0
    
    # MRR (Mean Reciprocal Rank)
    mrr = 0.0
    for idx, doc_id in enumerate(retrieved_doc_ids):
        if doc_id in expected_doc_ids:
            mrr = 1.0 / (idx + 1)
            break
            
    return {"recall@k": round(recall, 3), "precision@k": round(precision, 3), "mrr": round(mrr, 3)}

def evaluate_faithfulness(answer: str, context: str) -> float:
    """Measures how well the generated answer is grounded in the retrieved context."""
    if "not found in the available documents" in answer.lower():
        return 1.0
        
    answer_words = [w.lower() for w in answer.split() if len(w) > 3]
    context_words = set(context.lower().split())
    
    if not answer_words:
        return 0.0
        
    matches = sum(1 for w in answer_words if w in context_words)
    return round(matches / len(answer_words), 3)

def evaluate_conflict_resolution(conflicts: List[Any], expected_winner_doc_name: str) -> float:
    """Verifies if the rule-based verification engine correctly identified the authoritative winner."""
    if not conflicts:
        return 0.0
    for c in conflicts:
        if expected_winner_doc_name.lower() in c.resolution.lower() or expected_winner_doc_name.lower() in c.source_a.document_name.lower():
            return 1.0
    return 0.0

def run_comprehensive_evaluation(test_suite: List[Dict[str, Any]], db_session: Session) -> Dict[str, Any]:
    """
    Runs an automated benchmark across:
    1. Retrieval metrics (Recall, Precision, MRR)
    2. Generation metrics (Faithfulness)
    3. Innovation metrics (Conflict Resolution, Outdated Rejection, Authority Selection)
    """
    emb_service = EmbeddingService()
    vec_store = VectorStoreService()
    llm = LLMService()
    
    detailed_results = []
    total_recall = 0.0
    total_precision = 0.0
    total_mrr = 0.0
    total_faithfulness = 0.0
    total_conflict_acc = 0.0
    conflict_tests_count = 0
    outdated_rejection_count = 0
    total_outdated_tests = 0
    
    for test in test_suite:
        query = test["question"]
        expected_docs = test.get("expected_doc_ids", [])
        expected_winner = test.get("expected_winner_doc_name", "")
        test_type = test.get("type", "general")
        
        # 1. Retrieve
        query_emb = emb_service.embed_query(query)
        raw_chunks = vec_store.search(query_emb, top_k=5)
        ranked = filter_and_rank(raw_chunks, db_session)
        conflicts = detect_conflicts(ranked)
        classification = classify_evidence(ranked, conflicts)
        
        # 2. Context & LLM
        context_str = "\n\n".join([f"[{e.document_name}]\n{e.chunk_text}" for e in ranked[:3]])
        conflicts_str = "\n".join([f"Conflict in {c.topic}: {c.resolution}" for c in conflicts])
        answer = llm.generate(query, context_str, conflicts_str)
        
        # Metrics
        ret_metrics = evaluate_retrieval(expected_docs, ranked[:3])
        faith = evaluate_faithfulness(answer, context_str)
        
        total_recall += ret_metrics["recall@k"]
        total_precision += ret_metrics["precision@k"]
        total_mrr += ret_metrics["mrr"]
        total_faithfulness += faith
        
        conflict_score = None
        if test_type == "conflict":
            conflict_tests_count += 1
            conflict_score = evaluate_conflict_resolution(conflicts, expected_winner)
            total_conflict_acc += conflict_score
            
        outdated_rejected = None
        if test_type == "outdated_query":
            total_outdated_tests += 1
            # Verify system indicates outdated status or picks active revised version
            if classification in ["outdated", "verified"]:
                outdated_rejected = 1.0
                outdated_rejection_count += 1
            else:
                outdated_rejected = 0.0
                
        detailed_results.append({
            "question": query,
            "classification": classification,
            "retrieval": ret_metrics,
            "faithfulness": faith,
            "conflict_resolution_score": conflict_score,
            "outdated_handled": outdated_rejected,
            "answer_preview": answer[:120] + "..."
        })
        
    num_tests = len(test_suite) or 1
    avg_recall = round(total_recall / num_tests, 3)
    avg_precision = round(total_precision / num_tests, 3)
    avg_mrr = round(total_mrr / num_tests, 3)
    avg_faithfulness = round(total_faithfulness / num_tests, 3)
    avg_conflict_acc = round(total_conflict_acc / (conflict_tests_count or 1), 3) if conflict_tests_count > 0 else 1.0
    outdated_accuracy = round(outdated_rejection_count / (total_outdated_tests or 1), 3) if total_outdated_tests > 0 else 1.0
    
    return {
        "summary": {
            "total_test_cases": num_tests,
            "retrieval_recall@3": avg_recall,
            "retrieval_precision@3": avg_precision,
            "mean_reciprocal_rank": avg_mrr,
            "answer_faithfulness": avg_faithfulness,
            "conflict_resolution_accuracy": avg_conflict_acc,
            "outdated_rejection_accuracy": outdated_accuracy,
            "overall_reliability_score": round((avg_recall + avg_faithfulness + avg_conflict_acc + outdated_accuracy) / 4.0, 3)
        },
        "detailed_runs": detailed_results
    }
