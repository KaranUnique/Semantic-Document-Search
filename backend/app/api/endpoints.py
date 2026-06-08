import os
import json
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

# In-memory document storage (simplified - no database)
uploaded_documents: List[Dict[str, Any]] = []

# ==========================================
# DOCUMENT MANAGEMENT ROUTERS
# ==========================================

@router.post("/documents/upload", status_code=status.HTTP_201_CREATED)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Uploads and processes documents (PDF, DOCX, PPTX, TXT).
    Extracts text, chunks it, and stores embeddings in ChromaDB.
    """
    processed_docs = []
    
    for file in files:
        temp_path = os.path.join(doc_processor.upload_dir, f"temp_{file.filename}")
        try:
            # Write temp file
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
                
            # Rename to final path
            final_path = os.path.join(doc_processor.upload_dir, f"{int(datetime.utcnow().timestamp())}_{file.filename}")
            os.rename(temp_path, final_path)
            
            # Parse and chunk document
            chunks, page_count = doc_processor.process_file(final_path, file.filename)
            
            # Add to ChromaDB vector store
            vector_store.add_documents(chunks)
            
            # Store metadata in memory
            doc_info = {
                "id": len(uploaded_documents) + 1,
                "name": file.filename,
                "file_path": final_path,
                "file_type": os.path.splitext(file.filename)[1].lower(),
                "size_bytes": len(content),
                "page_count": page_count,
                "chunk_count": len(chunks),
                "uploaded_at": datetime.utcnow().isoformat()
            }
            uploaded_documents.append(doc_info)
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
            
        # Remove from in-memory storage
        uploaded_documents.remove(doc)
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
