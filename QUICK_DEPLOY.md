# 🚀 ProfileGPT - Quick Production Deployment

## **Method 1: Direct Web Deployment (No CLI Required)**

### **Step 1: Deploy Backend to Railway**
1. **Go to:** https://railway.app
2. **Sign up/Login** with GitHub
3. **Click "Deploy from GitHub repo"**
4. **Select this repository** and choose `/backend` folder
5. **Add PostgreSQL database:**
   - Click "Add Service" → PostgreSQL
   - Railway auto-configures DATABASE_URL

6. **Set Environment Variables:**
   ```
   ENVIRONMENT=production
   USE_LOCAL_EMBEDDINGS=true
   EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
   CHUNK_SIZE=1000
   MAX_RETRIEVAL_CHUNKS=12
   ENABLE_RERANKING=true
   LOG_LEVEL=INFO
   ```

### **Step 2: Deploy Frontend to Vercel**
1. **Go to:** https://vercel.com
2. **Sign up/Login** with GitHub
3. **Click "Add New Project"**
4. **Import this repository**
5. **Set Framework Preset:** Next.js
6. **Set Root Directory:** `frontend`
7. **Add Environment Variable:**
   ```
   NEXT_PUBLIC_API_URL=https://[your-railway-app].railway.app
   ```

### **Step 3: Update CORS (Important!)**
After frontend deploys, update Railway backend environment:
```
ALLOWED_ORIGINS=["https://[your-vercel-app].vercel.app","http://localhost:3000"]
```

---

## **Method 2: CLI Deployment (If you have CLIs)**

### **Install CLIs:**
```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Install Vercel CLI
npm install -g vercel
```

### **Deploy Backend:**
```bash
cd backend
railway login
railway init profilegpt-backend
railway add postgresql
railway deploy
```

### **Deploy Frontend:**
```bash
cd frontend
vercel login
vercel --prod
```

---

## **Method 3: Docker Deployment (Self-Hosting)**

### **Prerequisites:**
- Docker and Docker Compose installed
- Domain name (optional)

### **Deploy:**
```bash
# Use the production docker setup
docker-compose -f docker-compose.prod.yml up -d

# Your app will be available at:
# http://localhost (frontend)
# http://localhost:8000 (backend API)
```

---

## **🎯 Expected Results**

After deployment, you'll have:

✅ **Live URLs:**
- **Frontend:** `https://[project-name].vercel.app`
- **Backend:** `https://[project-name].railway.app`
- **API Docs:** `https://[backend-url]/docs`

✅ **Features Working:**
- Document upload and processing
- AI chat with citations
- Intelligent skill discovery
- Web research enhancement
- Adaptive learning from conversations

✅ **Production Ready:**
- Auto-scaling infrastructure
- SSL certificates
- Database with backups
- Health monitoring
- 99.9% uptime SLA

---

## **🧪 Testing Your Deployment**

### **1. Test Backend Health:**
Visit: `https://[your-backend].railway.app/health`
Should return: `{"status": "healthy"}`

### **2. Test API Documentation:**
Visit: `https://[your-backend].railway.app/docs`
Should show interactive API documentation

### **3. Test Frontend:**
Visit: `https://[your-frontend].vercel.app`
Should show ProfileGPT interface

### **4. Test Full Flow:**
1. Upload a document via the interface
2. Ask questions in the chat
3. Verify responses include citations
4. Check that new skills are learned

---

## **📊 What Happens Next**

### **Immediate Benefits:**
- Your ProfileGPT is **LIVE 24/7**
- Recruiters can chat with your AI profile anytime
- System learns and improves from each interaction
- All conversations are grounded in your actual documents

### **Scaling:**
- **Railway Free Tier:** $5 credit/month (sufficient for personal use)
- **Vercel Free Tier:** Unlimited deployments
- **Upgrade when needed:** Both platforms scale seamlessly

### **Maintenance:**
- **Auto-deploys:** Push to GitHub = automatic deployment
- **Monitoring:** Built-in dashboards for both platforms
- **Backups:** Automatic database backups
- **Updates:** Easy environment variable updates

---

## **🔧 Configuration Files Ready**

All deployment configurations are prepared:
- ✅ `Dockerfile` - Production container
- ✅ `railway.json` - Railway deployment config
- ✅ `vercel.json` - Vercel deployment config
- ✅ `.env.production` - Production environment variables
- ✅ `requirements-deploy.txt` - Simplified dependencies

---

## **💡 Pro Tips**

1. **Custom Domain:** Add your own domain in Railway/Vercel dashboards
2. **Analytics:** Enable Vercel Analytics for usage insights
3. **Monitoring:** Add Langfuse for AI conversation tracking
4. **Scaling:** Both platforms auto-scale based on traffic
5. **Cost:** Stay within free tiers for personal use

---

## **🎉 You're Ready to Deploy!**

Choose your preferred method above and your ProfileGPT will be live in minutes!

**Need help?**
- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- Check the logs in the platform dashboards