import re
from PyPDF2 import PdfReader
from docx import Document
from typing import List, Dict, Any

def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    pages_text = []
    try:
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages_text.append({"page": i + 1, "text": text})
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return pages_text

def extract_text_from_docx(file_path: str) -> List[Dict[str, Any]]:
    pages_text = []
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        pages_text.append({"page": 1, "text": "\n".join(full_text)})
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return pages_text

def extract_text_from_txt(file_path: str) -> List[Dict[str, Any]]:
    pages_text = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        pages_text.append({"page": 1, "text": content})
    except Exception as e:
        print(f"Error reading TXT/MD {file_path}: {e}")
    return pages_text

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(pages_text: List[Dict[str, Any]], chunk_size: int = 800, overlap: int = 200, doc_id: int = None, doc_name: str = None) -> List[Dict[str, Any]]:
    chunks = []
    chunk_index = 0
    for page in pages_text:
        text = clean_text(page["text"])
        
        lines = text.split('.')
        current_section = "General"
        for line in lines:
            clean_line = line.strip()
            if clean_line.isupper() or clean_line.endswith(':'):
                current_section = clean_line[:50]
        
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_str = text[start:end]
            chunks.append({
                "chunk_text": chunk_str,
                "metadata": {
                    "doc_id": doc_id or 0,
                    "doc_name": doc_name or "Unknown",
                    "page_number": page["page"],
                    "chunk_index": chunk_index,
                    "section_hint": current_section
                }
            })
            chunk_index += 1
            start += (chunk_size - overlap)
    return chunks
