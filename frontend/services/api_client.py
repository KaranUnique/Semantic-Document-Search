import os
import logging
import requests
from typing import Generator, List, Dict, Any

logger = logging.getLogger("api_client")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

class APIClient:
    @staticmethod
    def _get_headers(multipart: bool = False) -> Dict[str, str]:
        """Returns appropriate headers for requests."""
        headers = {}
        if not multipart:
            headers["Content-Type"] = "application/json"
        return headers

    @staticmethod
    def upload_documents(uploaded_files: list) -> List[Dict[str, Any]]:
        """Uploads multiple files simultaneously in batch."""
        url = f"{BACKEND_URL}/documents/upload"
        files_payload = []
        
        # Structure files for multipart
        for file in uploaded_files:
            files_payload.append(("files", (file.name, file.getvalue(), file.type)))
            
        headers = APIClient._get_headers(multipart=True)
        response = requests.post(url, files=files_payload, headers=headers)
        
        if response.status_code != 201:
            raise Exception(response.json().get("detail", "Batch upload failed."))
        return response.json()

    @staticmethod
    def get_documents() -> List[Dict[str, Any]]:
        """Retrieves document library list."""
        url = f"{BACKEND_URL}/documents"
        headers = APIClient._get_headers()
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(response.json().get("detail", "Failed to retrieve documents."))
        return response.json()

    @staticmethod
    def delete_document(doc_id: int) -> Dict[str, str]:
        """Deletes a document by ID."""
        url = f"{BACKEND_URL}/documents/{doc_id}"
        headers = APIClient._get_headers()
        response = requests.delete(url, headers=headers)
        if response.status_code != 200:
            raise Exception(response.json().get("detail", "Delete document failed."))
        return response.json()

    @staticmethod
    def send_chat_message_stream(query: str) -> Generator[str, None, None]:
        """Sends a chat query and yields generative response tokens."""
        url = f"{BACKEND_URL}/chat"
        headers = APIClient._get_headers(multipart=True)
        data = {"query": query}
        
        response = requests.post(url, data=data, headers=headers, stream=True)
        if response.status_code != 200:
            raise Exception("Failed to send message.")
            
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk

    @staticmethod
    def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Performs semantic search on uploaded documents."""
        url = f"{BACKEND_URL}/rag/semantic-search"
        headers = APIClient._get_headers(multipart=True)
        data = {"query": query, "top_k": top_k}
        response = requests.post(url, data=data, headers=headers)
        if response.status_code != 200:
            raise Exception(response.json().get("detail", "Semantic search query failed."))
        return response.json()

    @staticmethod
    def summarize_document_stream(doc_name: str) -> Generator[str, None, None]:
        """Queries document summarization stream."""
        url = f"{BACKEND_URL}/rag/summarize/{doc_name}"
        headers = APIClient._get_headers()
        response = requests.post(url, headers=headers, stream=True)
        if response.status_code != 200:
            raise Exception("Failed to generate summary.")
            
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk
