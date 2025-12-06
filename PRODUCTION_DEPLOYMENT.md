# 🚀 ProfileGPT Production Deployment Guide

## 🎯 Quick Deploy Summary

Your ProfileGPT is ready for production deployment with enhanced features:

### ✨ Enhanced Features Added:
- **Advanced Document Processing**: PDF, DOCX, TXT, MD, HTML, CSV support
- **Better AI Models**: Local sentence-transformers for reliability
- **Production Database**: PostgreSQL configuration
- **Enhanced RAG**: Improved chunking and retrieval
- **Robust Error Handling**: Fallback methods for document processing

## 🏗️ Deployment Architecture

```
User → Vercel (Frontend) → Railway (Backend + Database) → Document Storage
                            ↓
                        Enhanced AI Pipeline
                        - Local Embeddings
                        - Smart Chunking
                        - Multiple File Types
```

## 📋 Pre-Deployment Checklist

### Environment Variables Required:

#### Backend (.env.production):
```bash
# Database - Railway auto-provides this
DATABASE_URL=${DATABASE_URL}

# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=openai
USE_LOCAL_EMBEDDINGS=true
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# Production Settings
ENVIRONMENT=production
CHUNK_SIZE=1000
MAX_RETRIEVAL_CHUNKS=12
ALLOWED_ORIGINS=["https://your-frontend.vercel.app"]
```

#### Frontend:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## 🚀 Step-by-Step Deployment

### Option 1: Railway + Vercel (Recommended - Free/Low Cost)

#### Deploy Backend to Railway:

1. **Setup Railway Account**
   ```bash
   # Install Railway CLI
   curl -fsSL https://railway.app/install.sh | sh

   # Login
   railway login
   ```

2. **Deploy Backend**
   ```bash
   cd backend

   # Initialize Railway project
   railway init

   # Add PostgreSQL database
   railway add postgresql

   # Set environment variables in Railway dashboard:
   # - OPENAI_API_KEY (your API key)
   # - ENVIRONMENT=production
   # - USE_LOCAL_EMBEDDINGS=true

   # Deploy
   railway deploy
   ```

3. **Get Backend URL**
   ```bash
   railway domain
   # Example: https://profilegpt-backend-production.up.railway.app
   ```

#### Deploy Frontend to Vercel:

1. **Setup Vercel**
   ```bash
   npm install -g vercel
   vercel login
   ```

2. **Update Frontend Configuration**
   - Update `NEXT_PUBLIC_API_URL` in vercel.json with your Railway backend URL

3. **Deploy**
   ```bash
   cd frontend
   vercel --prod
   ```

### Option 2: Manual GitHub Integration

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Production deployment setup"
   git push origin main
   ```

2. **Connect Railway to GitHub**
   - Go to Railway dashboard
   - Connect your GitHub repository
   - Auto-deploy from main branch

3. **Connect Vercel to GitHub**
   - Go to Vercel dashboard
   - Import your GitHub repository
   - Set environment variables

## 🔧 Advanced Configuration

### Database Migration
```bash
# In production, your database will be empty initially
# Upload your personal content using the API:

# Upload resume
curl -X POST https://your-backend.railway.app/ingest \\
  -F "file=@your-resume.pdf" \\
  -F "source_type=resume" \\
  -F "title=Professional Resume"

# Upload cover letter
curl -X POST https://your-backend.railway.app/ingest \\
  -F "file=@cover-letter.docx" \\
  -F "source_type=cover_letter"
```

### API Key Configuration
```bash
# Get OpenAI API key from: https://platform.openai.com/api-keys
# Set in Railway environment variables:
OPENAI_API_KEY=sk-your-actual-key-here

# For free/local-only operation, leave as placeholder:
OPENAI_API_KEY=sk-demo-key-placeholder
```

### Enhanced Document Processing
The system now supports:
- **PDF**: Multi-method extraction with fallbacks
- **DOCX**: Tables and structured content
- **Markdown**: Converted to clean text
- **HTML**: Tag removal and text extraction
- **CSV**: Data summary and statistics
- **TXT**: Encoding detection

## 📊 Performance Monitoring

### Health Checks
- Backend: `GET /health`
- Frontend: Built-in Vercel monitoring

### Logs Access
```bash
# Railway logs
railway logs

# Vercel logs available in dashboard
```

### Performance Targets
- **API Response**: < 2 seconds for RAG queries
- **Document Processing**: < 30 seconds for large PDFs
- **Frontend Load**: < 3 seconds initial
- **Uptime**: > 99% (Railway SLA)

## 💰 Cost Estimation

### Free Tier Limits:
- **Railway**: $5 credit/month (enough for small usage)
- **Vercel**: Unlimited static deployments
- **OpenAI**: Pay per token (~$0.10-$1/day typical usage)

### Upgrade Thresholds:
- **High Traffic**: Railway Pro $20/month
- **Team Features**: Vercel Pro $20/month
- **Heavy AI Usage**: OpenAI pay-as-you-go

## 🔐 Security Configuration

### Environment Variables:
```bash
# Generate secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Set CORS properly
ALLOWED_ORIGINS=["https://your-domain.vercel.app"]

# Database security
DATABASE_URL=postgresql://user:password@host:port/db  # Railway managed
```

### HTTPS/SSL:
- ✅ Railway: Automatic HTTPS
- ✅ Vercel: Automatic HTTPS + CDN

## 🧪 Testing Production Deployment

### 1. Test API Endpoints:
```bash
# Health check
curl https://your-backend.railway.app/health

# Test Q&A
curl -X POST https://your-backend.railway.app/ask \\
  -H "Content-Type: application/json" \\
  -d '{"question": "What are your Python skills?"}'
```

### 2. Test Document Upload:
```bash
# Upload a test document
curl -X POST https://your-backend.railway.app/ingest \\
  -F "file=@test-resume.pdf" \\
  -F "source_type=resume"
```

### 3. Test Frontend:
- Visit your Vercel URL
- Try uploading documents through the UI
- Test chat interface
- Verify citations appear

## 🚨 Troubleshooting

### Common Issues:

1. **CORS Errors**
   - Verify ALLOWED_ORIGINS includes your frontend URL
   - Check Railway environment variables

2. **Document Processing Failures**
   - Check file format support
   - Verify file size limits (50MB max)
   - Check Railway logs for errors

3. **AI Response Issues**
   - Verify OPENAI_API_KEY is set correctly
   - Check if USE_LOCAL_EMBEDDINGS=true for free operation
   - Monitor token usage in OpenAI dashboard

4. **Database Connection**
   - Railway auto-configures DATABASE_URL
   - Check Railway service status
   - Verify database plan limits

### Debug Commands:
```bash
# Check Railway status
railway status

# View real-time logs
railway logs --follow

# Test database connection
railway connect postgresql
```

## 📈 Scaling & Optimization

### When to Scale:
- **>1000 queries/day**: Upgrade Railway plan
- **>100MB documents**: Add Redis caching
- **>10 concurrent users**: Increase Railway resources

### Performance Optimization:
```python
# Backend optimizations (already configured):
- Sentence transformer caching
- Database connection pooling
- Efficient chunking algorithms
- Smart document processing fallbacks
```

## 🎉 Success Checklist

- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] Database connected and working
- [ ] OpenAI API key configured
- [ ] Documents uploaded and indexed
- [ ] Chat interface responding
- [ ] Citations showing in responses
- [ ] Health checks passing

## 🔄 Continuous Deployment

### GitHub Actions (Optional):
```yaml
# .github/workflows/deploy.yml
name: Deploy ProfileGPT
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        uses: railway/github-action@v1
        with:
          token: ${{ secrets.RAILWAY_TOKEN }}
```

## 📞 Support & Maintenance

### Regular Tasks:
- Monitor API usage and costs
- Update documents via /ingest endpoint
- Check application logs weekly
- Update dependencies monthly

### Backup Strategy:
- Database: Railway auto-backup
- Documents: Export via API
- Code: GitHub repository

## 🎯 Next Steps After Deployment

1. **Share Your ProfileGPT:**
   - Add to LinkedIn profile
   - Include in job applications
   - Share with recruiters

2. **Customize Content:**
   - Upload your actual resume/CV
   - Add portfolio projects
   - Include work samples

3. **Monitor Performance:**
   - Track query patterns
   - Monitor response quality
   - Gather user feedback

---

## 🚀 Ready to Deploy?

Your ProfileGPT is enhanced and production-ready! Choose your deployment method:

- **Quick Start**: Use existing PythonAnywhere setup + Vercel
- **Scalable**: Deploy to Railway + Vercel
- **Self-Hosted**: Use Docker compose files

**Happy Deploying! 🎉**