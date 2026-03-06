from typing import List
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.models.rag_models import RetrievalResult
import logging
logger = logging.getLogger(__name__)


class RetrievalEngine:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):
        """Initialize embedding service and vector store."""
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve_context(self, query: str, top_k: int = 5,
                        similarity_threshold: float = 0.3) -> List[RetrievalResult]:
        """Retrieve relevant chunks for query."""

        logging.info(f"Retrieving context for query: '{query[:50]}...'")
        # Step 1: Embed the query
        query_embedding = self.embedding_service.embed_text(query)

        # Step 2: Search vector store
        results = self.vector_store.query(query_embedding, top_k=top_k)
        logging.info(f"Found: {len(results)} results from vector store")

        # Step 3: Filter by threshold
        filtered_results = self._filter_by_threshold(results,similarity_threshold)
        logging.info(f"After filtering: {len(filtered_results)} results above threshold {similarity_threshold}")

        return filtered_results
        

    def _filter_by_threshold(self, results: List[RetrievalResult],
                            threshold: float) -> List[RetrievalResult]:
        """Filter results below similarity threshold."""
        # filtered = []
        # for r in results:
        #     if r.score >= threshold:
        #         filtered.append(r)
            
        # return filtered
        filtered = [r for r in results if r.score >= threshold]
        return filtered

      