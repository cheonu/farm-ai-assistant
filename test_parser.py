#!/usr/bin/env python3
"""Quick test script for WhatsApp parser."""

import logging
from app.services.whatsapp_parser import WhatsAppParser

# Set up logging
logging.basicConfig(level=logging.INFO)

# Test the parser
parser = WhatsAppParser()
messages = parser.parse_chat_file('data/whatsapp_export.txt')

print(f"\n✅ Successfully parsed {len(messages)} messages!")
print(f"\n📊 Sample messages:\n")

# Show first 5 messages
for i, msg in enumerate(messages[:5], 1):
    print(f"{i}. [{msg.timestamp}] {msg.sender}: {msg.content[:60]}...")
    print(f"   Type: {msg.message_type.value}\n")

# Show statistics
print(f"\n📈 Statistics:")
print(f"   Total messages: {len(messages)}")
print(f"   Date range: {messages[0].timestamp} to {messages[-1].timestamp}")

# Count message types
from collections import Counter
type_counts = Counter(msg.message_type for msg in messages)
print(f"\n   Message types:")
for msg_type, count in type_counts.items():
    print(f"     {msg_type.value}: {count}")

# Count senders
sender_counts = Counter(msg.sender for msg in messages)
print(f"\n   Top 5 senders:")
for sender, count in sender_counts.most_common(5):
    print(f"     {sender}: {count} messages")
