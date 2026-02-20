# Implementation Plan: WhatsApp RAG System

## Overview

This implementation plan builds a Retrieval-Augmented Generation (RAG) system that enhances the existing Farm AI Assistant with historical context from WhatsApp chat exports. The plan follows an incremental approach: data models → parsing → chunking → embedding → storage → retrieval → augmentation → API integration → ingestion pipeline. Each step builds on previous work and includes testing to validate functionality early.

## Tasks

- [ ] 1. Set up RAG infrastructure and dependencies
  - Install required packages: chromadb, sentence-transformers, hypothesis
  - Update requirements.txt with new dependencies
  - Create directory structure: app/services/rag/, app/models/rag/, tests/rag/
  - Create data directory for vector store: data/chroma_db/
  - _Requirements: 3.1, 4.1_

- [ ] 2. Implement core data models
  - [ ] 2.1 Create RAG data models in app/models/rag_models.py
    - Define MessageType enum (TEXT, MEDIA, SYSTEM)
    - Define ChatMessage dataclass with timestamp, sender, content, message_type
    - Define DocumentChunk dataclass with id, text, messages, metadata, embedding
    - Define RetrievalResult dataclass with chunk_id, text, score, metadata
    - Define RAGResponse dataclass with answer, sources, rag_used, retrieval_time_ms
    - Define IngestionConfig and IngestionStats dataclasses
    - Define RAGConfig Pydantic model with validation
    - _Requirements: 1.5, 2.3, 3.5, 5.5, 7.3, 9.1, 9.2, 9.3, 9.4_

  - [ ]* 2.2 Write property test for data model validation
    - **Property 1: Complete message extraction** (schema validation)
    - **Validates: Requirements 1.5**

- [ ] 3. Implement WhatsApp parser
  - [ ] 3.1 Create WhatsAppParser class in app/services/rag/whatsapp_parser.py
    - Implement parse_chat_file() to read and parse WhatsApp export files
    - Implement _parse_message_line() with regex for timestamp detection
    - Implement _is_continuation() to detect multi-line messages
    - Handle message type detection (TEXT, MEDIA, SYSTEM)
    - Add error handling for invalid lines with logging
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 10.1, 10.2_

  - [ ]* 3.2 Write property test for complete message extraction
    - **Property 1: Complete message extraction**
    - **Validates: Requirements 1.1, 1.5**

  - [ ]* 3.3 Write property test for multi-line message handling
    - **Property 2: Multi-line message handling**
    - **Validates: Requirements 1.2**

  - [ ]* 3.4 Write property test for message type categorization
    - **Property 3: Message type categorization**
    - **Validates: Requirements 1.3**

  - [ ]* 3.5 Write property test for parse error resilience
    - **Property 4: Parse error resilience**
    - **Validates: Requirements 1.4**

  - [ ]* 3.6 Write unit tests for WhatsApp parser edge cases
    - Test empty files, single message, media messages, system messages
    - Test 12-hour vs 24-hour time formats
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 4. Checkpoint - Ensure parser tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement document chunker
  - [ ] 5.1 Create DocumentChunker class in app/services/rag/document_chunker.py
    - Implement chunk_messages() to group messages into chunks
    - Implement _should_start_new_chunk() for boundary detection
    - Enforce min/max message constraints per chunk
    - Detect time gaps for topic boundaries (configurable threshold)
    - Generate chunk metadata (date range, participants, message count)
    - Implement text normalization (remove excessive whitespace)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ]* 5.2 Write property test for chunk size constraints
    - **Property 5: Chunk size constraints**
    - **Validates: Requirements 2.2**

  - [ ]* 5.3 Write property test for time-based chunk boundaries
    - **Property 6: Time-based chunk boundaries**
    - **Validates: Requirements 2.1, 2.5**

  - [ ]* 5.4 Write property test for metadata preservation
    - **Property 7: Metadata preservation**
    - **Validates: Requirements 2.3**

  - [ ]* 5.5 Write property test for text normalization
    - **Property 8: Text normalization consistency**
    - **Validates: Requirements 2.4**

  - [ ]* 5.6 Write unit tests for chunker edge cases
    - Test single message, messages with identical timestamps
    - Test minimum and maximum chunk sizes
    - _Requirements: 2.1, 2.2, 2.5_

- [ ] 6. Implement embedding service
  - [ ] 6.1 Create EmbeddingService class in app/services/rag/embedding_service.py
    - Initialize sentence-transformers model (all-MiniLM-L6-v2)
    - Implement embed_text() for single text embedding
    - Implement embed_batch() for efficient batch processing
    - Implement get_embedding_dimension() to return vector dimensions
    - Add error handling for embedding failures with logging
    - _Requirements: 3.1, 3.3, 3.4, 10.1, 10.2_

  - [ ]* 6.2 Write property test for embedding generation completeness
    - **Property 9: Embedding generation completeness**
    - **Validates: Requirements 3.1**

  - [ ]* 6.3 Write property test for batch processing equivalence
    - **Property 10: Batch processing equivalence**
    - **Validates: Requirements 3.3**

  - [ ]* 6.4 Write property test for embedding error resilience
    - **Property 11: Embedding error resilience**
    - **Validates: Requirements 3.4**

  - [ ]* 6.5 Write unit tests for embedding service
    - Test model initialization, single embedding, batch embedding
    - Test empty text handling, very long text handling
    - _Requirements: 3.1, 3.3, 3.4_

- [ ] 7. Checkpoint - Ensure embedding tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement vector store
  - [ ] 8.1 Create VectorStore class in app/services/rag/vector_store.py
    - Initialize ChromaDB with persistence (PersistentClient)
    - Create or get collection with cosine similarity metric
    - Implement add_chunks() to store chunks with embeddings and metadata
    - Implement query() for similarity search with top-k and filtering
    - Implement count() to return total stored chunks
    - Implement clear() for re-ingestion support
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 3.5_

  - [ ]* 8.2 Write property test for persistence round-trip
    - **Property 12: Persistence round-trip**
    - **Validates: Requirements 3.5, 4.1**

  - [ ]* 8.3 Write property test for top-k retrieval correctness
    - **Property 13: Top-k retrieval correctness**
    - **Validates: Requirements 4.2, 5.2, 5.3**

  - [ ]* 8.4 Write property test for metadata filtering
    - **Property 14: Metadata filtering**
    - **Validates: Requirements 4.3**

  - [ ]* 8.5 Write property test for incremental update correctness
    - **Property 15: Incremental update correctness**
    - **Validates: Requirements 4.4, 8.5**

  - [ ]* 8.6 Write unit tests for vector store
    - Test store and retrieve single/multiple chunks
    - Test query with no results, metadata filtering
    - Test persistence across restarts (mock restart)
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 9. Implement retrieval engine
  - [ ] 9.1 Create RetrievalEngine class in app/services/rag/retrieval_engine.py
    - Initialize with EmbeddingService and VectorStore dependencies
    - Implement retrieve_context() to orchestrate query embedding and search
    - Implement _filter_by_threshold() to filter low-similarity results
    - Format RetrievalResult objects with scores and metadata
    - Add performance logging (retrieval time)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.4_

  - [ ]* 9.2 Write property test for query embedding generation
    - **Property 16: Query embedding generation**
    - **Validates: Requirements 5.1**

  - [ ]* 9.3 Write property test for similarity threshold filtering
    - **Property 17: Similarity threshold filtering**
    - **Validates: Requirements 5.4**

  - [ ]* 9.4 Write property test for result structure completeness
    - **Property 18: Result structure completeness**
    - **Validates: Requirements 5.5**

  - [ ]* 9.5 Write unit tests for retrieval engine
    - Test query with results above/below threshold
    - Test top-k limiting, result ordering
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 10. Checkpoint - Ensure retrieval tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement context augmenter
  - [ ] 11.1 Create ContextAugmenter class in app/services/rag/context_augmenter.py
    - Implement augment_prompt() to combine context and query
    - Implement _format_context_section() to format retrieved chunks
    - Implement _estimate_tokens() for rough token counting (1 token ≈ 4 chars)
    - Implement _truncate_context() to enforce token limits
    - Create prompt template with context section and source attribution
    - Handle empty context case (return query only)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 11.2 Write property test for context formatting
    - **Property 19: Context formatting**
    - **Validates: Requirements 6.1, 6.3**

  - [ ]* 11.3 Write property test for token limit enforcement
    - **Property 20: Token limit enforcement**
    - **Validates: Requirements 6.2**

  - [ ]* 11.4 Write property test for context placement
    - **Property 21: Context placement**
    - **Validates: Requirements 6.4**

  - [ ]* 11.5 Write property test for empty context handling
    - **Property 22: Empty context handling**
    - **Validates: Requirements 6.5**

  - [ ]* 11.6 Write unit tests for context augmenter
    - Test format single/multiple chunks
    - Test token limit truncation, empty context handling
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 12. Implement RAG service
  - [ ] 12.1 Create RAGService class in app/services/rag/rag_service.py
    - Initialize with RetrievalEngine, ContextAugmenter, and FarmLLMService
    - Implement ask_with_rag() to orchestrate complete RAG pipeline
    - Retrieve context using RetrievalEngine
    - Augment prompt using ContextAugmenter
    - Call existing LLMService with augmented prompt
    - Format response with sources and metadata
    - Implement fallback to non-RAG mode on retrieval errors
    - Track retrieval time for performance metrics
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 10.4_

  - [ ]* 12.2 Write property test for end-to-end RAG execution
    - **Property 23: End-to-end RAG execution**
    - **Validates: Requirements 7.2, 7.3**

  - [ ]* 12.3 Write property test for RAG fallback resilience
    - **Property 24: RAG fallback resilience**
    - **Validates: Requirements 7.4**

  - [ ]* 12.4 Write property test for conversation history persistence
    - **Property 25: Conversation history persistence**
    - **Validates: Requirements 7.5**

  - [ ]* 12.5 Write unit tests for RAG service
    - Test end-to-end query processing
    - Test fallback on retrieval failure
    - Test conversation history management
    - _Requirements: 7.2, 7.3, 7.4, 7.5_

- [ ] 13. Checkpoint - Ensure RAG service tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Integrate RAG with FastAPI
  - [ ] 14.1 Add RAG endpoint to app/main.py
    - Initialize RAG service components (singleton pattern)
    - Add POST /ask-with-rag endpoint
    - Define request/response models using Pydantic
    - Handle errors and return appropriate HTTP status codes
    - Add optional use_rag parameter to toggle RAG on/off
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ]* 14.2 Write integration tests for RAG API endpoint
    - Test /ask-with-rag with valid query
    - Test with missing parameters, error responses
    - Test RAG toggle (use_rag=false)
    - _Requirements: 7.1, 7.2, 7.3_

- [ ] 15. Implement ingestion pipeline
  - [ ] 15.1 Create ingestion script scripts/ingest_whatsapp.py
    - Create IngestionPipeline class
    - Implement ingest_file() to orchestrate parsing, chunking, embedding, storage
    - Add command-line argument parsing (file path, clear existing flag)
    - Implement progress indicators using tqdm library
    - Generate and display ingestion statistics
    - Add error handling with detailed logging
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 10.1, 10.2, 10.3_

  - [ ]* 15.2 Write property test for complete ingestion pipeline
    - **Property 26: Complete ingestion pipeline**
    - **Validates: Requirements 8.2**

  - [ ]* 15.3 Write unit tests for ingestion pipeline
    - Test complete ingestion flow with sample data
    - Test progress reporting, statistics generation
    - Test re-ingestion (incremental updates)
    - _Requirements: 8.1, 8.2, 8.5_

- [ ] 16. Implement configuration management
  - [ ] 16.1 Create configuration loading in app/services/rag/config.py
    - Define load_rag_config() to load from environment variables
    - Define load_rag_config_from_file() to load from YAML/JSON
    - Implement validation using RAGConfig Pydantic model
    - Implement default value fallback with warning logging
    - Create example config file: config/rag_config.example.yaml
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 10.1_

  - [ ]* 16.2 Write property test for configuration application
    - **Property 27: Configuration application**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4**

  - [ ]* 16.3 Write property test for invalid configuration handling
    - **Property 28: Invalid configuration handling**
    - **Validates: Requirements 9.5**

  - [ ]* 16.4 Write unit tests for configuration loading
    - Test loading from environment variables
    - Test loading from config file
    - Test invalid configuration with defaults
    - _Requirements: 9.4, 9.5_

- [ ] 17. Implement comprehensive logging
  - [ ] 17.1 Add logging throughout RAG components
    - Configure Python logging with appropriate levels (DEBUG, INFO, WARNING, ERROR)
    - Add performance metric logging (retrieval time, embedding time, chunk counts)
    - Add error logging with context for all error types
    - Add progress logging for long-running operations
    - Create logging configuration file: config/logging_config.yaml
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ]* 17.2 Write property test for non-critical error resilience
    - **Property 29: Non-critical error resilience**
    - **Validates: Requirements 10.2**

  - [ ]* 17.3 Write property test for critical error signaling
    - **Property 30: Critical error signaling**
    - **Validates: Requirements 10.3**

  - [ ]* 17.4 Write property test for comprehensive logging
    - **Property 31: Comprehensive logging**
    - **Validates: Requirements 10.1, 10.4, 10.5**

- [ ] 18. Create documentation and examples
  - [ ] 18.1 Create README for RAG system
    - Document architecture and components
    - Provide setup instructions (dependencies, configuration)
    - Provide usage examples (ingestion, querying)
    - Document configuration options
    - Add troubleshooting section
    - Create docs/rag_system.md

  - [ ] 18.2 Create example WhatsApp export file
    - Create sample export file: examples/sample_whatsapp_export.txt
    - Include various message types (text, media, system)
    - Include multi-line messages and time gaps
    - Document the format in examples/README.md

  - [ ] 18.3 Create example usage scripts
    - Create example_ingest.py showing ingestion usage
    - Create example_query.py showing RAG query usage
    - Add examples to examples/ directory

- [ ] 19. Final checkpoint - Integration testing
  - [ ] 19.1 Run complete end-to-end test
    - Ingest sample WhatsApp export
    - Query RAG system via API
    - Verify relevant context is retrieved and used
    - Verify sources are returned correctly

  - [ ] 19.2 Test persistence
    - Ingest data, restart application
    - Query and verify results still available

  - [ ] 19.3 Test incremental updates
    - Ingest initial data
    - Ingest additional data
    - Query and verify both datasets are searchable

  - [ ] 19.4 Test fallback behavior
    - Simulate vector store failure
    - Query and verify fallback to standard LLM

  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: data models → parsing → chunking → embedding → storage → retrieval → augmentation → API → ingestion
- All components are designed to integrate with the existing FastAPI application
- Configuration is flexible (environment variables or config files) for easy customization
- Comprehensive logging enables debugging and monitoring
