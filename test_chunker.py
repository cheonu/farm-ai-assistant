from app.services.whatsapp_parser import WhatsAppParser
from app.services.document_chunker import DocumentChunker

# Parse messages
parser = WhatsAppParser()
messages = parser.parse_chat_file('data/whatsapp_export.txt')

# Chunk them
chunker = DocumentChunker(min_messages=3, max_messages=20, time_gap_hours=2)
chunks = chunker.chunk_messages(messages)

print(f"✅ Created {len(chunks)} chunks from {len(messages)} messages")
print(f"\n📊 Sample chunk:")
chunk = chunks[0]
print(f"   ID: {chunk.id}")
print(f"   Messages: {chunk.message_count}")
print(f"   Participants: {', '.join(chunk.participants)}")
print(f"   Date range: {chunk.start_date} to {chunk.end_date}")
print(f"   Text preview: {chunk.text[:200]}...")
