# Bugfix Requirements Document

## Introduction

The RAG system currently requires manual initialization of the ChromaDB vector database after deployment. When the FastAPI application starts in a GKE pod, the vector database is empty, causing RAG queries to return no context. This bug affects the user experience by requiring manual intervention via `kubectl exec` to run initialization scripts that parse 14,667 WhatsApp messages into 1,274 conversation chunks and populate the database.

This bugfix implements automatic initialization that checks the database state on startup and populates it with WhatsApp chat data when empty, eliminating the need for manual intervention.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the FastAPI application starts up in a GKE pod THEN the ChromaDB collection is empty or doesn't exist

1.2 WHEN the RAG service is lazy-loaded via `get_rag_service()` THEN it initializes services but never checks if the vector database needs population

1.3 WHEN a user makes the first RAG query with an empty database THEN the query returns no context because no embeddings exist

1.4 WHEN the pod restarts or is redeployed THEN users must manually run `kubectl exec` with initialization scripts to populate the database

### Expected Behavior (Correct)

2.1 WHEN the FastAPI application starts up or the RAG service is first accessed THEN the system SHALL check if the ChromaDB collection is empty or doesn't exist

2.2 WHEN the ChromaDB collection is empty or doesn't exist THEN the system SHALL automatically parse the WhatsApp data file at `data/whatsapp_export.txt`

2.3 WHEN parsing WhatsApp data THEN the system SHALL chunk the 14,667 messages into 1,274 conversation chunks

2.4 WHEN conversation chunks are created THEN the system SHALL generate embeddings for all chunks using the embedding service

2.5 WHEN embeddings are generated THEN the system SHALL store them in the ChromaDB vector database in the `whatsapp_conversations` collection

2.6 WHEN initialization is in progress THEN the system SHALL log the initialization progress (e.g., number of chunks processed, completion status)

2.7 WHEN initialization completes successfully THEN subsequent RAG queries SHALL return relevant context from the populated database

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the ChromaDB collection already contains data THEN the system SHALL CONTINUE TO skip initialization and use the existing data

3.2 WHEN a RAG query is made with a populated database THEN the system SHALL CONTINUE TO retrieve and return relevant context as before

3.3 WHEN the embedding service generates embeddings THEN the system SHALL CONTINUE TO use the same embedding model and parameters

3.4 WHEN the WhatsApp parser processes messages THEN the system SHALL CONTINUE TO use the same parsing logic and chunking strategy

3.5 WHEN the vector store performs similarity searches THEN the system SHALL CONTINUE TO use the same search algorithms and ranking

3.6 WHEN the persistent volume stores ChromaDB data THEN the system SHALL CONTINUE TO persist data across pod restarts


## Bug Condition Specification

### Bug Condition Function

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type ApplicationStartupState
  OUTPUT: boolean
  
  // Returns true when the bug condition is met
  // Bug occurs when app starts with empty or non-existent ChromaDB collection
  RETURN (X.chromadb_collection_exists = false) OR 
         (X.chromadb_collection_exists = true AND X.chromadb_collection_count = 0)
END FUNCTION
```

### Property Specification: Fix Checking

```pascal
// Property: Automatic Initialization on Empty Database
FOR ALL X WHERE isBugCondition(X) DO
  result ← startupWithAutoInit'(X)
  
  ASSERT result.whatsapp_file_parsed = true
  ASSERT result.chunks_created = 1274
  ASSERT result.embeddings_generated = 1274
  ASSERT result.chromadb_populated = true
  ASSERT result.initialization_logged = true
  ASSERT result.rag_queries_return_context = true
END FOR
```

### Property Specification: Preservation Checking

```pascal
// Property: Skip Initialization When Database Already Populated
FOR ALL X WHERE NOT isBugCondition(X) DO
  // F = original behavior, F' = fixed behavior
  ASSERT F(X).chromadb_data = F'(X).chromadb_data
  ASSERT F(X).rag_query_results = F'(X).rag_query_results
  ASSERT F(X).embedding_model = F'(X).embedding_model
  ASSERT F(X).parsing_logic = F'(X).parsing_logic
  ASSERT F(X).search_behavior = F'(X).search_behavior
END FOR
```

### Key Definitions

- **F**: The original (unfixed) function - RAG service initialization without automatic database population check
- **F'**: The fixed function - RAG service initialization with automatic database population when empty
- **C(X)**: Bug Condition - ChromaDB collection is empty or doesn't exist at startup
- **¬C(X)**: Non-buggy inputs - ChromaDB collection already contains data
- **P(result)**: Property - Automatic parsing, chunking, embedding generation, and database population with logging

### Counterexample

```
Input: GKE pod starts with empty ChromaDB at data/chroma_db/
Current Behavior: RAG service initializes but database remains empty
Expected Behavior: RAG service detects empty database, parses data/whatsapp_export.txt,
                   creates 1,274 chunks, generates embeddings, populates ChromaDB,
                   logs progress, and enables context retrieval for queries
```
