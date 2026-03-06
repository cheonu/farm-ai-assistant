from typing import List, Dict, Optional
from app.services.retrieval_engine import RetrievalEngine
from app.services.context_augmenter import ContextAugmenter
from app.services.llm_service import FarmLLMService
from app.models.rag_models import RAGResponse, RetrievalResult
import time
import logging

logger = logging.getLogger(__name__)


class RagService:
    def __init__(self, retrieval_engine: RetrievalEngine,
                 context_augmenter: ContextAugmenter,
                 llm_service: FarmLLMService):
        """Initialize RAG service with dependencies."""
        self.retrieval_engine = retrieval_engine
        self.context_augmenter = context_augmenter
        self.llm_service = llm_service

    async def ask_with_rag(
        self,
        question: str,
        farm_data: Optional[Dict] = None,
        conversation_id: Optional[str] = None,
        use_rag: bool = True
    ) -> RAGResponse:
        """Process query with RAG enhancement."""
        start_time = time.time()
        retrieved_chunks = []
        rag_used = False

        try:
            # step 1: Retrieve context (if RAG is enabled)
            if use_rag:
                logger.info(f"Retrieving context for: '{question[:50]}...")

                retrieved_chunks = self.retrieval_engine.retrieve_context(
                    query=question,
                    top_k=5,
                    similarity_threshold=0.3
                )
                logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")

            # step 2: Augument prompt with context
            if retrieved_chunks:
                augumented_prompt = self.context_augmenter.augment_prompt(
                    query=question,
                    retrieved_chunks=retrieved_chunks
                )
                rag_used = True
                logger.info("Using RAG-enhanced prompt")
            else:
                augumented_prompt = question
                logger.info("No relevant context found, using original question")

            # step 3: Generate answer using LLM
            llm_response = await self.llm_service.ask_question(
                question=augumented_prompt,
                farm_context=farm_data,
                conversation_id=conversation_id
            )

            # Step 4: Calculate retrieval time
            retrieval_time_ms = int((time.time() - start_time) * 1000)
            
            # Step 5: Format sources
            sources = self._format_sources(retrieved_chunks) if retrieved_chunks else []
            
            # Step 6: Create response
            return RAGResponse(
                answer=llm_response.get('answer', llm_response),
                sources=sources,
                rag_used=rag_used,
                retrieval_time_ms=retrieval_time_ms
            )
        
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            
            # Fallback: Try without RAG
            try:
                logger.info("Falling back to non-RAG mode")
                llm_response = await self.llm_service.ask_question(
                    question=question,
                    farm_context=farm_data,
                    conversation_id=conversation_id
                )
                
                retrieval_time_ms = int((time.time() - start_time) * 1000)
                
                return RAGResponse(
                    answer=llm_response.get('answer', llm_response),
                    sources=[],
                    rag_used=False,
                    retrieval_time_ms=retrieval_time_ms
                )
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                raise

    def _format_sources(self, chunks: List[RetrievalResult]) -> List[Dict]:
        """Format source information for response."""
        sources = []
        for chunk in chunks:
            source = {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                "score": round(chunk.score, 3),
                "metadata": chunk.metadata
            }
            sources.append(source)
        
        return sources
