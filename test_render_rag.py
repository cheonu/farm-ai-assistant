import requests
import json

# Your Render URL
RENDER_URL = "https://farm-ai-assistant.onrender.com"

def test_render_deployment():
    print("=" * 70)
    print("TESTING RAG SYSTEM ON RENDER")
    print("=" * 70)
    
    # Test 1: Health Check
    print("\n1️⃣  Testing Health Endpoint...")
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Render: {e}")
        return
    
    # Test 2: Without RAG
    print("\n2️⃣  Testing WITHOUT RAG...")
    try:
        payload = {
            "question": "How do I take care of the pigs?",
            "farm_data": {},
            "use_rag": False
        }
        response = requests.post(f"{RENDER_URL}/ask", json=payload, timeout=30)
        result = response.json()
        print(f"✅ Response received")
        print(f"   RAG Used: {result.get('rag_used')}")
        print(f"   Answer: {result.get('answer')[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: With RAG
    print("\n3️⃣  Testing WITH RAG (WhatsApp History)...")
    try:
        payload = {
            "question": "How do I take care of the pigs?",
            "farm_data": {},
            "use_rag": True
        }
        response = requests.post(f"{RENDER_URL}/ask", json=payload, timeout=30)
        result = response.json()
        print(f"✅ Response received")
        print(f"   RAG Used: {result.get('rag_used')}")
        print(f"   Sources Found: {len(result.get('sources', []))}")
        print(f"   Retrieval Time: {result.get('retrieval_time_ms')}ms")
        print(f"   Answer: {result.get('answer')[:150]}...")
        
        if result.get('sources'):
            print(f"\n   📚 Top Source:")
            source = result['sources'][0]
            print(f"      Score: {source['score']}")
            print(f"      Text: {source['text'][:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ RENDER DEPLOYMENT TEST COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Commit React app changes: cd PigFarmNew && git add . && git commit -m 'Connect to Render'")
    print("2. Push: git push")
    print("3. Test on your phone!")

if __name__ == "__main__":
    test_render_deployment()
