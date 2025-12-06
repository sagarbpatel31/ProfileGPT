# ProfileGPT Production Deployment Guide

## 🚀 Quick Deployment Steps

### Step 1: Railway Backend Deployment

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Deploy Backend:**
   ```bash
   cd backend
   railway init
   railway link [your-project-id]
   railway up
   ```

3. **Set Environment Variables:**
   ```bash
   # Copy from .env.production and set in Railway dashboard
   railway variables set ENVIRONMENT=production
   railway variables set LOG_LEVEL=INFO
   railway variables set USE_LOCAL_EMBEDDINGS=true
   railway variables set EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
   railway variables set CHUNK_SIZE=1000
   railway variables set MAX_RETRIEVAL_CHUNKS=12
   ```

### Step 2: Vercel Frontend Deployment

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   vercel login
   ```

2. **Deploy Frontend:**
   ```bash
   cd frontend
   vercel --prod
   ```

3. **Configure Environment:**
   ```bash
   # Set in Vercel dashboard or via CLI
   vercel env add NEXT_PUBLIC_API_URL production
   # Enter your Railway backend URL: https://[your-app].railway.app
   ```

### Step 3: Database Setup

**Option A: Railway Postgres (Recommended)**
```bash
railway add postgresql
# Auto-configures DATABASE_URL
```

**Option B: Supabase (Advanced)**
1. Create project at supabase.com
2. Enable pgvector extension
3. Set DATABASE_URL in Railway

### Step 4: Production Configuration

**Backend Environment Variables (Railway):**
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://[auto-generated]
USE_LOCAL_EMBEDDINGS=true
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
LOG_LEVEL=INFO
CHUNK_SIZE=1000
MAX_RETRIEVAL_CHUNKS=12
ENABLE_RERANKING=true
MAX_UPLOAD_SIZE=10485760
```

**Frontend Environment Variables (Vercel):**
```bash
NEXT_PUBLIC_API_URL=https://[your-railway-app].railway.app
NEXT_PUBLIC_APP_NAME=ProfileGPT
NEXT_PUBLIC_VERSION=1.0.0
```

## 🔧 Advanced Configuration

### Custom Domain Setup

**Railway (Backend):**
1. Go to Railway dashboard → Settings → Domains
2. Add custom domain: `api.yourdomain.com`
3. Configure CNAME: `[project-id].railway.app`

**Vercel (Frontend):**
1. Go to Vercel dashboard → Settings → Domains
2. Add custom domain: `yourdomain.com`
3. Configure DNS as instructed

### SSL & Security
- Both platforms provide automatic HTTPS
- Configure CORS in FastAPI for your frontend domain
- Set secure headers in Vercel

### Monitoring & Logs

**Railway:**
```bash
railway logs --follow
railway metrics
```

**Vercel:**
```bash
vercel logs
vercel analytics
```

## 📋 Pre-deployment Checklist

- [ ] Backend tests passing
- [ ] Frontend builds successfully
- [ ] Environment variables configured
- [ ] Database connections working
- [ ] CORS settings updated
- [ ] Domain DNS configured
- [ ] Health checks responding

## 🛠 Troubleshooting

**Common Issues:**

1. **Port Configuration:**
   - Railway: Uses $PORT environment variable
   - Ensure FastAPI binds to `0.0.0.0:$PORT`

2. **Database Connections:**
   - Check DATABASE_URL format
   - Verify network connectivity
   - Enable SSL for external databases

3. **CORS Errors:**
   - Update allowed origins in FastAPI
   - Add frontend URL to CORS settings

4. **Build Failures:**
   - Check requirements.txt for conflicts
   - Verify Node.js version compatibility

## 📊 Performance Optimization

**Backend:**
- Enable gzip compression
- Configure Redis caching (optional)
- Optimize embedding model size
- Use CDN for static files

**Frontend:**
- Enable Vercel Analytics
- Configure image optimization
- Implement lazy loading
- Use service worker for caching

## 🔄 Continuous Deployment

**Auto-deploy from Git:**

**Railway:**
```bash
# Connect GitHub repo in dashboard
railway connect
```

**Vercel:**
```bash
# Connect GitHub repo in dashboard
vercel git connect
```

Both platforms will auto-deploy on push to main branch.

## 🎯 Production URLs

After deployment:
- **Frontend**: `https://[project-name].vercel.app`
- **Backend**: `https://[project-name].railway.app`
- **Health Check**: `https://[backend-url]/health`
- **API Docs**: `https://[backend-url]/docs`

## 💡 Next Steps

1. Configure monitoring and alerting
2. Set up backup strategies
3. Implement rate limiting
4. Configure CDN for global performance
5. Set up CI/CD pipelines
6. Monitor performance metrics

---

Your ProfileGPT application will be live and continuously running! 🎉