from typing import List, Optional
import re
import logging
from datetime import datetime
from app.models.rag_models import ChatMessage, MessageType

logger = logging.getLogger(__name__)


class WhatsAppParser:
    def __init__(self):
        # Pattern for: 2/7/23, 7:45 PM - Bamiche: Message
        self.message_pattern = re.compile(
            r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}\s+[AP]M)\s+-\s+([^:]+):\s+(.+)$'
        )
        # Pattern for system messages: 2/7/23, 7:45 PM - System message (no sender)
        self.system_pattern = re.compile(
            r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}\s+[AP]M)\s+-\s+(.+)$'
        )

    def parse_chat_file(self, file_path: str) -> List[ChatMessage]:
        """Parse WhatsApp export file into structured messages."""
        messages = []
        current_message = None
        skipped_lines = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.rstrip('\n')
                    
                    if not line.strip():
                        continue
                    
                    # Check if this is a new message or continuation
                    if self._is_continuation(line):
                        # Append to current message
                        if current_message:
                            current_message.content += '\n' + line
                    else:
                        # Save previous message
                        if current_message:
                            messages.append(current_message)
                        
                        # Parse new message
                        current_message = self._parse_message_line(line)
                        if current_message is None:
                            skipped_lines += 1
                            logger.warning(f"Skipped line {line_num}: Could not parse")
                
                # Don't forget the last message
                if current_message:
                    messages.append(current_message)
            
            logger.info(f"Parsed {len(messages)} messages from {file_path}")
            if skipped_lines > 0:
                logger.warning(f"Skipped {skipped_lines} invalid lines")
            
            return messages
        
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error parsing file: {e}")
            raise

    def _parse_message_line(self, line: str) -> Optional[ChatMessage]:
        """Parse a single line into a ChatMessage object."""
        # Try to match regular message with sender
        match = self.message_pattern.match(line)
        if match:
            date_str, time_str, sender, content = match.groups()
            
            # Parse timestamp
            timestamp = self._parse_timestamp(date_str, time_str)
            if not timestamp:
                return None
            
            # Determine message type
            message_type = self._determine_message_type(content)
            
            return ChatMessage(
                timestamp=timestamp,
                sender=sender.strip(),
                content=content.strip(),
                message_type=message_type
            )
        
        # Try to match system message (no sender)
        match = self.system_pattern.match(line)
        if match:
            date_str, time_str, content = match.groups()
            
            # Skip system messages (encryption notices, group changes, etc.)
            if self._is_system_message(content):
                return None
            
            # If it's not a system message but has no sender, skip it
            return None
        
        return None

    def _is_continuation(self, line: str) -> bool:
        """Check if line is a continuation of previous message."""
        # If line matches message pattern, it's a new message
        if self.message_pattern.match(line) or self.system_pattern.match(line):
            return False
        return True

    def _parse_timestamp(self, date_str: str, time_str: str) -> Optional[datetime]:
        """Parse date and time strings into datetime object."""
        try:
            # Combine date and time: "2/7/23, 7:45 PM"
            datetime_str = f"{date_str}, {time_str}"
            
            # Try different date formats
            formats = [
                "%m/%d/%y, %I:%M %p",  # 2/7/23, 7:45 PM
                "%d/%m/%y, %I:%M %p",  # 7/2/23, 7:45 PM (alternative)
                "%m/%d/%Y, %I:%M %p",  # 2/7/2023, 7:45 PM
                "%d/%m/%Y, %I:%M %p",  # 7/2/2023, 7:45 PM (alternative)
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(datetime_str, fmt)
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse timestamp: {datetime_str}")
            return None
        
        except Exception as e:
            logger.warning(f"Error parsing timestamp '{date_str}, {time_str}': {e}")
            return None

    def _determine_message_type(self, content: str) -> MessageType:
        """Determine message type based on content."""
        content_lower = content.lower().strip()
        
        # Check for media
        if '<media omitted>' in content_lower or 'image omitted' in content_lower:
            return MessageType.MEDIA
        
        # Check for common system message patterns
        if self._is_system_message(content):
            return MessageType.SYSTEM
        
        return MessageType.TEXT

    def _is_system_message(self, content: str) -> bool:
        """Check if content is a system message."""
        system_keywords = [
            'messages and calls are end-to-end encrypted',
            'created group',
            'added',
            'removed',
            'left',
            'changed this group',
            'changed the subject',
            'you were added',
            'security code changed',
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in system_keywords)