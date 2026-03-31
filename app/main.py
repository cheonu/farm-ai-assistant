from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import logging
from pathlib import Path
from threading import Lock
from dotenv import load_dotenv

from .services.llm_service import FarmLLMService
from .services.rag_service import RagService
from .services.embedding_service import EmbeddingService
from .services.vector_store import VectorStore
from .services.retrieval_engine import RetrievalEngine
from .services.context_augmenter import ContextAugmenter
from .services.whatsapp_parser import WhatsAppParser
from .services.document_chunker import DocumentChunker
from .utils.data_processor import FarmDataProcessor

# Load environment variables
load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Farm AI Assistant"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="AI-powered farm management assistant"
)

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
WHATSAPP_EXPORT_PATH = PROJECT_ROOT / "data" / "whatsapp_export.txt"
VECTOR_DB_PATH = PROJECT_ROOT / "data" / "chroma_db"

@app.on_event("startup")
async def startup_event():
    """Startup event to signal the app is ready"""
    print("=" * 50)
    print("🚀 Farm AI Assistant starting up...")
    print("=" * 50)

# CORS middleware for React Native app
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (with error handling)
llm_service = None
try:
    llm_service = FarmLLMService()
    print("✅ LLM service initialized")
except Exception as e:
    print(f"⚠️ LLM service initialization failed: {e}")
    print("⚠️ App will start but LLM features will be limited")

data_processor = FarmDataProcessor()

# RAG services - will be initialized on first use (lazy loading)
embedding_service = None
vector_store = None
retrieval_engine = None
context_augmenter = None
rag_service = None
rag_init_lock = Lock()


def ensure_vector_store_initialized(store: VectorStore, embedder: EmbeddingService) -> None:
    """Populate vector store from WhatsApp export if collection is empty."""
    current_count = store.count()
    if current_count > 0:
        logger.info("Vector store already populated with %s chunks, skipping initialization", current_count)
        return

    logger.info("Vector store is empty; starting automatic WhatsApp ingestion")
    if not WHATSAPP_EXPORT_PATH.exists():
        logger.warning(
            "WhatsApp export file not found at %s; skipping auto-initialization",
            WHATSAPP_EXPORT_PATH,
        )
        return

    parser = WhatsAppParser()
    chunker = DocumentChunker(min_messages=3, max_messages=20, time_gap_hours=2)

    messages = parser.parse_chat_file(str(WHATSAPP_EXPORT_PATH))
    logger.info("Parsed %s WhatsApp messages", len(messages))

    chunks = chunker.chunk_messages(messages)
    logger.info("Created %s conversation chunks", len(chunks))

    if not chunks:
        logger.warning("No chunks generated from WhatsApp data; vector store remains empty")
        return

    logger.info("Generating embeddings and storing %s chunks in ChromaDB", len(chunks))
    store.add_chunks(chunks, embedder)
    logger.info("Automatic vector store initialization completed; stored chunks=%s", store.count())

def get_rag_service():
    """Lazy-load RAG service on first use to avoid startup timeout"""
    global embedding_service, vector_store, retrieval_engine, context_augmenter, rag_service
    
    if rag_service is None:
        with rag_init_lock:
            if rag_service is None:
                print("🔄 Initializing RAG services...")
                embedding_service = EmbeddingService()
                vector_store = VectorStore(persist_directory=str(VECTOR_DB_PATH))
                ensure_vector_store_initialized(vector_store, embedding_service)
                retrieval_engine = RetrievalEngine(embedding_service, vector_store)
                context_augmenter = ContextAugmenter(max_context_tokens=2000)
                rag_service = RagService(retrieval_engine, context_augmenter, llm_service)
                print("✅ RAG services initialized")
    
    return rag_service

class FarmQuery(BaseModel):
    question: str
    farm_data: Optional[Dict] = None
    conversation_id: Optional[str] = None
    use_rag: bool = False

class FarmResponse(BaseModel):
    answer: str
    confidence: Optional[float] = None
    sources: List[Dict] = []
    conversation_id: Optional[str] = None
    rag_used: Optional[bool] = None
    retrieval_time_ms: Optional[int] = None

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "service": "farm-ai-assistant", "rag": "enabled"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Farm AI Assistant is running!", 
        "rag_enabled": True,
        "version": os.getenv("APP_VERSION", "2.0.0")
    }

@app.post("/ask", response_model=FarmResponse)
async def ask_farm_question(query: FarmQuery):
    try:
        # Check if LLM service is available
        if llm_service is None:
            raise HTTPException(
                status_code=503, 
                detail="LLM service not initialized. Check OPENAI_API_KEY environment variable."
            )
        
        # Process farm data
        processed_data = data_processor.process_farm_data(query.farm_data)

        # Use RAG-enhanced service if requested
        if query.use_rag:
            # Lazy-load RAG service on first use
            rag = get_rag_service()
            
            rag_response = await rag.ask_with_rag(
                question=query.question,
                farm_data=processed_data,
                conversation_id=query.conversation_id,
                use_rag=True
            )

            return FarmResponse(
                answer=rag_response.answer,
                sources=rag_response.sources,
                rag_used=rag_response.rag_used,
                conversation_id=query.conversation_id,
                retrieval_time_ms=rag_response.retrieval_time_ms
            )
        else:
            # Use standard LLM service without RAG
            response = await llm_service.ask_question(
                question=query.question,
                farm_context=processed_data,
                conversation_id=query.conversation_id
            )
            
            return FarmResponse(
                answer=response.get('answer'),
                confidence=response.get('confidence'),
                sources=[],
                conversation_id=response.get('conversation_id'),
                rag_used=False,
                retrieval_time_ms=0
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_farm_data(farm_data: Dict):
    try:
        analysis = await llm_service.analyze_farm_performance(farm_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
