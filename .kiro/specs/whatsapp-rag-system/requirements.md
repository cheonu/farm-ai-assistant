# Requirements Document: WhatsApp RAG System

## Introduction

This feature adds Retrieval-Augmented Generation (RAG) capabilities to the existing Farm AI Assistant by processing and indexing 3 years of WhatsApp channel history. The RAG system will enhance the AI assistant's responses by retrieving relevant historical context from past conversations, enabling more informed and contextually aware answers. This is a learning project focused on understanding AI concepts and Python implementation.

## Glossary

- **RAG_System**: The Retrieval-Augmented Generation system that combines document retrieval with LLM generation
- **WhatsApp_Parser**: Component that extracts and structures messages from WhatsApp chat export files
- **Vector_Store**: Database that stores document embeddings for semantic similarity search
- **Embedding_Service**: Service that converts text into vector representations for similarity matching
- **Retrieval_Engine**: Component that searches the Vector_Store for relevant historical messages
- **Context_Augmenter**: Component that combines retrieved context with user queries before LLM processing
- **Chat_Message**: A single message from WhatsApp history with metadata (sender, timestamp, content)
- **Document_Chunk**: A segment of chat history processed into a retrievable unit
- **Semantic_Search**: Finding relevant documents based on meaning rather than exact keyword matching

## Requirements

### Requirement 1: WhatsApp Chat History Processing

**User Story:** As a developer, I want to parse WhatsApp chat export files, so that I can extract structured message data for indexing.

#### Acceptance Criteria

1. WHEN a WhatsApp chat export file (.txt format) is provided, THE WhatsApp_Parser SHALL extract all messages with sender, timestamp, and content
2. WHEN parsing messages, THE WhatsApp_Parser SHALL handle multi-line messages correctly
3. WHEN parsing messages, THE WhatsApp_Parser SHALL handle media attachments and system messages appropriately
4. WHEN invalid or corrupted lines are encountered, THE WhatsApp_Parser SHALL skip them and log warnings without stopping the process
5. THE WhatsApp_Parser SHALL output structured data containing message text, sender name, timestamp, and message type

### Requirement 2: Document Chunking and Preprocessing

**User Story:** As a developer, I want to chunk chat history into meaningful segments, so that retrieval results are contextually relevant and appropriately sized.

#### Acceptance Criteria

1. WHEN processing parsed messages, THE RAG_System SHALL group messages into Document_Chunks based on temporal proximity and conversation flow
2. WHEN creating Document_Chunks, THE RAG_System SHALL ensure each chunk contains sufficient context (minimum 3 messages, maximum 20 messages)
3. WHEN creating Document_Chunks, THE RAG_System SHALL preserve metadata including date range, participants, and topic indicators
4. THE RAG_System SHALL clean and normalize text by removing excessive whitespace and special characters while preserving meaning
5. WHEN chunking conversations, THE RAG_System SHALL detect topic boundaries using time gaps (messages more than 2 hours apart start new chunks)

### Requirement 3: Vector Embeddings Generation

**User Story:** As a developer, I want to convert chat chunks into vector embeddings, so that I can perform semantic similarity searches.

#### Acceptance Criteria

1. THE Embedding_Service SHALL generate vector embeddings for each Document_Chunk using a pre-trained embedding model
2. WHEN generating embeddings, THE Embedding_Service SHALL use a model suitable for conversational text (e.g., sentence-transformers)
3. THE Embedding_Service SHALL handle batch processing to efficiently embed large volumes of chat history
4. WHEN embedding generation fails for a chunk, THE Embedding_Service SHALL log the error and continue processing remaining chunks
5. THE Embedding_Service SHALL store embeddings with their associated metadata and original text

### Requirement 4: Vector Store Implementation

**User Story:** As a developer, I want to store and query vector embeddings efficiently, so that I can retrieve relevant historical context quickly.

#### Acceptance Criteria

1. THE Vector_Store SHALL persist embeddings and metadata to disk for reuse across application restarts
2. WHEN querying, THE Vector_Store SHALL support semantic similarity search returning top-k most relevant chunks
3. THE Vector_Store SHALL support filtering by metadata (date range, sender, keywords)
4. WHEN storing embeddings, THE Vector_Store SHALL handle incremental updates for new chat data
5. THE Vector_Store SHALL provide query response times under 500ms for typical searches

### Requirement 5: Retrieval Engine Integration

**User Story:** As a developer, I want to retrieve relevant chat history based on user queries, so that the AI assistant has contextual information.

#### Acceptance Criteria

1. WHEN a user query is received, THE Retrieval_Engine SHALL convert the query into a vector embedding
2. WHEN searching, THE Retrieval_Engine SHALL retrieve the top 5 most semantically similar Document_Chunks from the Vector_Store
3. THE Retrieval_Engine SHALL rank results by relevance score and return them in descending order
4. WHEN no relevant results are found (all scores below threshold 0.3), THE Retrieval_Engine SHALL return an empty result set
5. THE Retrieval_Engine SHALL include relevance scores and source metadata with each retrieved chunk

### Requirement 6: Context Augmentation

**User Story:** As a user, I want the AI assistant to use relevant historical context when answering my questions, so that responses are more informed and personalized.

#### Acceptance Criteria

1. WHEN relevant chat history is retrieved, THE Context_Augmenter SHALL format it into a context section for the LLM prompt
2. THE Context_Augmenter SHALL limit total context size to prevent exceeding LLM token limits (maximum 2000 tokens)
3. WHEN formatting context, THE Context_Augmenter SHALL include source attribution (date and participants) for each chunk
4. THE Context_Augmenter SHALL prepend retrieved context to the user query before sending to the LLM
5. WHEN no relevant context is found, THE Context_Augmenter SHALL allow the query to proceed without historical context

### Requirement 7: RAG-Enhanced API Endpoint

**User Story:** As a user, I want to ask questions through an API that uses RAG, so that I get contextually enhanced responses.

#### Acceptance Criteria

1. THE RAG_System SHALL provide a new API endpoint `/ask-with-rag` that accepts user queries
2. WHEN a query is received, THE RAG_System SHALL retrieve relevant context, augment the prompt, and generate a response
3. THE RAG_System SHALL return the AI response along with sources (which chat chunks were used)
4. WHEN RAG retrieval fails, THE RAG_System SHALL fall back to standard LLM response without context
5. THE RAG_System SHALL maintain conversation history for multi-turn dialogues with RAG context

### Requirement 8: Data Ingestion Pipeline

**User Story:** As a developer, I want an automated pipeline to process and index WhatsApp exports, so that I can easily update the knowledge base.

#### Acceptance Criteria

1. THE RAG_System SHALL provide a command-line script to ingest WhatsApp chat export files
2. WHEN running the ingestion script, THE RAG_System SHALL parse, chunk, embed, and store the chat history
3. THE RAG_System SHALL display progress indicators during ingestion (messages processed, chunks created, embeddings generated)
4. WHEN ingestion completes, THE RAG_System SHALL report statistics (total messages, chunks created, processing time)
5. THE RAG_System SHALL support re-ingestion to update the index with new chat data

### Requirement 9: Configuration and Customization

**User Story:** As a developer, I want to configure RAG parameters, so that I can optimize retrieval quality and performance.

#### Acceptance Criteria

1. THE RAG_System SHALL support configuration of chunk size parameters (min/max messages per chunk)
2. THE RAG_System SHALL support configuration of retrieval parameters (top-k results, similarity threshold)
3. THE RAG_System SHALL support configuration of embedding model selection
4. THE RAG_System SHALL load configuration from environment variables or a config file
5. WHEN invalid configuration is provided, THE RAG_System SHALL use sensible defaults and log warnings

### Requirement 10: Error Handling and Logging

**User Story:** As a developer, I want comprehensive error handling and logging, so that I can debug issues and monitor system health.

#### Acceptance Criteria

1. WHEN errors occur during parsing, embedding, or retrieval, THE RAG_System SHALL log detailed error messages with context
2. THE RAG_System SHALL continue processing when non-critical errors occur (e.g., single message parse failure)
3. WHEN critical errors occur (e.g., Vector_Store unavailable), THE RAG_System SHALL raise exceptions with clear error messages
4. THE RAG_System SHALL log performance metrics (retrieval time, embedding time, chunk counts)
5. THE RAG_System SHALL provide different log levels (DEBUG, INFO, WARNING, ERROR) for development and production use
