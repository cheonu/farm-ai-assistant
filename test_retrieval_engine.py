from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.retrieval_engine import RetrievalEngine
from app.models.rag_models import DocumentChunk
import uuid
from datetime import datetime

# Initialize services
embedder = EmbeddingService()
store = VectorStore()
retrieval_engine = RetrievalEngine(embedder, store)

# Clear and add test data
store.clear()

texts = [
    "The pigs need feeding at 6am every morning",
    "Irrigation system broke down, needs repair",
    "Goats jumped the fence again today",
    "Pig pen needs cleaning this weekend",
    "Water pump for irrigation is not working",
    "Chickens laid 12 eggs today",
    "Tractor needs oil change soon"
]

print("Setting up test data...")
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

store.add_chunks(chunks)
print(f"✅ Added {len(chunks)} chunks to store\n")

# Test retrieval with different queries
queries = [
    "How do I care for the pigs?",
    "What's wrong with the water system?",
    "Tell me about the chickens"
]

for query in queries:
    print(f"🔍 Query: '{query}'")
    
    # Retrieve with threshold
    results = retrieval_engine.retrieve_context(
        query=query,
        top_k=3,
        similarity_threshold=0.3
    )
    
    print(f"📊 Found {len(results)} relevant results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result.score:.3f}")
        print(f"   Text: {result.text}\n")
    
    print("-" * 60 + "\n")
