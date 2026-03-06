from app.services.embedding_service import EmbeddingService

# Initialize service
print("Loading model...")
service = EmbeddingService()

# Test single embedding
text = "The pigs need feeding at 6am"
embedding = service.embed_text(text)

print(f"\n✅ Single embedding:")
print(f"   Text: {text}")
print(f"   Dimension: {len(embedding)}")
print(f"   First 5 values: {embedding[:5]}")

# Test batch embedding
texts = [
    "The pigs need feeding at 6am",
    "Irrigation system needs repair",
    "Goats jumped the fence again"
]
embeddings = service.embed_batch(texts)

print(f"\n✅ Batch embeddings:")
print(f"   Texts: {len(texts)}")
print(f"   Embeddings: {len(embeddings)}")
print(f"   Dimension: {service.get_embedding_dimension()}")

# Test similarity (bonus!)
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

sim1 = cosine_similarity(embeddings[0], embeddings[1])
sim2 = cosine_similarity(embeddings[0], embeddings[2])

print(f"\n🔍 Similarity test:")
print(f"   'pigs feeding' vs 'irrigation': {sim1:.3f}")
print(f"   'pigs feeding' vs 'goats fence': {sim2:.3f}")
