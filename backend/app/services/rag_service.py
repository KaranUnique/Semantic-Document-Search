import os
import logging
from typing import Generator, List, Dict, Any, Tuple
import google.generativeai as genai
from backend.app.services.vector_store import VectorStoreService

logger = logging.getLogger("rag_service")

class RAGService:
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        
        # Setup Gemini API
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.api_configured = False
        
        if self.api_key and self.api_key != "YOUR_GEMINI_API_KEY_HERE":
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.api_configured = True
                logger.info("Gemini API configured successfully.")
            except Exception as e:
                logger.error(f"Failed to configure Gemini API: {str(e)}")
        else:
            logger.warning("Gemini API key is not set.")

    def _get_no_llm_error_stream(self) -> Generator[str, None, None]:
        """Provides an informative streaming message when no LLM is available."""
        yield "⚠️ **No LLM Available.**\n\n"
        yield "Please configure Gemini API:\n"
        yield "1. Get an API key from https://makersuite.google.com/app/apikey\n"
        yield "2. Set `GEMINI_API_KEY` in `backend/.env`\n"
        yield "Then restart the application."
    
    def _gemini_stream(self, prompt: str) -> Generator[str, None, None]:
        """Streams generation from Gemini API."""
        if not self.api_configured:
            return
        
        try:
            logger.info("Generating response using Gemini 1.5 Flash API")
            response = self.model.generate_content(prompt, stream=True)
            
            for token in response:
                if token.text:
                    yield token.text
                    
        except Exception as e:
            logger.error(f"Error during Gemini generation: {str(e)}")
            raise

    def answer_query_stream(self, query: str) -> Tuple[Generator[str, None, None], List[Dict[str, Any]]]:
        """
        Retrieves top context chunks using semantic search, constructs a prompt,
        and yields generative tokens from Gemini 1.5 Flash.
        Returns the generator and the raw retrieved chunks for UI citation tracking.
        """
        # 1. Retrieve chunks using semantic search
        chunks = self.vector_store.semantic_search(query, top_k=5)
        
        if not chunks:
            # Fallback if no documents exist in store
            def empty_corpus_generator():
                yield "No documents have been uploaded to the database yet. Please go to the **Upload Documents** page and ingest files before starting chat assistant."
            return empty_corpus_generator(), []
        
        # Check if LLM is available
        if not self.api_configured:
            return self._get_no_llm_error_stream(), chunks
            
        # 2. Build context block with page citations
        context_blocks = []
        for idx, chunk in enumerate(chunks):
            ref_id = idx + 1
            context_blocks.append(
                f"[{ref_id}] File: {chunk['source']} (Page: {chunk['page']})\n"
                f"Content: {chunk['text']}"
            )
        context_str = "\n\n".join(context_blocks)
        
        # 3. Design precise system context prompt
        prompt = f"""You are a helpful and precise Knowledge Assistant.
Use the provided context to answer the user query as concisely and factually as possible.

INSTRUCTIONS:
1. Base your answer strictly on the provided Context.
2. If the answer cannot be found in the Context, clearly state that: "The requested information could not be found in the uploaded documents." Do NOT attempt to make up or hallucinate answers.
3. Keep the response natural, professional, and structured.
4. When referencing information from a specific chunk, append the reference number, e.g., [1] or [2], matching the Context bracket indices.

Context:
{context_str}

User Query:
{query}

Answer:"""

        # 4. Stream generative responses using Gemini
        def stream_generator():
            try:
                yield from self._gemini_stream(prompt)
            except Exception as e:
                logger.error(f"Error during generation: {str(e)}")
                yield f"Generation error: {str(e)}"
        
        return stream_generator(), chunks

    def summarize_document(self, filename: str) -> Generator[str, None, None]:
        """Loads all chunks for a document and streams a comprehensive summary."""
        if not self.api_configured:
            return self._get_no_llm_error_stream()
            
        # Retrieve all chunks
        results = self.vector_store.collection.get(where={"source": filename})
        if not results or not results["documents"]:
            def no_doc_generator():
                yield "Selected document text could not be retrieved from database."
            return no_doc_generator()
            
        # Concatenate in index order
        paired = []
        for text, meta in zip(results["documents"], results["metadatas"]):
            paired.append((meta.get("chunk_index", 0), text))
        paired.sort()
        full_text = "\n".join([item[1] for item in paired])
        
        prompt = f"""You are an expert analyst. Provide a comprehensive summary of the document: '{filename}'.
Organize your output into three Markdown sections:

# Document Summary
[Provide a high-level overview of the core subject matter]

# Executive Summary
[Write a professional overview outlining the context, objectives, and key findings]

# Key Insights & Takeaways
[Present a bulleted list of the most critical facts, numbers, dates, or decisions]

Document Content:
{full_text}
"""
        
        def summary_generator():
            try:
                yield from self._gemini_stream(prompt)
            except Exception as e:
                logger.error(f"Summary generation error: {str(e)}")
                yield f"Summary generation failed: {str(e)}"
        
        return summary_generator()

