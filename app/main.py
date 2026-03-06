from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

from .services.llm_service import FarmLLMService
from .services.rag_service import RagService
from .services.embedding_service import EmbeddingService
from .services.vector_store import VectorStore
from .services.retrieval_engine import RetrievalEngine
from .services.context_augmenter import ContextAugmenter
from .utils.data_processor import FarmDataProcessor

# Load environment variables
load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Farm AI Assistant"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="AI-powered farm management assistant"
)

# CORS middleware for React Native app
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_service = FarmLLMService()
data_processor = FarmDataProcessor()

# RAG services - will be initialized on first use (lazy loading)
embedding_service = None
vector_store = None
retrieval_engine = None
context_augmenter = None
rag_service = None

def get_rag_service():
    """Lazy-load RAG service on first use to avoid startup timeout"""
    global embedding_service, vector_store, retrieval_engine, context_augmenter, rag_service
    
    if rag_service is None:
        print("🔄 Initializing RAG services...")
        embedding_service = EmbeddingService()
        vector_store = VectorStore(persist_directory="data/chroma_db")
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
    return {"status": "healthy", "service": "farm-ai-assistant"}

@app.get("/")
async def root():
    return {"message": "Farm AI Assistant is running!", "rag_enabled": True}

@app.post("/ask", response_model=FarmResponse)
async def ask_farm_question(query: FarmQuery):
    try:
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
    uvicorn.run(app, host="0.0.0.0", port=8000)