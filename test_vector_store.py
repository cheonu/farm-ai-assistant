from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.models.rag_models import DocumentChunk
import uuid
from datetime import datetime

# Initialize services
embedder = EmbeddingService()
store = VectorStore()

# Clear existing data
store.clear()

# Create sample chunks with embeddings
texts = [
    "The pigs need feeding at 6am every morning",
    "Irrigation system broke down, needs repair",
    "Goats jumped the fence again today",
    "Pig pen needs cleaning this weekend",
    "Water pump for irrigation is not working"
]

print("Creating and embedding chunks...")
chunks = []
for text in texts:
    embedding = embedder.embed_text(text)
    chunk = DocumentChunk(
        id=str(uuid.uuid4()),
        text=text,
        messages=None,
        metadata={"topic": "farm"},
        start_date=datetime.now(),
        end_date=datetime.now(),
        participants=["Test"],
        message_count=1,
        embedding=embedding
    )
    chunks.append(chunk)

# Add to vector store
print(f"Adding {len(chunks)} chunks to vector store...")
store.add_chunks(chunks)

# Check count
print(f"✅ Total chunks in store: {store.count()}")

# Test query
query_text = "How do I take care of the pigs?"
print(f"\n🔍 Query: '{query_text}'")

query_embedding = embedder.embed_text(query_text)
results = store.query(query_embedding, top_k=3)

print(f"\n📊 Top 3 results:")
for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result.score:.3f}")
    print(f"   Text: {result.text}")
