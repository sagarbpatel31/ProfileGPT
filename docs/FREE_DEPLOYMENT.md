# 🆓 100% Free Deployment Guide

## Option 1: Netlify + PythonAnywhere (Recommended)

### Step 1: Deploy Frontend to Netlify

1. **Sign up at [Netlify.com](https://netlify.com)** (100% free forever)
2. **Connect GitHub** and select ProfileGPT repository
3. **Build settings:**
   ```
   Base directory: frontend
   Build command: npm run build
   Publish directory: frontend/.next
   ```
4. **Environment variables:**
   ```
   NEXT_PUBLIC_API_URL=https://yourusername.pythonanywhere.com
   ```
5. **Custom domain:** Add your .io domain in Site settings → Domain management

### Step 2: Deploy Backend to PythonAnywhere

1. **Sign up at [PythonAnywhere.com](https://pythonanywhere.com)** (Always free account)
2. **Upload your backend files** via Files tab
3. **Create web app:**
   - Go to Web tab → Add new web app
   - Choose Flask/WSGI
   - Python 3.10
4. **Configure WSGI file** (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):
   ```python
   import sys
   import os

   # Add your project directory to sys.path
   path = '/home/yourusername/ProfileGPT/backend'
   if path not in sys.path:
       sys.path.append(path)

   from main import app as application

   if __name__ == "__main__":
       application.run()
   ```
5. **Install dependencies:**
   ```bash
   pip3.10 install --user fastapi uvicorn
   ```

## Option 2: GitHub Pages + Render

### Step 1: GitHub Pages Frontend

1. **Enable GitHub Pages** in repository settings
2. **Create workflow** `.github/workflows/deploy.yml`:
   ```yaml
   name: Deploy to GitHub Pages

   on:
     push:
       branches: [ main ]

   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-node@v2
           with:
             node-version: '18'
         - run: cd frontend && npm install
         - run: cd frontend && npm run build
         - run: cd frontend && npm run export
         - uses: peaceiris/actions-gh-pages@v3
           with:
             github_token: ${{ secrets.GITHUB_TOKEN }}
             publish_dir: ./frontend/out
   ```

### Step 2: Render Backend

1. **Sign up at [Render.com](https://render.com)** (Free tier)
2. **Create Web Service:**
   - Repository: ProfileGPT
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Option 3: Vercel + Koyeb

### Step 1: Vercel Frontend (Same as before)

1. **Sign up at [Vercel.com](https://vercel.com)**
2. **Import ProfileGPT** repository
3. **Configure:**
   - Root directory: `frontend`
   - Framework: Next.js
   - Environment: `NEXT_PUBLIC_API_URL=https://your-app.koyeb.app`

### Step 2: Koyeb Backend

1. **Sign up at [Koyeb.com](https://koyeb.com)**
2. **Create service:**
   - Source: GitHub repository
   - Build: Dockerfile or Buildpack
   - Port: 8000
3. **$5.50 monthly credits** renew automatically

## Domain Configuration

### Free Subdomain Options:
- Netlify: `yourapp.netlify.app`
- PythonAnywhere: `yourusername.pythonanywhere.com`
- Render: `yourapp.onrender.com`
- Vercel: `yourapp.vercel.app`

### Custom .io Domain:
1. **Purchase domain** (~$35/year only cost)
2. **Point DNS to your free hosting:**
   ```
   CNAME  yourname.io      yourapp.netlify.app
   CNAME  api.yourname.io  yourusername.pythonanywhere.com
   ```

## Cost Breakdown

**Completely Free Option:**
- Frontend: $0 (Netlify/GitHub Pages/Vercel)
- Backend: $0 (PythonAnywhere/Render/Koyeb)
- **Total: $0/month forever**

**With Custom Domain:**
- Domain: ~$35/year
- Everything else: $0
- **Total: ~$3/month**

## Performance Expectations

**Free Tier Limitations:**
- PythonAnywhere: CPU seconds limited (fine for portfolio)
- Render: Sleeps after 15min inactivity
- Koyeb: Nano instances (0.1 vCPU, 128MB RAM)

**Perfect for:**
- Personal portfolios
- Demonstrating skills
- Low-traffic professional sites

## Recommended: Netlify + PythonAnywhere

**Why this combo:**
- ✅ Both services are free forever
- ✅ No credit card required
- ✅ Good performance for portfolio use
- ✅ Easy custom domain setup
- ✅ Reliable uptime

Choose the option that fits your needs best!