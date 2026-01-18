from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

from .services.llm_service import FarmLLMService
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

class FarmQuery(BaseModel):
    question: str
    farm_data: Optional[Dict] = None
    conversation_id: Optional[str] = None

class FarmResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[str]
    conversation_id: str

@app.get("/")
async def root():
    return {"message": "Farm AI Assistant is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "farm-ai-assistant"}

@app.post("/ask", response_model=FarmResponse)
async def ask_farm_question(query: FarmQuery):
    try:
        # Process farm data
        processed_data = data_processor.process_farm_data(query.farm_data)
        
        # Get AI response
        response = await llm_service.ask_question(
            question=query.question,
            farm_context=processed_data,
            conversation_id=query.conversation_id
        )
        
        return response
    
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