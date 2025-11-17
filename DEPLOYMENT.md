# ProfileGPT Deployment Guide

## Quick Deployment Options

### Option 1: Railway + Vercel (Recommended for .io domains)

#### Step 1: Deploy Backend to Railway

1. **Sign up at [Railway.app](https://railway.app)**
2. **Connect your GitHub account** and import the ProfileGPT repository
3. **Configure deployment:**
   - Select the `backend` folder as root
   - Railway will auto-detect Python and use our `Procfile`
   - Set environment variables in Railway dashboard:
     ```
     PORT=8000
     PYTHONPATH=/app
     ```

4. **Deploy:** Railway will automatically build and deploy your backend
5. **Get the URL:** Railway provides a URL like `https://your-app.railway.app`

#### Step 2: Deploy Frontend to Vercel

1. **Sign up at [Vercel.com](https://vercel.com)**
2. **Import ProfileGPT repository**
3. **Configure deployment:**
   - Set root directory to `frontend`
   - Framework: Next.js (auto-detected)
   - Build command: `npm run build`
   - Output directory: `.next`

4. **Set environment variables in Vercel:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

5. **Deploy:** Vercel will build and deploy your frontend
6. **Get your URL:** Vercel provides URLs like `https://your-app.vercel.app`

#### Step 3: Custom Domain (.io)

**For Railway Backend:**
1. Go to Railway dashboard → Settings → Domains
2. Add your custom domain: `api.yourname.io`
3. Update DNS records as instructed

**For Vercel Frontend:**
1. Go to Vercel dashboard → Domains
2. Add your custom domain: `yourname.io` or `www.yourname.io`
3. Update DNS records as instructed

**Update environment variables:**
```
NEXT_PUBLIC_API_URL=https://api.yourname.io
```

### Option 2: Render + Vercel

#### Backend on Render
1. **Sign up at [Render.com](https://render.com)**
2. **Create Web Service:**
   - Repository: ProfileGPT
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables:**
   ```
   PYTHON_VERSION=3.11
   ```

#### Frontend same as Vercel above

### Option 3: Fly.io (Great for .io domains)

1. **Install Fly CLI:** `curl -L https://fly.io/install.sh | sh`
2. **Login:** `fly auth login`

**Backend:**
```bash
cd backend
fly launch --name profilegpt-api
fly deploy
```

**Frontend:**
```bash
cd frontend
fly launch --name profilegpt-app
fly deploy
```

## DNS Configuration for .io Domain

Once you have your deployment URLs, configure your domain:

1. **Purchase .io domain** from providers like Namecheap, GoDaddy, or Cloudflare
2. **Set DNS records:**
   ```
   A     yourname.io        →  Vercel IP (provided in dashboard)
   CNAME api.yourname.io    →  your-backend.railway.app
   CNAME www.yourname.io    →  your-frontend.vercel.app
   ```

## Free Tier Limits

- **Railway:** 500 hours/month free
- **Vercel:** Unlimited hobby projects
- **Render:** 750 hours/month free
- **Fly.io:** $5/month after free credits

## Environment Variables Setup

### Backend (Railway/Render/Fly.io)
```
PORT=8000
PYTHONPATH=/app
DATABASE_URL=sqlite:///./profilegpt.db
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

## Post-Deployment Testing

1. **Test backend:** Visit `https://your-backend-url/docs`
2. **Test frontend:** Visit your frontend URL
3. **Test API integration:** Try asking questions in the chat

## Custom Domain Examples

Once deployed, you can access:
- **Main site:** `https://yourname.io`
- **Personalized chat:** `https://yourname.io/personalized`
- **API docs:** `https://api.yourname.io/docs`

## Troubleshooting

### Common Issues:
1. **CORS errors:** Ensure backend allows your frontend domain
2. **Environment variables:** Double-check API URL configuration
3. **Build failures:** Verify all dependencies in requirements.txt

### Railway Specific:
- Check logs in Railway dashboard
- Ensure Python version compatibility

### Vercel Specific:
- Check build logs for any missing dependencies
- Verify environment variables are set correctly

## Cost Estimate

**Free tier:** $0/month (with limitations)
**Paid:** ~$10-20/month for:
- Domain registration (.io): ~$35/year
- Railway Pro: $5/month
- Vercel Pro: $20/month (if needed)

Choose the deployment option that best fits your needs!