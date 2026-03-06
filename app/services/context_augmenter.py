from typing import List
from app.models.rag_models import RetrievalResult


class ContextAugmenter:
    def __init__(self, max_context_tokens: int = 2000):
        """Initialize with token limit."""
        self.max_context_tokens = max_context_tokens

    def augment_prompt(self, query: str, retrieved_chunks: List[RetrievalResult]) -> str:
        """Create augmented prompt with context."""
        # If no chunks, return just the query
        if not retrieved_chunks:
            return query

        # Truncate to fit token limit
        truncated_chunks = self._truncate_context(retrieved_chunks, self.max_context_tokens)

        # Format context section
        context_section = self._format_context_section(truncated_chunks)

        # If context is empty after truncation, return just query
        if not context_section:
            return query

        # Build final prompt
        prompt_parts = [
            context_section,
            "---",
            f"CURRENT QUESTION: {query}",
            "",
            "Please answer the question using the historical context above when relevant. If the context doesn't help, answer based on your general knowledge."
        ]

        return '\n'.join(prompt_parts)

    def _format_context_section(self, chunks: List[RetrievalResult]) -> str:
        """Format chunks into context section."""
        if not chunks:
            return ""

        #start with header
        context_parts = ["HISTORICAL CONTEXT FROM WHATSAPP:"]
        context_parts.append("The following are the relevant excerpts from past conversation. \n")

        # format each chunk
        for i, chunk in enumerate(chunks, 1):
            # Extract metadata
            start_date = chunk.metadata.get('start_date','Unknown date')
            participants = chunk.metadata.get('participants', 'Unknown')

             # Format participants (could be a list or string)
            if isinstance(participants,list):
                participants_str = ', '.join(participants)
            else:
                participants_str = participants
            
            # format chunk with header
            chunk_header = f"[Context {i} - {start_date}, participants: {participants_str}]"
            context_parts.append(chunk_header)
            context_parts.append(chunk.text)
            context_parts.append("")
        
        return "\n".join(context_parts)


    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough: 1 token ≈ 4 chars)."""
        return len(text) // 4

    def _truncate_context(self, chunks: List[RetrievalResult],
                         max_tokens: int) -> List[RetrievalResult]:
        """Truncate chunks to fit within token limit."""

        truncated = []
        total_tokens = 0

        for chunk in chunks:
        # Estimate tokens for this chunk
            chunk_tokens = self._estimate_tokens(chunk.text)

        # would this exceed the limit
            if total_tokens + chunk_tokens > max_tokens:
                break #stop adding chunks
            truncated.append(chunk)
            total_tokens+= chunk_tokens
        
        return truncated