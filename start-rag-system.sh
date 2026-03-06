#!/bin/bash

echo "🚀 Starting Farm AI Assistant with RAG"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -d "farm-ai-assistant" ] || [ ! -d "PigFarmNew" ]; then
    echo "❌ Error: Please run this script from the parent directory containing both farm-ai-assistant and PigFarmNew"
    exit 1
fi

echo "📋 Setup Instructions:"
echo ""
echo "1️⃣  Terminal 1 - Start FastAPI Backend:"
echo "   cd farm-ai-assistant"
echo "   python3 -m uvicorn app.main:app --reload --host 0.0.0.0"
echo ""
echo "2️⃣  Terminal 2 - Start React Native App:"
echo "   cd PigFarmNew"
echo "   npm start"
echo ""
echo "3️⃣  On your phone/emulator:"
echo "   - Open Expo Go app"
echo "   - Scan the QR code from Terminal 2"
echo "   - Open AI Assistant (Piro)"
echo "   - Toggle RAG ON/OFF with the button in header"
echo ""
echo "✅ RAG Features:"
echo "   - 🧠 RAG ON: Uses 3 years of WhatsApp history"
echo "   - 💭 Basic: Standard AI without history"
echo "   - 📚 Shows sources when RAG is used"
echo "   - ⏱️  Shows retrieval time"
echo ""
echo "🧪 Test Questions:"
echo "   - How do I take care of the pigs?"
echo "   - What should I do about the irrigation system?"
echo "   - Tell me about the goats"
echo ""
echo "======================================"
echo "Ready to start? Open 2 terminals and run the commands above!"
