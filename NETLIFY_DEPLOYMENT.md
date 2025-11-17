# 🚀 Netlify + PythonAnywhere Deployment Guide

## Step 1: Deploy Frontend to Netlify (100% Free Forever)

### 1.1 Push Code to GitHub

```bash
# If you haven't already, push your code to GitHub
git add .
git commit -m "Ready for Netlify deployment"
git remote add origin https://github.com/yourusername/ProfileGPT.git
git push -u origin main
```

### 1.2 Deploy to Netlify

1. **Sign up at [netlify.com](https://netlify.com)**
2. **Click "Add new site" → "Import an existing project"**
3. **Connect to GitHub** and select your ProfileGPT repository
4. **Configure build settings:**
   ```
   Base directory: frontend
   Build command: npm run build && npm run export
   Publish directory: frontend/out
   ```
5. **Click "Deploy site"**

### 1.3 Configure Environment Variables

In your Netlify dashboard:
1. Go to **Site settings → Environment variables**
2. Add:
   ```
   NEXT_PUBLIC_API_URL = https://yourusername.pythonanywhere.com
   ```
   (Replace `yourusername` with your actual PythonAnywhere username)

### 1.4 Set Custom Domain (Optional)

1. **Buy your .io domain** from Namecheap, GoDaddy, etc.
2. In Netlify dashboard: **Domain settings → Add custom domain**
3. **Update DNS records** at your domain provider:
   ```
   CNAME  yourname.io     your-site-name.netlify.app
   CNAME  www.yourname.io your-site-name.netlify.app
   ```

## Step 2: Deploy Backend to PythonAnywhere (Always Free)

### 2.1 Sign Up for PythonAnywhere

1. **Go to [pythonanywhere.com](https://pythonanywhere.com)**
2. **Sign up for a free "Beginner" account**
3. **No credit card required**

### 2.2 Upload Backend Files

1. **Open the "Files" tab** in PythonAnywhere dashboard
2. **Create a new folder**: `/home/yourusername/ProfileGPT`
3. **Upload your backend files:**
   - `main.py`
   - `database.py`
   - `rag_engine.py`
   - `requirements.txt`
   - `wsgi.py`

### 2.3 Install Dependencies

1. **Open a Bash console** in PythonAnywhere
2. **Run:**
   ```bash
   cd ProfileGPT/backend
   pip3.10 install --user fastapi uvicorn PyPDF2 beautifulsoup4 requests python-docx numpy pandas pydantic python-multipart
   ```

### 2.4 Create Web App

1. **Go to "Web" tab** in PythonAnywhere
2. **Click "Add a new web app"**
3. **Choose:**
   - Manual configuration
   - Python 3.10
4. **Configure WSGI file** (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):
   ```python
   import sys
   import os

   # Add your project directory to the Python path
   path = '/home/yourusername/ProfileGPT/backend'
   if path not in sys.path:
       sys.path.append(path)

   # Import your FastAPI app
   from main import app as application

   if __name__ == "__main__":
       application.run()
   ```

### 2.5 Configure Static Files (if needed)

In the Web tab, under "Static files":
- URL: `/static/`
- Directory: `/home/yourusername/ProfileGPT/backend/static/`

### 2.6 Reload Web App

1. **Click "Reload" button** in Web tab
2. **Your API will be available at:** `https://yourusername.pythonanywhere.com`

## Step 3: Update Environment Variables

### 3.1 Update Netlify Environment

1. **Go to Netlify dashboard → Site settings → Environment variables**
2. **Update:**
   ```
   NEXT_PUBLIC_API_URL = https://yourusername.pythonanywhere.com
   ```
3. **Trigger a new deploy** (Site overview → Trigger deploy → Deploy site)

## Step 4: Test Your Deployment

### 4.1 Test Backend
Visit: `https://yourusername.pythonanywhere.com/docs`
- Should show FastAPI documentation

### 4.2 Test Frontend
Visit: `https://your-site-name.netlify.app`
- Should load ProfileGPT interface
- Try asking a question to test API connection

### 4.3 Test Personalized Chat
Visit: `https://your-site-name.netlify.app/personalized`
- Should load the enhanced chat interface

## Final URLs

After successful deployment:
- **Frontend**: `https://your-site-name.netlify.app` or `https://yourname.io`
- **Backend API**: `https://yourusername.pythonanywhere.com`
- **API Docs**: `https://yourusername.pythonanywhere.com/docs`
- **Personalized Chat**: `https://your-site-name.netlify.app/personalized`

## Cost Breakdown

- **Netlify**: $0/month forever
- **PythonAnywhere**: $0/month forever
- **Custom .io domain**: ~$35/year (optional)
- **Total**: $0-3/month

## Troubleshooting

### Common Issues:

1. **Build fails on Netlify:**
   - Check Node.js version (should be 18+)
   - Verify build command: `npm run build && npm run export`

2. **API connection fails:**
   - Verify environment variable: `NEXT_PUBLIC_API_URL`
   - Check PythonAnywhere web app is running
   - Test backend directly: `https://yourusername.pythonanywhere.com/docs`

3. **CORS errors:**
   - Backend already has CORS configured for all origins
   - Should work out of the box

4. **PythonAnywhere 500 errors:**
   - Check error logs in PythonAnywhere dashboard
   - Verify all dependencies are installed
   - Check WSGI file configuration

## Performance Notes

**Free Tier Limitations:**
- PythonAnywhere: CPU seconds limited (sufficient for portfolio use)
- Netlify: 100GB bandwidth/month (more than enough)

**Expected Performance:**
- Frontend: Instant loading (static files)
- Backend: 1-3 second response times
- Perfect for portfolio and demonstration use

## Success! 🎉

Your ProfileGPT is now live and accessible worldwide! Share your custom domain with recruiters and collaborators.