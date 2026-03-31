import requests
import json

RENDER_URL = "https://farm-ai-assistant.onrender.com"

print("=" * 70)
print("TESTING LIVE RENDER DEPLOYMENT")
print("=" * 70)

# Test 1: Health Check
print("\n1️⃣  Health Check...")
try:
    response = requests.get(f"{RENDER_URL}/health", timeout=10)
    print(f"✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Root Endpoint
print("\n2️⃣  Root Endpoint...")
try:
    response = requests.get(f"{RENDER_URL}/", timeout=10)
    print(f"✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Ask WITHOUT RAG
print("\n3️⃣  Testing WITHOUT RAG...")
try:
    payload = {
        "question": "How do I take care of the pigs?",
        "farm_data": {},
        "use_rag": False
    }
    response = requests.post(f"{RENDER_URL}/ask", json=payload, timeout=30)
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"   RAG Used: {result.get('rag_used')}")
    print(f"   Answer: {result.get('answer')[:100]}...")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Ask WITH RAG (WhatsApp History)
print("\n4️⃣  Testing WITH RAG (WhatsApp History)...")
try:
    payload = {
        "question": "How do I take care of the pigs?",
        "farm_data": {},
        "use_rag": True
    }
    response = requests.post(f"{RENDER_URL}/ask", json=payload, timeout=60)
    result = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"   RAG Used: {result.get('rag_used')}")
    print(f"   Sources: {len(result.get('sources', []))}")
    print(f"   Retrieval Time: {result.get('retrieval_time_ms')}ms")
    print(f"   Answer: {result.get('answer')[:150]}...")
    
    if result.get('sources'):
        print(f"\n   📚 Top Source:")
        source = result['sources'][0]
        print(f"      Score: {source['score']}")
        print(f"      Text: {source['text'][:80]}...")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ RENDER DEPLOYMENT TEST COMPLETE")
print("=" * 70)
print(f"\n🌐 Your API is live at: {RENDER_URL}")
print("\nNext: Update React Native app and build APK!")
