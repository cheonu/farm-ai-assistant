import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_without_rag():
    """Test the API without RAG enhancement"""
    print("=" * 70)
    print("TEST 1: WITHOUT RAG")
    print("=" * 70)
    
    payload = {
        "question": "How do I take care of the pigs?",
        "farm_data": {},
        "use_rag": False
    }
    
    response = requests.post(f"{BASE_URL}/ask", json=payload)
    result = response.json()
    
    print(f"Question: {payload['question']}")
    print(f"\nAnswer: {result['answer']}")
    print(f"RAG Used: {result.get('rag_used', 'N/A')}")
    print(f"Sources: {len(result.get('sources', []))}")
    print()

def test_with_rag():
    """Test the API with RAG enhancement"""
    print("=" * 70)
    print("TEST 2: WITH RAG")
    print("=" * 70)
    
    payload = {
        "question": "How do I take care of the pigs?",
        "farm_data": {},
        "use_rag": True
    }
    
    response = requests.post(f"{BASE_URL}/ask", json=payload)
    result = response.json()
    
    print(f"Question: {payload['question']}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nRAG Used: {result.get('rag_used')}")
    print(f"Retrieval Time: {result.get('retrieval_time_ms')}ms")
    print(f"Sources Found: {len(result.get('sources', []))}")
    
    if result.get('sources'):
        print("\nTop Sources:")
        for i, source in enumerate(result['sources'][:3], 1):
            print(f"  {i}. Score: {source['score']}")
            print(f"     Text: {source['text'][:100]}...")
            print()

def test_multiple_questions():
    """Test multiple questions with RAG"""
    print("=" * 70)
    print("TEST 3: MULTIPLE QUESTIONS WITH RAG")
    print("=" * 70)
    
    questions = [
        "What should I do about the irrigation system?",
        "Tell me about the goats",
        "How many eggs did the chickens lay?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Question: {question}")
        
        payload = {
            "question": question,
            "farm_data": {},
            "use_rag": True
        }
        
        response = requests.post(f"{BASE_URL}/ask", json=payload)
        result = response.json()
        
        print(f"   Answer: {result['answer'][:150]}...")
        print(f"   Sources: {len(result.get('sources', []))}")
        print(f"   Time: {result.get('retrieval_time_ms')}ms")

if __name__ == "__main__":
    try:
        # Check if server is running
        health = requests.get(f"{BASE_URL}/health")
        print(f"✅ Server is running: {health.json()}\n")
        
        # Run tests
        test_without_rag()
        test_with_rag()
        test_multiple_questions()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API server")
        print("Please start the server with: python3 -m uvicorn app.main:app --reload")
