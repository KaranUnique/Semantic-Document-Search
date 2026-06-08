import os
import logging
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("vector_store")

class VectorStoreService:
    def __init__(self, db_path: str = "./chroma_db"):
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Initialize collection using Cosine similarity
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize SentenceTransformer embedding model locally
        logger.info("Initializing local SentenceTransformer ('all-MiniLM-L6-v2')...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("SentenceTransformer loaded successfully.")

    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Ingests document chunks into ChromaDB.
        Each chunk is formatted as:
        {
            "text": str,
            "metadata": {
                "source": str,
                "page": int,
                "chunk_index": int,
                "file_type": str
            }
        }
        """
        if not chunks:
            return
            
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for idx, chunk in enumerate(chunks):
            # Create a deterministic and unique chunk ID
            source = chunk["metadata"]["source"]
            chunk_idx = chunk["metadata"]["chunk_index"]
            chunk_id = f"{source}_chunk_{chunk_idx}"
            
            ids.append(chunk_id)
            documents.append(chunk["text"])
            
            # ChromaDB metadatas must be flat dicts with str, int, float, or bool values
            metadatas.append(chunk["metadata"])
            
        # Generate embeddings in batch
        logger.info(f"Generating embeddings for {len(documents)} chunks...")
        embeddings_list = self.model.encode(documents, show_progress_bar=False)
        embeddings = [emb.tolist() for emb in embeddings_list]
        
        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        logger.info("Chunks successfully stored in ChromaDB.")

    def delete_document_chunks(self, filename: str) -> None:
        """Deletes all chunks associated with a specific filename from Chroma."""
        # Find matches based on metadata filter
        results = self.collection.get(
            where={"source": filename}
        )
        if results and results["ids"]:
            self.collection.delete(ids=results["ids"])
            logger.info(f"Deleted {len(results['ids'])} chunks for {filename} from ChromaDB.")

    def get_all_chunks(self) -> Tuple[List[str], List[Dict[str, Any]], List[str]]:
        """Retrieves all documents, metadata, and IDs from ChromaDB."""
        results = self.collection.get()
        return results.get("documents", []), results.get("metadatas", []), results.get("ids", [])

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes simple semantic search using ChromaDB vector embeddings.
        Returns top_k results with metadata and similarity scores.
        """
        # Get all chunks to check if database is empty
        documents, metadatas, ids = self.get_all_chunks()
        if not documents:
            return []
        
        # Vector Search using ChromaDB
        query_embedding = self.model.encode([query])[0].tolist()
        vector_query = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, len(documents)),
            include=["documents", "metadatas", "distances"]
        )
        
        # Map results
        results = []
        if vector_query and vector_query["ids"] and len(vector_query["ids"][0]) > 0:
            for i in range(len(vector_query["ids"][0])):
                doc_id = vector_query["ids"][0][i]
                doc_text = vector_query["documents"][0][i]
                metadata = vector_query["metadatas"][0][i]
                # Cosine distance to similarity (1 - dist)
                dist = vector_query["distances"][0][i]
                similarity = max(0.0, min(1.0, 1.0 - dist))
                # Convert to percentage
                similarity_percent = round(similarity * 100, 1)
                
                results.append({
                    "id": doc_id,
                    "text": doc_text,
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "file_type": metadata["file_type"],
                    "relevance_score": similarity_percent
                })
        
        return results
