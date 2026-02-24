class DocumentChunker:
    def __init__(self, min_messages: int = 3, max_messages: int = 20, 
                 time_gap_hours: int = 2):
        """Initialize chunker with configurable parameters."""
        pass

    def chunk_messages(self, messages: List[ChatMessage]) -> List[DocumentChunk]:
        """Group messages into chunks based on time gaps and message count """
        pass

    def _should_start_new_chunk (self, current_chunk: List[ChatMessage], next_message: ChatMessage) -> bool:
        """ Determine if the next message warrants starting a new chunk """
        pass
