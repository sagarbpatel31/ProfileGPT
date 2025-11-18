# ProfileGPT Setup Guide

✅ **Current Status**: Backend foundation is complete and tested!

Your ProfileGPT backend is now running with mock data. Here's how to complete the setup:

## 🎯 **What's Working Right Now**

✅ FastAPI backend with all endpoints
✅ Mock RAG responses with citations
✅ Skills lookup system
✅ CORS configured for frontend integration
✅ Production-ready code structure

**Test your API**: Visit http://localhost:8000/docs

## 🚀 **Next Steps to Complete Setup**

### Step 1: Create Supabase Project (5 minutes)

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for database to initialize (2-3 minutes)
3. Go to **Settings → API** and copy:
   - Project URL
   - Anon public key
   - Service role key (keep secret!)

### Step 2: Configure Database (2 minutes)

1. In Supabase, go to **SQL Editor**
2. Paste and run the contents of `backend/setup_database.sql`
3. Verify tables were created in **Table Editor**

### Step 3: Update Environment Variables

Edit `backend/.env` with your actual values:

```bash
# From your Supabase project
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# From OpenAI (get from platform.openai.com)
OPENAI_API_KEY=sk-your_openai_api_key_here
```

### Step 4: Switch to Production Backend

```bash
cd backend
python3 main.py  # Full RAG implementation
```

## 🧪 **Testing Your Setup**

Run the verification script:
```bash
python3 test_setup.py
```

## 📁 **Project Structure**

```
ProfileGPT/
├── backend/
│   ├── main_simple.py     ← Currently running (mock data)
│   ├── main.py            ← Full RAG implementation
│   ├── setup_database.sql ← Run this in Supabase
│   ├── .env              ← Your credentials go here
│   └── app/
│       ├── services/     ← RAG engine, embeddings, Supabase
│       ├── models/       ← Database schemas
│       └── core/         ← Configuration
├── frontend/             ← Next.js (your friend will use this)
├── CLAUDE.md            ← AI assistant guidance
└── README.md            ← Complete documentation
```

## 🔧 **Available Endpoints (Currently Mock)**

- `GET /health` - Health check
- `POST /ask` - Chat with profile
- `GET /skills?name=Python` - Check specific skills
- `GET /skills/list` - List all skills
- `POST /ingest` - Document upload (will be real after Supabase setup)

## 🎨 **Frontend Integration**

Your friend can connect to the API at `http://localhost:8000` with these endpoints. The response format is production-ready:

```typescript
// Chat response format
interface ChatResponse {
  answer: string;
  citations: Array<{
    index: number;
    title: string;
    section: string;
    chunk_id: string;
  }>;
  sources: Array<{
    chunk_id: string;
    title: string;
    section: string;
    text_preview: string;
  }>;
  latency_ms: number;
  mode: string;
}
```

## 🚢 **Deployment Options**

### Option A: Railway (Recommended)
```bash
# After Supabase setup
railway login
railway link
railway up
```

### Option B: Vercel (API Routes)
```bash
vercel login
vercel --prod
```

### Option C: Docker
```bash
docker build -t profilegpt-api .
docker run -p 8000:8000 profilegpt-api
```

## 🔒 **Security Setup**

1. **API Keys**: Never commit real keys to Git
2. **CORS**: Update allowed origins in production
3. **Rate Limiting**: Add Redis for production
4. **Authentication**: Add tenant API key validation

## 📊 **Monitoring (Optional)**

1. Sign up for [Langfuse](https://langfuse.com) for LLM tracing
2. Add keys to `.env`:
   ```bash
   LANGFUSE_SECRET_KEY=your_secret_key
   LANGFUSE_PUBLIC_KEY=your_public_key
   ```

## 🎉 **What Happens After Supabase Setup**

1. **Real vector search** instead of mock responses
2. **Document ingestion** - upload PDFs, resumes, etc.
3. **Skills extraction** from your actual documents
4. **Persistent storage** of conversations
5. **Multi-tenant support** for hosting multiple profiles

## 🆘 **Troubleshooting**

**Can't access localhost:8000?**
- Check if server is running: `ps aux | grep uvicorn`
- Try a different port: `uvicorn main_simple:app --port 8001`

**Import errors?**
- Install dependencies: `pip install -r requirements-core.txt`
- Try: `pip install supabase openai`

**Database connection fails?**
- Double-check your Supabase URL and keys
- Make sure you ran `setup_database.sql`
- Check Supabase project status

## 📞 **Ready for Production?**

Once Supabase is configured, you'll have:
- ✅ RAG-powered Q&A with citations
- ✅ Document ingestion pipeline
- ✅ Skills matrix with evidence
- ✅ Multi-tenant architecture
- ✅ Production deployment configs

**Time to complete**: ~15 minutes total

**Current server**: http://localhost:8000 (mock data)
**After setup**: Full RAG system with your documents!