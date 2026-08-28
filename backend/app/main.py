from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import chat, documents, admin
import os

app = FastAPI(title="RAG College Helpdesk", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.on_event("startup")
def on_startup():
    init_db()
    os.makedirs("./uploads", exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "running", "version": "1.0.0"}
