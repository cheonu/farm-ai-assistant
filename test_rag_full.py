import asyncio
import dotenv
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.retrieval_engine import RetrievalEngine
from app.services.context_augmenter import ContextAugmenter
from app.services.rag_service import RagService
from app.services.llm_service import FarmLLMService

# Load environment variables
dotenv.load_dotenv()

async def test_with_full_dataset():
    print("=" * 70)
    print("RAG SYSTEM TEST - FULL WHATSAPP DATASET")
    print("=" * 70)
    
    # Initialize all services (using existing vector store with 1,274 chunks)
    print("\nInitializing services...")
    embedder = EmbeddingService()
    store = VectorStore(persist_directory="data/chroma_db")
    retrieval_engine = RetrievalEngine(embedder, store)
    augmenter = ContextAugmenter(max_context_tokens=2000)
    llm_service = FarmLLMService()
    rag_service = RagService(retrieval_engine, augmenter, llm_service)
    
    print("✅ Services initialized")
    print(f"✅ Using vector store with your full WhatsApp history\n")
    
    # Test questions
    questions = [
        "How do I take care of the pigs?",
        "What should I do about the irrigation system?",
        "Tell me about the goats",
    ]
    
    for i, question in enumerate(questions, 1):
        print("=" * 70)
        print(f"TEST {i}")
        print("=" * 70)
        print(f"Question: {question}\n")
        
        response = await rag_service.ask_with_rag(
            question=question,
            farm_data={},
            use_rag=True
        )
        
        print(f"Answer:\n{response.answer}\n")
        print(f"📊 RAG Used: {response.rag_used}")
        print(f"⏱️  Retrieval Time: {response.retrieval_time_ms}ms")
        print(f"📚 Sources Found: {len(response.sources)}\n")
        
        if response.sources:
            print("Top Sources:")
            for j, source in enumerate(response.sources[:3], 1):
                print(f"  {j}. Score: {source['score']}")
                print(f"     Text: {source['text'][:150]}...")
                print(f"     Date: {source['metadata'].get('start_date', 'N/A')}")
                print()

if __name__ == "__main__":
    asyncio.run(test_with_full_dataset())
