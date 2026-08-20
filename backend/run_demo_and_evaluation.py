import os
import sys
import json

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db
from app.services.rag_pipeline import process_query
from app.services.evaluation import run_comprehensive_evaluation

def run_tests():
    init_db()
    db = SessionLocal()
    
    print("=" * 80)
    print("DEMO 1: VERIFIED POLICY RESOLUTION & CONFLICT HANDLING")
    print("=" * 80)
    
    q1 = "What is the final exam registration deadline?"
    print(f"\n[Student Query]: {q1}")
    res1 = process_query(q1, db)
    print(f"\n[Chatbot Classification]: {res1.classification.upper()}")
    print(f"[Reliability Confidence Score]: {res1.confidence_score:.3f}")
    print(f"[Answer]:\n{res1.answer}\n")
    print("[Evidence & Citations]:")
    for s in res1.sources:
        print(f" - Document: {s.document_name} | Authority: {s.authority_label} (Level {s.authority_level}) | Status: {s.status} | Date: {s.effective_date}")
    
    if res1.conflicts:
        print("\n[Detected Policy Conflicts Resolved]:")
        for c in res1.conflicts:
            print(f" * Topic: {c.topic}")
            print(f"   Source A: {c.source_a.document_name} (Status: {c.source_a.status})")
            print(f"   Source B: {c.source_b.document_name} (Status: {c.source_b.status})")
            print(f"   Resolution: {c.resolution} -> {c.explanation}")
            
    print("\n" + "=" * 80)
    print("DEMO 2: UNAVAILABLE / LOW COVERAGE REJECTION")
    print("=" * 80)
    
    q2 = "What are the rules and timings for booking the college swimming pool?"
    print(f"\n[Student Query]: {q2}")
    res2 = process_query(q2, db)
    print(f"\n[Chatbot Classification]: {res2.classification.upper()}")
    print(f"[Reliability Confidence Score]: {res2.confidence_score:.3f}")
    print(f"[Answer]:\n{res2.answer}")
    
    print("\n" + "=" * 80)
    print("RUNNING AUTOMATED RAG EVALUATION BENCHMARK SUITE")
    print("=" * 80)
    
    benchmark_suite = [
        {
            "question": "What is the exam registration deadline?",
            "expected_doc_ids": [2, 3],
            "expected_winner_doc_name": "Revised Academic Regulations 2026",
            "type": "conflict"
        },
        {
            "question": "What are the continuous assessment components CAT-1 and CAT-2 weightage?",
            "expected_doc_ids": [2, 3],
            "type": "general"
        },
        {
            "question": "What is the minimum CGPA required to avoid academic probation in 2026?",
            "expected_doc_ids": [2],
            "type": "general"
        },
        {
            "question": "What was the previous exam deadline in the old 2024 regulations?",
            "expected_doc_ids": [1],
            "type": "outdated_query"
        },
        {
            "question": "How many credits can an undergraduate student register for per semester?",
            "expected_doc_ids": [2],
            "type": "general"
        },
        {
            "question": "What are the flight training simulator guidelines?",
            "expected_doc_ids": [],
            "type": "unsupported"
        }
    ]
    
    report = run_comprehensive_evaluation(benchmark_suite, db)
    print("\nBENCHMARK RESULTS SUMMARY:")
    print(json.dumps(report["summary"], indent=4))
    
    db.close()

if __name__ == "__main__":
    run_tests()
