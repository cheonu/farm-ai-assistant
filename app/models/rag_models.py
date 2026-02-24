from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

class MessageType(str, Enum):
    TEXT = "text"
    MEDIA = "media"
    SYSTEM = "system"

@dataclass
class ChatMessage:
    timestamp: datetime
    sender: str
    content: str
    message_type: MessageType = MessageType.TEXT

@dataclass
class DocumentChunk:
    id: str
    text: str
    messages: Optional[List[ChatMessage]]
    metadata: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    participants: List[str]
    message_count: int
    embedding: Optional[List[float]] = None

@dataclass
class RetrievalResult:
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any]

from typing import List

@dataclass
class RAGResponse:
    answer: str
    sources: List[RetrievalResult]
    rag_used: bool
    retrieval_time_ms: int

@dataclass
class IngestionConfig:
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    batch_size: int
    vector_store_path: str

@dataclass
class IngestionStats:
    total_documents: int
    total_chunks: int
    total_tokens: int
    processing_time_ms: int
    errors: int = 0

class RAGConfig(BaseModel):
    embedding_model: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2000, ge=0)
    enable_reranking: bool = False