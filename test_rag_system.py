import asyncio
import dotenv
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.retrieval_engine import RetrievalEngine
from app.services.context_augmenter import ContextAugmenter
from app.services.rag_service import RagService
from app.services.llm_service import FarmLLMService
from app.models.rag_models import DocumentChunk
import uuid
from datetime import datetime

# Load environment variables
dotenv.load_dotenv()

async def test_rag_system():
    print("=" * 70)
    print("INITIALIZING RAG SYSTEM")
    print("=" * 70)
    
    # Initialize all services
    embedder = EmbeddingService()
    store = VectorStore()
    retrieval_engine = RetrievalEngine(embedder, store)
    augmenter = ContextAugmenter(max_context_tokens=2000)
    llm_service = FarmLLMService()
    rag_service = RagService(retrieval_engine, augmenter, llm_service)
    
    # Clear and add test data
    store.clear()
    
    texts = [
        "Bamiche: The pigs need feeding at 6am every morning. Use 2kg of feed per pig.",
        "Mum Texas: Don't forget to clean the pig pen this weekend. It's getting dirty.",
        "Chinedu: The irrigation system broke down yesterday. Water pump needs repair.",
        "Bamiche: Goats jumped the fence again. We need to make it taller.",
        "Mum Texas: Chickens laid 12 eggs today. Production is good.",
    ]
    
    print("\nAdding test data to vector store...")
    chunks = []
    for i, text in enumerate(texts):
        embedding = embedder.embed_text(text)
        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            text=text,
            messages=None,
            metadata={
                "start_date": f"2023-02-{7+i:02d}T10:00:00",
                "participants": ["Bamiche", "Mum Texas", "Chinedu"],
                "message_count": 1
            },
            start_date=datetime.now(),
            end_date=datetime.now(),
            participants=["Test"],
            message_count=1,
            embedding=embedding
        )
        chunks.append(chunk)
    
    store.add_chunks(chunks)
    print(f"✅ Added {len(chunks)} chunks\n")
    
    # Test RAG query
    print("=" * 70)
    print("TEST 1: RAG-Enhanced Query")
    print("=" * 70)
    
    question = "How do I take care of the pigs?"
    print(f"Question: {question}\n")
    
    response = await rag_service.ask_with_rag(
        question=question,
        farm_data={},
        use_rag=True
    )
    
    print(f"Answer: {response.answer}\n")
    print(f"RAG Used: {response.rag_used}")
    print(f"Retrieval Time: {response.retrieval_time_ms}ms")
    print(f"Sources Found: {len(response.sources)}\n")
    
    if response.sources:
        print("Sources:")
        for i, source in enumerate(response.sources, 1):
            print(f"  {i}. Score: {source['score']}")
            print(f"     Text: {source['text'][:100]}...\n")
    
    # Test without RAG
    print("=" * 70)
    print("TEST 2: Without RAG (Baseline)")
    print("=" * 70)
    
    response_no_rag = await rag_service.ask_with_rag(
        question=question,
        farm_data={},
        use_rag=False
    )
    
    print(f"Answer: {response_no_rag.answer}\n")
    print(f"RAG Used: {response_no_rag.rag_used}")
    print(f"Sources: {len(response_no_rag.sources)}")

if __name__ == "__main__":
    asyncio.run(test_rag_system())
