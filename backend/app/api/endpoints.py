import os
import json
import hashlib
import logging
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from backend.app.services.doc_processor import DocProcessor
from backend.app.services.vector_store import VectorStoreService
from backend.app.services.rag_service import RAGService

logger = logging.getLogger("endpoints")
router = APIRouter()

# Initialize core services
doc_processor = DocProcessor()
vector_store = VectorStoreService()
rag_service = RAGService(vector_store)

# ── Registry persistence ──────────────────────────────────────────────────────
REGISTRY_PATH = os.path.join(doc_processor.upload_dir, "_registry.json")

def _load_registry() -> List[Dict[str, Any]]:
    """Load document registry from disk, rebuilding from ChromaDB if missing."""
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Registry file unreadable, rebuilding: {e}")

    # Rebuild from ChromaDB metadata
    logger.info("Rebuilding document registry from ChromaDB...")
    _, metadatas, _ = vector_store.get_all_chunks()
    seen = {}
    for meta in metadatas:
        src = meta.get("source")
        if src and src not in seen:
            seen[src] = {
                "id": len(seen) + 1,
                "name": src,
                "file_path": "",
                "file_type": meta.get("file_type", ""),
                "size_bytes": 0,
                "page_count": meta.get("page", 1),
                "chunk_count": 0,
                "uploaded_at": datetime.utcnow().isoformat()
            }
    docs = list(seen.values())
    _save_registry(docs)
    return docs

def _save_registry(docs: List[Dict[str, Any]]) -> None:
    """Persist the document registry to disk."""
    try:
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save registry: {e}")

# In-memory document storage — loaded from disk on startup
uploaded_documents: List[Dict[str, Any]] = _load_registry()

# ==========================================
# DOCUMENT MANAGEMENT ROUTERS
# ==========================================

@router.post("/documents/upload", status_code=status.HTTP_201_CREATED)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Uploads and processes documents (PDF, DOCX, PPTX, TXT, MD).
    Skips duplicates via MD5 hash check, chunks text, and stores embeddings in ChromaDB.
    """
    processed_docs = []
    
    for file in files:
        temp_path = os.path.join(doc_processor.upload_dir, f"temp_{file.filename}")
        try:
            content = await file.read()

            # Write temp file to compute MD5
            with open(temp_path, "wb") as f:
                f.write(content)

            file_md5 = DocProcessor.calculate_md5(temp_path)

            # Duplicate check — skip if same file already uploaded
            existing = next((d for d in uploaded_documents if d.get("md5") == file_md5), None)
            if existing:
                logger.info(f"Skipping duplicate file '{file.filename}' (md5 matches '{existing['name']}')")
                os.remove(temp_path)
                processed_docs.append(existing)
                continue

            # Rename to final path
            final_path = os.path.join(doc_processor.upload_dir, f"{int(datetime.utcnow().timestamp())}_{file.filename}")
            os.rename(temp_path, final_path)
            
            # Parse and chunk document
            chunks, page_count = doc_processor.process_file(final_path, file.filename)
            
            # Add to ChromaDB vector store
            vector_store.add_documents(chunks)
            
            # Store metadata in memory and persist
            doc_info = {
                "id": len(uploaded_documents) + 1,
                "name": file.filename,
                "file_path": final_path,
                "file_type": os.path.splitext(file.filename)[1].lower(),
                "size_bytes": len(content),
                "page_count": page_count,
                "chunk_count": len(chunks),
                "md5": file_md5,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            uploaded_documents.append(doc_info)
            _save_registry(uploaded_documents)
            processed_docs.append(doc_info)
            
        except Exception as e:
            logger.error(f"Failed to ingest file {file.filename}: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error ingesting document '{file.filename}': {str(e)}"
            )
            
    return processed_docs

@router.get("/documents")
def get_documents():
    """Lists all uploaded documents."""
    return uploaded_documents

@router.delete("/documents/{doc_id}", status_code=status.HTTP_200_OK)
def delete_document(doc_id: int):
    """Deletes a document from the system (ChromaDB and local disk)."""
    doc = next((d for d in uploaded_documents if d["id"] == doc_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    try:
        # Delete from ChromaDB vector store
        vector_store.delete_document_chunks(doc["name"])
        
        # Delete from local disk storage
        if os.path.exists(doc["file_path"]):
            os.remove(doc["file_path"])
            
        # Remove from in-memory storage and persist
        uploaded_documents.remove(doc)
        _save_registry(uploaded_documents)
        return {"detail": f"Document '{doc['name']}' deleted successfully."}
    except Exception as e:
        logger.error(f"Error deleting document {doc['name']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

# ==========================================
# CHAT ROUTER
# ==========================================

@router.post("/chat")
def chat(query: str = Form(...)):
    """
    Processes a user query, retrieves relevant document chunks,
    and streams the AI response with citations.
    """
    # Fetch stream and citations
    stream_gen, retrieved_chunks = rag_service.answer_query_stream(query)
    
    # Prepare citation references
    citations = []
    for idx, c in enumerate(retrieved_chunks):
        citations.append({
            "index": idx + 1,
            "source": c["source"],
            "page": c["page"],
            "relevance_score": c["relevance_score"]
        })
    citations_json = json.dumps(citations)
    
    # Stream response generator
    def stream_wrapper():
        # First line contains citation metadata
        yield f"[SOURCES_METADATA]: {citations_json}\n"
        
        for token in stream_gen:
            yield token
            
    return StreamingResponse(stream_wrapper(), media_type="text/event-stream")

# ==========================================
# RAG PIPELINE ENDPOINTS
# ==========================================

@router.post("/rag/semantic-search")
def semantic_search_endpoint(query: str = Form(...), top_k: int = Form(5)):
    """
    Performs semantic search on uploaded documents.
    Returns matching chunks with page locations and similarity scores.
    """
    return vector_store.semantic_search(query, top_k=top_k)

@router.post("/rag/summarize/{doc_name}")
def summarize_document_endpoint(doc_name: str):
    """Streams a comprehensive summary of the specified document."""
    stream_gen = rag_service.summarize_document(doc_name)
    return StreamingResponse(stream_gen, media_type="text/event-stream")
