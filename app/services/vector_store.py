from typing import List, Dict, Optional
import chromadb
from app.models.rag_models import DocumentChunk, RetrievalResult


class VectorStore:
    def __init__(self, persist_directory: str = './data/chroma_db'):
        """Initialize ChromaDB with persistence."""
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="whatsapp_history",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Add document chunks with embeddings to store."""
        valid_chunks = [c for c in chunks if c.embedding is not None]

        if not valid_chunks:
            print ("No chunks with embeddings to add")
            return
        
        # extract data from embeddings
        ids = [chunk.id for chunk in valid_chunks]
        embeddings = [chunk.embedding for chunk in valid_chunks]
        documents=[chunk.text for chunk in valid_chunks]
        metadatas = [chunk.metadata for chunk in valid_chunks]

        # add to chromadb
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        print(f"Added {len(valid_chunks)} chunks to vector store")


    def query(self, query_embedding: List[float], top_k: int = 5,
              filters: Optional[Dict] = None) -> List[RetrievalResult]:
        """Query for similar chunks."""
        results = self.collection.query(
           query_embeddings=[query_embedding],
           n_results=top_k,
           where=filters    
        )

        # parse results

        retrieval_results = []

        # chromadb returns list of lists, we want first result set
        ids = results['ids'][0]
        distances = results['distances'][0]
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]

        # create RetrievalResult objects
        for i in range (len(ids)):
            # convert distance to similarity
            similarity = 1 -  distances[i] # cosine distance to similarity score

            result = RetrievalResult(
                chunk_id=ids[i],
                text=documents[i],
                score=similarity,
                metadata=metadatas[i]
            )
            retrieval_results.append(result)
        return retrieval_results

    def count(self) -> int:
        """Return total number of stored chunks."""
        return self.collection.count()

    def clear(self) -> None:
        """Clear all data (for re-ingestion)."""
        self.client.delete_collection(name="whatsapp_history")
        self.collection = self.client.get_or_create_collection(
            name="whatsapp_history",
            metadata={"hnsw:space": "cosine"}
        )


