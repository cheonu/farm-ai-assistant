from typing import List
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with sentence-transformers model."""
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        embedding = self.model.encode (text)
        return embedding.tolist ()

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(
            texts, 
            batch_size=batch_size,
            show_progress_bar=True
            )
        return embeddings.tolist()

    def get_embedding_dimension(self) -> int:
        """Return dimension of embedding vectors."""
        return self.model.get_sentence_embedding_dimension()

    # error handling 
    def embed_text (self, text: str) -> List[float]:
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Error embedding text: {e}")
            # return zero vector as fallback
            return [0.0] * self.get_embedding_dimension()
