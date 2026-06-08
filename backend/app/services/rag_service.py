import os
import json
import logging
import requests
from typing import Generator, List, Dict, Any, Tuple
from backend.app.services.vector_store import VectorStoreService

logger = logging.getLogger("rag_service")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "mistral")


class RAGService:
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        self.ollama_available = self._check_ollama()

    def _check_ollama(self) -> bool:
        """Ping Ollama and verify the configured model is pulled."""
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
            if r.status_code != 200:
                logger.warning("Ollama is running but returned non-200 on /api/tags")
                return False
            models = [m["name"].split(":")[0] for m in r.json().get("models", [])]
            if OLLAMA_MODEL not in models:
                logger.warning(
                    f"Model '{OLLAMA_MODEL}' not found in Ollama. "
                    f"Run: ollama pull {OLLAMA_MODEL}"
                )
                return False
            logger.info(f"Ollama ready — using model '{OLLAMA_MODEL}'")
            return True
        except Exception as e:
            logger.warning(f"Ollama not reachable at {OLLAMA_BASE_URL}: {e}")
            return False

    def _ollama_stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream tokens from Ollama /api/generate."""
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": True,
        }
        with requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue

    def _no_llm_stream(self) -> Generator[str, None, None]:
        yield (
            f"⚠️ **Ollama not available.**\n\n"
            f"Please make sure Ollama is running and the model is pulled:\n\n"
            f"1. Install Ollama: https://ollama.ai\n"
            f"2. Pull the model:\n"
            f"   ```\n   ollama pull {OLLAMA_MODEL}\n   ```\n"
            f"3. Restart the backend.\n\n"
            f"Current config: `OLLAMA_MODEL={OLLAMA_MODEL}`, "
            f"`OLLAMA_BASE_URL={OLLAMA_BASE_URL}`"
        )

    def answer_query_stream(
        self, query: str
    ) -> Tuple[Generator[str, None, None], List[Dict[str, Any]]]:
        """Retrieve context chunks and stream an answer from the local LLM."""
        chunks = self.vector_store.semantic_search(query, top_k=5)

        if not chunks:
            def _no_docs():
                yield "No documents have been uploaded yet. Please upload files on the Home page first."
            return _no_docs(), []

        # Re-check Ollama liveness on each request (model may have been loaded after startup)
        if not self.ollama_available:
            self.ollama_available = self._check_ollama()

        if not self.ollama_available:
            return self._no_llm_stream(), chunks

        context_blocks = []
        for idx, chunk in enumerate(chunks):
            context_blocks.append(
                f"[{idx+1}] File: {chunk['source']} (Page: {chunk['page']})\n"
                f"Content: {chunk['text']}"
            )
        context_str = "\n\n".join(context_blocks)

        prompt = f"""You are a helpful Knowledge Assistant. Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say: "The requested information could not be found in the uploaded documents."
Cite sources using bracket numbers like [1], [2] where relevant.

Context:
{context_str}

Question: {query}

Answer:"""

        def _stream():
            try:
                yield from self._ollama_stream(prompt)
            except Exception as e:
                logger.error(f"Ollama generation error: {e}")
                yield f"Generation error: {str(e)}"

        return _stream(), chunks

    def summarize_document(self, filename: str) -> Generator[str, None, None]:
        """Stream a structured summary of a document."""
        if not self.ollama_available:
            self.ollama_available = self._check_ollama()
        if not self.ollama_available:
            return self._no_llm_stream()

        results = self.vector_store.collection.get(where={"source": filename})
        if not results or not results["documents"]:
            def _no_doc():
                yield "Document text could not be retrieved from the database."
            return _no_doc()

        paired = sorted(
            zip(results["metadatas"], results["documents"]),
            key=lambda x: x[0].get("chunk_index", 0),
        )
        full_text = "\n".join(doc for _, doc in paired)

        prompt = f"""You are an expert analyst. Summarise the document '{filename}' using the content below.
Structure your response in these three Markdown sections:

# Document Summary
A high-level overview of the subject matter.

# Executive Summary
A professional overview of context, objectives, and key findings.

# Key Insights & Takeaways
A bullet list of the most critical facts, numbers, dates, or decisions.

Document Content:
{full_text}
"""

        def _stream():
            try:
                yield from self._ollama_stream(prompt)
            except Exception as e:
                logger.error(f"Summary generation error: {e}")
                yield f"Summary generation failed: {str(e)}"

        return _stream()
