# Deploying Farm AI Assistant with RAG to Render

## Prerequisites
- GitHub account
- Render account (free tier works)
- OpenAI API key

## Deployment Steps

### 1. Prepare the Repository

```bash
cd farm-ai-assistant

# Check git status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Add RAG system with WhatsApp history integration"

# Push to GitHub
git push origin main
```

### 2. Deploy to Render

#### Option A: Using render.yaml (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Select the `farm-ai-assistant` repository
5. Render will detect `render.yaml` automatically
6. Click "Apply"

#### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `farm-ai-assistant-rag`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `farm-ai-assistant` if in monorepo)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

5. Add Environment Variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `APP_NAME`: Farm AI Assistant with RAG
   - `APP_VERSION`: 2.0.0
   - `ALLOWED_ORIGINS`: *

6. Click "Create Web Service"

### 3. Wait for Deployment

- First deployment takes 5-10 minutes
- Render will:
  - Install dependencies (including sentence-transformers, chromadb)
  - Download the embedding model (~90MB)
  - Start the FastAPI server
  - Your vector database (data/chroma_db) will be included

### 4. Get Your Render URL

Once deployed, you'll get a URL like:
```
https://farm-ai-assistant-rag.onrender.com
```

### 5. Test the Deployment

```bash
# Test health endpoint
curl https://farm-ai-assistant-rag.onrender.com/health

# Test RAG endpoint
curl -X POST https://farm-ai-assistant-rag.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I take care of the pigs?",
    "farm_data": {},
    "use_rag": true
  }'
```

### 6. Update React Native App

Update `PigFarmNew/components/AIAssistant.js`:

```javascript
const AI_API_URL = 'https://farm-ai-assistant-rag.onrender.com';
```

Then rebuild your React Native app:
```bash
cd PigFarmNew
npm start
```

## Important Notes

### Vector Database Persistence

⚠️ **Render Free Tier Limitation**: The free tier doesn't have persistent disk storage. This means:

- Your vector database is included in the deployment
- It works fine while the service is running
- **BUT**: If Render restarts your service (after 15 min inactivity), the vector database is reset

### Solutions:

#### Option 1: Upgrade to Paid Plan ($7/month)
- Includes persistent disk storage
- Vector database persists across restarts

#### Option 2: Rebuild Vector Store on Startup
Add a startup script that checks if vector store exists, and rebuilds it if missing:

```python
# In app/main.py, add after service initialization:
@app.on_event("startup")
async def startup_event():
    # Check if vector store is empty
    if vector_store.count() == 0:
        print("🔄 Vector store empty, rebuilding from WhatsApp data...")
        # Run ingestion script
        from scripts.ingest_whatsapp import main as ingest
        ingest()
```

#### Option 3: Use External Vector Database
- Use Pinecone (free tier available)
- Use Weaviate Cloud
- Use Qdrant Cloud

### Cold Start Warning

⚠️ Render free tier services sleep after 15 minutes of inactivity:
- First request after sleep takes 30-60 seconds
- Subsequent requests are fast
- This is normal for free tier

## Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Check Python version matches (3.11)
- Check logs in Render dashboard

### Service Crashes
- Check environment variables are set
- Check OPENAI_API_KEY is valid
- Check logs for errors

### RAG Not Working
- Verify vector database was included in deployment
- Check `/health` endpoint works
- Test with `use_rag: false` first, then `use_rag: true`

## Monitoring

Check your service health:
```bash
# Health check
curl https://your-service.onrender.com/health

# Check vector store
curl https://your-service.onrender.com/docs
```

## Next Steps

1. Deploy to Render
2. Test the RAG endpoints
3. Update React Native app with new URL
4. Consider upgrading to paid plan for persistence
5. Monitor usage and costs

🎉 Your RAG system is now live!
