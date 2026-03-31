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

    def add_chunks(self, chunks: List[DocumentChunk], embedding_service) -> None:
        """Add document chunks with embeddings to store."""
        if not chunks:
            print("No chunks to add")
            return
        
        # Generate embeddings for chunks
        print(f"Generating embeddings for {len(chunks)} chunks...")
        for idx, chunk in enumerate(chunks, start=1):
            chunk.embedding = embedding_service.embed_text(chunk.text)
            if idx % 100 == 0 or idx == len(chunks):
                print(f"Progress: embedded {idx}/{len(chunks)} chunks")
        
        # Extract data for ChromaDB
        chunk_ids = [chunk.id for chunk in chunks]
        embeddings = [chunk.embedding for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        # Add to chromadb
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        print(f"✅ Added {len(chunks)} chunks to vector store")


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

