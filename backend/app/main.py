import logging
from dotenv import load_dotenv
load_dotenv()  # Load backend/.env before any service initializes

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.endpoints import router as api_router

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

# Create FastAPI app
app = FastAPI(
    title="Simple RAG Assistant API",
    description="Beginner-friendly RAG application backend with semantic search and document processing.",
    version="1.0.0"
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler for generic server issues
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

# Include central endpoints router
app.include_router(api_router)

@app.get("/")
def health_check():
    """Simple API health check."""
    return {
        "status": "healthy",
        "service": "Simple RAG Assistant Backend",
        "engine": "FastAPI, ChromaDB, Ollama (local LLM)"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting local development server via uvicorn...")
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
