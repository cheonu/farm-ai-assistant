from typing import List
import uuid
from datetime import timedelta
from app.models.rag_models import ChatMessage, DocumentChunk


class DocumentChunker:
    def __init__(self, min_messages: int = 3, max_messages: int = 20,
                 time_gap_hours: int = 2):
        """Initialize chunker with configurable parameters."""
        self.min_messages = min_messages
        self.max_messages = max_messages
        self.time_gap = timedelta(hours=time_gap_hours)

    def chunk_messages(self, messages: List[ChatMessage]) -> List[DocumentChunk]:
        """Group messages into chunks based on time gaps and message count."""
        if not messages:
            return []
        chunks = []
        current_chunk_messages = []

        for message in messages:
            # should we start a new chunk?
            if self._should_start_new_chunk(current_chunk_messages, message):
                # save current chunk if it meets the minimum size
                if len(current_chunk_messages) >= self.min_messages:
                    chunk = self._create_chunk(current_chunk_messages)
                    chunks.append(chunk)

                # start new chunk
                current_chunk_messages = [message]
            else:
                current_chunk_messages.append(message)
        
        # add final chunk if it has enough messages
        if len(current_chunk_messages) >= self.min_messages:
            chunk = self._create_chunk(current_chunk_messages)
            chunks.append(chunk)

        return chunks

    def _should_start_new_chunk(self, current_chunk: List[ChatMessage],
                                next_message: ChatMessage) -> bool:
        """Determine if the next message warrants starting a new chunk."""
        if not current_chunk:
            return False

        # reached max size? start new chunk
        if len(current_chunk) >= self.max_messages:
            return True

        # check time gap with previous message  
        last_message = current_chunk[-1]
        time_diff = next_message.timestamp - last_message.timestamp

        # time gap too large? start new chunk
        if time_diff > self.time_gap:
            return True

        return False

    def _create_chunk (self, messages: List[ChatMessage]) -> DocumentChunk:
        """ create a document chunk from a list of messages """
        # combine all message text
        text = '\n'.join(f"{msg.sender}: {msg.content}" for msg in messages)
        # normalize AFTER combining
        text = self._normalize_text(text)

        # extract unique participants
        participants = list(set(msg.sender for msg in messages))

        # get date range
        start_date = messages[0].timestamp
        end_date = messages[-1].timestamp

        # create a chunk
        return DocumentChunk(
            id=str(uuid.uuid4()),
            text=text,
            messages=messages,
            metadata={
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'participants': participants,
                'message_count': len(messages)
            },
            start_date= start_date,
            end_date=end_date,
            participants=participants,
            message_count=len(messages),
            embedding=None #will be filled later by embedding service
        )
    
    def _normalize_text(self, text:str) -> str:
        """ clean and normalize text. """
        import re
        # remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


      
