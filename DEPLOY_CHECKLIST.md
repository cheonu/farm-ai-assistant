# 🚀 Render Deployment Checklist

## ✅ Pre-Deployment Checklist

- [x] RAG system implemented and tested locally
- [x] Vector database created (1,274 chunks from WhatsApp)
- [x] All dependencies in requirements.txt
- [x] render.yaml configuration file created
- [x] DEPLOYMENT.md guide created
- [ ] Git repository ready
- [ ] OpenAI API key ready

## 📦 What's Being Deployed

### Core RAG System
- ✅ WhatsApp Parser (14,667 messages)
- ✅ Document Chunker (1,274 chunks)
- ✅ Embedding Service (sentence-transformers)
- ✅ Vector Store (ChromaDB with data)
- ✅ Retrieval Engine (semantic search)
- ✅ Context Augmenter (prompt formatting)
- ✅ RAG Service (orchestration)
- ✅ FastAPI endpoints with RAG toggle

### Data Included
- ✅ Vector database: `data/chroma_db/` (~208KB)
- ✅ WhatsApp export: `data/whatsapp_export.txt` (16,362 lines)
- ✅ Embeddings for all 1,274 chunks

## 🔧 Deployment Steps

### Step 1: Commit Changes

```bash
cd farm-ai-assistant

# Add all RAG files
git add .

# Commit
git commit -m "feat: Add RAG system with WhatsApp history integration

- Implemented WhatsApp parser for 3 years of chat history
- Created document chunker (1,274 conversation chunks)
- Integrated sentence-transformers for embeddings
- Set up ChromaDB vector store with persistent data
- Built retrieval engine with semantic search
- Added context augmenter for LLM prompts
- Created RAG service orchestrating all components
- Updated FastAPI with use_rag toggle parameter
- Included vector database in deployment
- Added Render deployment configuration"

# Push to GitHub
git push origin feature/actual-deliverydate
```

### Step 2: Merge to Main (if needed)

```bash
# Switch to main
git checkout main

# Merge feature branch
git merge feature/actual-deliverydate

# Push to main
git push origin main
```

### Step 3: Deploy to Render

1. Go to https://dashboard.render.com/
2. Click "New +" → "Blueprint"
3. Connect GitHub repository
4. Select `farm-ai-assistant` repo
5. Render detects `render.yaml`
6. Add environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: `your-api-key-here`
7. Click "Apply"

### Step 4: Monitor Deployment

Watch the logs for:
- ✅ Dependencies installing
- ✅ Sentence-transformers downloading (~90MB)
- ✅ FastAPI starting
- ✅ Service becomes live

Expected deployment time: 5-10 minutes

### Step 5: Test Deployment

```bash
# Replace with your actual Render URL
RENDER_URL="https://farm-ai-assistant-rag.onrender.com"

# Test health
curl $RENDER_URL/health

# Test without RAG
curl -X POST $RENDER_URL/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I take care of the pigs?",
    "farm_data": {},
    "use_rag": false
  }'

# Test with RAG
curl -X POST $RENDER_URL/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I take care of the pigs?",
    "farm_data": {},
    "use_rag": true
  }'
```

### Step 6: Update React Native App

Update `PigFarmNew/components/AIAssistant.js` line 29:

```javascript
const AI_API_URL = 'https://your-actual-render-url.onrender.com';
```

Then commit and push the React app:

```bash
cd PigFarmNew
git add components/AIAssistant.js
git commit -m "feat: Connect to RAG-enhanced API on Render"
git push
```

## ⚠️ Important Considerations

### Free Tier Limitations

**Render Free Tier**:
- ✅ Includes your vector database in deployment
- ✅ Works perfectly while service is running
- ⚠️ Service sleeps after 15 min inactivity (30-60s cold start)
- ⚠️ **No persistent disk** - vector DB resets on service restart

**Solutions**:
1. **Upgrade to Starter ($7/month)** - Persistent disk included
2. **Rebuild on startup** - Auto-rebuild vector store if empty
3. **External vector DB** - Use Pinecone/Weaviate/Qdrant

### Recommended: Upgrade to Starter Plan

For production use with RAG, the Starter plan is recommended:
- Persistent disk storage
- No cold starts
- Better performance
- Only $7/month

## 🧪 Testing Checklist

After deployment, test:

- [ ] Health endpoint works
- [ ] API docs accessible at `/docs`
- [ ] Ask endpoint without RAG works
- [ ] Ask endpoint with RAG works
- [ ] Sources are returned when RAG is used
- [ ] Retrieval time is reasonable (<5s)
- [ ] React Native app connects successfully
- [ ] RAG toggle works in mobile app
- [ ] Sources display correctly in mobile app

## 📊 Expected Performance

**First Request (Cold Start)**:
- Time: 30-60 seconds
- Reason: Service waking up + model loading

**Subsequent Requests**:
- Without RAG: 1-3 seconds
- With RAG: 2-5 seconds
- Retrieval: 1-3 seconds
- LLM: 1-2 seconds

## 🎯 Success Criteria

Deployment is successful when:
- ✅ Health endpoint returns 200
- ✅ RAG queries return relevant sources
- ✅ Mobile app can toggle RAG on/off
- ✅ Sources display in mobile app
- ✅ Answers are enhanced with WhatsApp history

## 🐛 Troubleshooting

### Build Fails
- Check requirements.txt syntax
- Verify Python version (3.11)
- Check Render build logs

### Service Crashes
- Verify OPENAI_API_KEY is set
- Check for missing dependencies
- Review application logs

### RAG Not Working
- Test without RAG first
- Check vector database was included
- Verify embedding model downloaded
- Check logs for errors

### Slow Performance
- Normal for first request (cold start)
- Consider upgrading to Starter plan
- Check OpenAI API rate limits

## 📝 Post-Deployment

After successful deployment:

1. Save your Render URL
2. Update React Native app
3. Test thoroughly on mobile
4. Monitor usage and costs
5. Consider upgrading to Starter plan
6. Set up monitoring/alerts

## 🎉 You're Ready!

Your RAG system with 3 years of WhatsApp history is ready to deploy!

Run the commands in Step 1 to begin.
