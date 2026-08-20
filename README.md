# A Verified and Version-Aware RAG System for College Information

An institutional Retrieval-Augmented Generation (RAG) platform with a **Verified Policy Resolution Engine**, designed to provide grounded, authoritative answers to student inquiries from official college documents.

---

## 🌟 Key Innovations (Patent-Worthy Features)

Traditional RAG systems treat all documents equally and suffer from hallucinations when policies conflict or when documents are outdated. This system introduces:

1. **Verified Policy Resolution Engine**:
   - Calculates a multi-factor **Reliability Score**:
     $$\text{Reliability Score} = 0.4 \cdot S_{\text{semantic}} + 0.2 \cdot S_{\text{authority}} + 0.2 \cdot S_{\text{validity}} + 0.1 \cdot S_{\text{recency}} + 0.1 \cdot S_{\text{consistency}}$$
   - Classifies query evidence into 5 distinct states:
     - `Verified`: Single authoritative, active document.
     - `Conflicting`: Multiple active documents provide contradictory rules.
     - `Outdated`: Only superseded or historical documents exist.
     - `Insufficient`: Information is too weak to provide a confident answer.
     - `Not Available`: No supporting evidence in institutional records.

2. **Document Lineage & Version Tracking**:
   - Explicit lineage mapping: `parent_document_id`, `supersedes_document_id`, `revision_reason`.
   - Hierarchical authority levels (1 = Committee, 2 = Department, 3 = Dean, 4 = Registrar / CoE, 5 = University / VC).

3. **Deterministic Rule-Based Conflict Resolution**:
   - Rules applied *before* LLM generation:
     $$\text{Status Check} \rightarrow \text{Lineage Precedence} \rightarrow \text{Effective Date} \rightarrow \text{Authority Level}$$
   - The LLM acts as an explanatory agent rather than an unconstrained arbitrator.

4. **Citation-Level Evidence Attribution**:
   - Answers are paired with exact evidence cards displaying Document Name, Page, Section, Issuing Authority, Effective Date, and Active Status.

---

## 🏗️ System Architecture

```
                  OFFICIAL COLLEGE DOCUMENTS
                    (PDF, DOCX, TXT, MD)
                              │
                              ▼
                     Document Processing
                  (Text Extraction & Chunking)
                              │
                              ▼
                     Embedding Generation
                  (Sentence-Transformers: all-MiniLM-L6-v2)
                              │
                              ▼
                      Vector Database
                         (ChromaDB)
                              │
      STUDENT QUERY           ▼
    ─────────────────► Semantic Retrieval (Top-K)
                              │
                              ▼
             ┌───────────────────────────────────┐
             │  VERIFIED POLICY RESOLUTION ENGINE │
             │  • Document Lineage Validation    │
             │  • Hierarchical Authority Ranking │
             │  • Temporal Recency & Validity    │
             │  • Rule-Based Conflict Detection  │
             │  • Multi-Factor Reliability Score │
             └────────────────┬──────────────────┘
                              │
                              ▼
                     Evidence Selection
                              │
                              ▼
                    LLM Generation Layer
                 (Gemini / OpenAI / Ollama)
                              │
                              ▼
             ┌───────────────────────────────────┐
             │ • Grounded Student Answer         │
             │ • Citation Cards & Authority Level│
             │ • Policy Conflict Resolution Note │
             │ • Confidence / Reliability Badge  │
             └───────────────────────────────────┘
```

---

## 📁 Repository Structure

```
rag-college-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI server entry point & CORS
│   │   ├── config.py                   # Pydantic v2 settings (.env loader)
│   │   ├── database.py                 # SQLite metadata DB & models
│   │   ├── models.py                   # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── chat.py                 # POST /api/chat endpoint
│   │   │   ├── documents.py            # POST/GET/PUT/DELETE /api/documents
│   │   │   └── admin.py                # Admin authentication & system stats
│   │   └── services/
│   │       ├── document_processor.py   # PDF, DOCX, TXT parsers & chunker
│   │       ├── embedding_service.py    # Sentence-Transformers singleton
│   │       ├── vector_store.py         # ChromaDB persistence & search
│   │       ├── verification_engine.py  # Reliability score & evidence ranking
│   │       ├── conflict_detector.py    # Rule-based policy conflict resolution
│   │       ├── llm_service.py          # Gemini/OpenAI/Ollama + fallback
│   │       ├── rag_pipeline.py         # End-to-end RAG orchestrator
│   │       └── evaluation.py           # Automated evaluation metrics suite
│   ├── seed_demo_data.py               # Auto-ingestion script for demo docs
│   ├── run_demo_and_evaluation.py      # Benchmark runner & killer demo tester
│   ├── requirements.txt                # Python backend dependencies
│   └── .env.example                    # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx              # Header navigation
│   │   │   ├── ChatInterface.jsx       # Real-time chat UI with auto-scroll
│   │   │   ├── MessageBubble.jsx       # Student message & Bot evidence bubble
│   │   │   ├── SourceCard.jsx          # Citation card with authority badge
│   │   │   ├── DocumentUpload.jsx      # Admin upload form with metadata fields
│   │   │   └── DocumentList.jsx        # Document table with status management
│   │   ├── pages/
│   │   │   ├── ChatPage.jsx            # Student chat screen
│   │   │   ├── AdminPage.jsx           # Knowledge base admin dashboard
│   │   │   └── LoginPage.jsx           # Administrator login screen
│   │   ├── services/
│   │   │   └── api.js                  # Axios client for backend API
│   │   ├── App.jsx                     # Routing setup
│   │   ├── main.jsx                    # React entrypoint
│   │   └── index.css                   # Tailwind directives & styles
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
└── sample_documents/
    ├── academic_regulations_2024.txt   # Old document (v1.0, deadline Sept 10)
    ├── academic_regulations_2026.txt   # Revised document (v2.0, deadline Sept 15)
    └── exam_circular_fall_2026.txt     # CoE circular (Level 4, deadline Sept 15)
```

---

## 🚀 Quickstart Guide

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# (Optional: Edit .env to add your GEMINI_API_KEY or OPENAI_API_KEY)

# Seed demo documents (indexes the 3 demo documents into SQLite & ChromaDB)
python seed_demo_data.py

# Start FastAPI server (runs at http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```

API documentation will be accessible at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server (runs at http://localhost:5173)
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🎯 Killer Demo Scenario (Viva Demonstration)

To demonstrate the system's superiority over standard RAG chatbots:

### Question 1: "What is the final exam registration deadline for Fall 2026?"
- **Standard RAG failure**: Might randomly pick September 10 (from the 2024 doc) or September 15 (from the 2026 doc).
- **Our System**:
  - Detects that **Academic Regulations 2026 (v2.0)** supersedes **Academic Regulations 2024 (v1.0)**.
  - Correctly answers **September 15, 2026**.
  - Highlights that the 2024 regulation is superseded.
  - Shows verified evidence from both the Revised Regulations (Level 5) and the Controller of Examinations Circular (Level 4).

### Question 2: "What was the registration deadline in the older 2024 regulations?"
- **Our System**:
  - Identifies that the query requests historical data.
  - Retrieves the **September 10** date from the 2024 regulations.
  - Labels the source with an `Outdated / Superseded` badge so students are not misled.

### Question 3: "How do I book the college swimming pool slots?"
- **Our System**:
  - Recognizes that no uploaded institutional documents cover this topic.
  - Returns classification: `NOT_AVAILABLE`.
  - Rejects the query instead of hallucinating instructions.

---

## 📊 Evaluation & Benchmarking

Run the automated test and evaluation suite:

```bash
cd backend
python run_demo_and_evaluation.py
```

### Metrics Covered:
1. **Retrieval**:
   - `Recall@3`
   - `Precision@3`
   - `Mean Reciprocal Rank (MRR)`
2. **Answer Quality**:
   - `Faithfulness` (Groundedness in context)
3. **Verification Engine Innovations**:
   - `Conflict Resolution Accuracy` (Accuracy in picking the authoritative active policy)
   - `Outdated Document Rejection Accuracy`
   - `Overall Reliability Score`
