from app.services.context_augmenter import ContextAugmenter
from app.models.rag_models import RetrievalResult

# Initialize augmenter
augmenter = ContextAugmenter(max_context_tokens=500)

# Create sample retrieval results
chunks = [
    RetrievalResult(
        chunk_id="1",
        text="Bamiche: The pigs need feeding at 6am every morning\nMum Texas: How much feed per pig?\nBamiche: About 2kg per pig",
        score=0.85,
        metadata={
            "start_date": "2023-02-07T06:00:00",
            "end_date": "2023-02-07T06:15:00",
            "participants": ["Bamiche", "Mum Texas"],
            "message_count": 3
        }
    ),
    RetrievalResult(
        chunk_id="2",
        text="Chinedu: Don't forget to clean the pig pen this weekend\nBamiche: Will do, thanks",
        score=0.72,
        metadata={
            "start_date": "2023-02-08T10:00:00",
            "end_date": "2023-02-08T10:05:00",
            "participants": ["Chinedu", "Bamiche"],
            "message_count": 2
        }
    )
]

# Test with context
query = "How do I take care of the pigs?"
print("=" * 70)
print("TEST 1: With Context")
print("=" * 70)
augmented_prompt = augmenter.augment_prompt(query, chunks)
print(augmented_prompt)

# Test without context
print("\n" + "=" * 70)
print("TEST 2: Without Context (empty chunks)")
print("=" * 70)
augmented_prompt_empty = augmenter.augment_prompt(query, [])
print(augmented_prompt_empty)

# Test token estimation
print("\n" + "=" * 70)
print("TEST 3: Token Estimation")
print("=" * 70)
sample_text = "The pigs need feeding at 6am"
tokens = augmenter._estimate_tokens(sample_text)
print(f"Text: '{sample_text}'")
print(f"Characters: {len(sample_text)}")
print(f"Estimated tokens: {tokens}")
