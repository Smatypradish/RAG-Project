# Verified & Version-Aware RAG — College Helpdesk

An institutional Retrieval-Augmented Generation (RAG) system that answers student
questions from official college documents, with explicit handling for **outdated,
superseded, and conflicting policies** — the situations where standard RAG chatbots
hallucinate most.

## What makes it different

Standard RAG treats every retrieved chunk as equally trustworthy. This system adds a
**Verified Policy Resolution Engine** between retrieval and generation:

1. **Reliability scoring** — every retrieved chunk is scored from semantic relevance,
   issuing authority level, document validity window (effective/expiry dates),
   recency, and active status.
2. **Evidence classification** — each answer is labeled one of:
   `verified` · `conflicting` · `outdated` · `insufficient` · `not_available`
3. **Rule-based conflict resolution** — when two active documents disagree,
   precedence is decided deterministically (status → lineage → effective date →
   authority level). The LLM only *explains* the resolved answer; it never picks
   the winner itself.
4. **Citation cards** — every answer shows the exact source: document name, page,
   section, authority level, effective date, and active/superseded status.

> These are engineering heuristics, not guarantees. The "relevance %" shown in the UI
> is a heuristic reliability score, not a probability of correctness.

## Architecture

```
Official documents (PDF / DOCX / TXT / MD)
        │
        ▼
Text extraction & chunking ──► Embeddings (all-MiniLM-L6-v2) ──► ChromaDB
                                                                    │
Student query ──► Semantic retrieval (top-k) ◄──────────────────────┘
                        ▼
        ┌────────────────────────────────────────────┐
        │  VERIFIED POLICY RESOLUTION ENGINE          │
        │  • lineage / authority / validity / recency │
        │  • deterministic conflict resolution        │
        └──────────────────────┬─────────────────────┘
                               ▼
              LLM answer (Gemini / OpenAI / Ollama)
              with evidence cards + classification
```

- **Backend:** FastAPI, SQLAlchemy (SQLite), ChromaDB, sentence-transformers
- **Frontend:** React + Vite + Tailwind CSS
- **LLM:** pluggable — Gemini, OpenAI, or local Ollama. With no key configured, the
  system falls back to a deterministic extractive summary from verified context.

## Project layout

```
backend/
  app/
    auth.py          # HMAC-signed, expiring session tokens
    config.py        # Settings loaded from .env (fails closed if ADMIN_PASSWORD unset)
    main.py          # FastAPI app, CORS, lifespan
    models.py        # Pydantic schemas
    routers/         # chat (public), documents & admin (token-protected)
    services/        # retrieval, verification, conflict detection, LLM
  seed_demo_data.py  # Index the 3 sample documents
  run_demo_and_evaluation.py
  tests/             # Deterministic unit tests (no model downloads)
frontend/src/        # React UI: chat page, admin dashboard, evidence cards
sample_documents/    # Demo corpus: 2024 (superseded) vs 2026 (active) regulations + CoE circular
```

## Quickstart

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # then edit .env:
                            #   - set ADMIN_PASSWORD (required for admin login)
                            #   - optionally add GEMINI_API_KEY or OPENAI_API_KEY
python seed_demo_data.py
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173.

### 3. Tests

```bash
cd backend
python -m unittest discover -s tests -v
```

## Demo scenario

| Question | Behavior |
|---|---|
| "What is the exam registration deadline for Fall 2026?" | Detects 2026 regulations supersede 2024; answers **Sept 15, 2026** and flags the old doc as superseded |
| "What was the deadline in the older 2024 regulations?" | Answers Sept 10 from the 2024 doc, labeled **outdated/superseded** |
| "How do I book swimming pool slots?" | No coverage in the corpus → classification `not_available`, refuses to invent an answer |

## Evaluation

```bash
cd backend
python run_demo_and_evaluation.py
```

Reports retrieval Recall@3 / Precision@3 / MRR, answer faithfulness (lexical overlap
heuristic), conflict-resolution accuracy, and outdated-document rejection on the
bundled demo corpus. These are demo-corpus benchmarks, not general claims.

## Security notes

- Admin login is disabled until `ADMIN_PASSWORD` is set (fail-closed).
- Session tokens are HMAC-signed and expire (`SESSION_TTL_MINUTES`).
- Document upload/list/update/delete and admin stats require a valid token.
- Uploads are limited by type (`pdf/docx/txt/md`), size (`MAX_UPLOAD_SIZE_MB`), and
  stored under generated names; failed ingestion is rolled back.
- CORS is restricted to `CORS_ORIGINS`.

## Known limitations

- Password is stored as plaintext config, not hashed (single-admin demo scope).
- Faithfulness and reliability scores are heuristics, not calibrated probabilities.
- Retrieval is semantic-only (no hybrid/BM25 re-ranking).
- SQLite + local ChromaDB are suitable for a single-machine deployment.
