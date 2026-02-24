class WhatsAppParser:
    def parse_chat_file(self, file_path: str) -> List[ChatMessage]:
        """Parse WhatsApp export file into structured messages."""
        pass
    
    def _parse_message_line(self, line: str) -> Optional[ChatMessage]:
        """Parse a single line into a ChatMessage object."""
        pass
    
    def _is_continuation(self, line: str) -> bool:
        """Check if line is a continuation of previous message."""
        pass