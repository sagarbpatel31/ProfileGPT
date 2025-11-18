# 🚀 ProfileGPT - Complete Setup & Usage Guide

## 🎉 **DEPLOYMENT STATUS: LIVE & READY**

Your ProfileGPT is now successfully deployed and ready to use!

### **Live URLs**
- **Frontend (Vercel)**: `https://personalgpt-projects.vercel.app` ✅ LIVE
- **Backend (PythonAnywhere)**: `https://sagarbpatel31.pythonanywhere.com` ✅ LIVE
- **API Health**: https://sagarbpatel31.pythonanywhere.com/ ✅ RESPONDING

### **Infrastructure Overview**
- **Frontend hosting**: Vercel (Next.js, CDN, HTTPS, auto-builds)
- **Backend hosting**: PythonAnywhere (FastAPI + SQLite) with optional upgrade to Supabase/Postgres (`backend/app` ready)
- **RAG pipeline**: Custom chunking + mock LLM/embeddings (swap in OpenAI or local sentence-transformers when needed)
- **Widget delivery**: `frontend/public/widget.js` served from Vercel

---

## 🔧 **IMMEDIATE NEXT STEPS**

### 1. **Test Your Live ProfileGPT**
Visit your Vercel URL and try these sample questions:
- "What are your Python skills?"
- "Tell me about your React experience"
- "What projects have you worked on?"
- "Do you have machine learning experience?"

### 2. **Replace Demo Data with Your Resume**

#### **Option A: Upload PDF/DOCX Resume**
```bash
curl -X POST https://sagarbpatel31.pythonanywhere.com/ingest \
  -F "file=@your-resume.pdf" \
  -F "source_type=resume" \
  -F "title=My Professional Resume"
```

#### **Option B: Add Text Content**
```bash
curl -X POST https://sagarbpatel31.pythonanywhere.com/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your resume content here...",
    "source_type": "resume",
    "title": "My Resume",
    "metadata": {"section": "experience"}
  }'
```

### 3. **Monitor Your ProfileGPT**

#### **Check Analytics**
- **Vercel**: Visit your Vercel dashboard → Analytics tab
- **PythonAnywhere**: Check "Tasks" tab for API request logs

#### **View Database Content**
```bash
# Connect to local development to see what's stored
cd backend
python3 -c "
import sqlite3
conn = sqlite3.connect('profilegpt.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM documents')
print('Documents:', cursor.fetchall())
cursor.execute('SELECT title, text[:100] FROM chunks LIMIT 5')
print('Sample chunks:', cursor.fetchall())
conn.close()
"
```

---

## 📊 **CUSTOMIZATION OPTIONS**

### **A. Update Skills & Experience**
Add specific technologies and experiences:
```bash
curl -X POST https://sagarbpatel31.pythonanywhere.com/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Expert in Python, Django, FastAPI, PostgreSQL, Docker, AWS, Machine Learning with TensorFlow and scikit-learn. 5+ years building scalable web applications.",
    "source_type": "skills",
    "title": "Technical Skills",
    "metadata": {"category": "programming"}
  }'
```

### **B. Add Project Descriptions**
```bash
curl -X POST https://sagarbpatel31.pythonanywhere.com/ingest \
  -F "file=@project-portfolio.pdf" \
  -F "source_type=portfolio" \
  -F "title=My Projects Portfolio"
```

### **C. Include Cover Letters**
```bash
curl -X POST https://sagarbpatel31.pythonanywhere.com/ingest \
  -F "file=@cover-letter.docx" \
  -F "source_type=cover_letter" \
  -F "title=Software Engineer Cover Letter"
```

---

## 🌐 **EMBEDDING YOUR PROFILEGPT**

### **Option 1: Direct Link**
Share your Vercel URL directly:
```
https://personalgpt-projects.vercel.app
```

### **Option 2: Embed as Widget**
Add this to any website:
```html
<!-- Add to your portfolio website -->
<div id="profilegpt-widget"></div>
<script src="https://personalgpt-projects.vercel.app/widget.js"
        data-tenant="your-name"
        data-theme="light"
        data-height="500px">
</script>
```

### **Option 3: Custom Domain**
In Vercel dashboard:
1. Go to Settings → Domains
2. Add your custom domain (e.g., `chat.yourname.com`)
3. Update DNS settings as instructed

---

## 📈 **SCALING & ENHANCEMENT**

### **Free Tier Limits**
- **Vercel**: 100GB bandwidth/month (very generous)
- **PythonAnywhere**: 100k requests/month (sufficient for personal use)
- **Storage**: Unlimited for text content

### **Upgrade Options When Needed**

#### **Enhanced AI Responses**
Replace mock responses with real AI:
```python
# In backend/rag_engine.py, replace mock_llm_call with:
import openai  # or use Groq, Together.ai for cheaper options

def real_llm_call(prompt, context):
    client = openai.OpenAI(api_key="your-api-key")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # $0.002 per 1k tokens
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content
```

#### **Better Search**
Add real embeddings:
```python
# Replace mock embeddings with sentence-transformers
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast & free

def create_embedding(text):
    return model.encode(text).tolist()
```

#### **Production Database**
Upgrade to PostgreSQL with pgvector:
```bash
# Supabase (free tier: 500MB, 2 concurrent connections)
pip install supabase psycopg2-binary pgvector
```

---

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

#### **"Network Error" in Frontend**
Check if backend is accessible:
```bash
curl https://sagarbpatel31.pythonanywhere.com/
# Should return: {"message": "ProfileGPT API is running", "status": "ok"}
```

#### **Empty or Wrong Responses**
Verify your data was uploaded:
```bash
curl https://sagarbpatel31.pythonanywhere.com/sources
```

#### **Vercel Build Failures**
Check build logs in Vercel dashboard and ensure:
- Root Directory is set to `frontend`
- Environment variable `NEXT_PUBLIC_API_URL` is set correctly

#### **PythonAnywhere API Errors**
Check error logs in PythonAnywhere → Tasks tab

---

## 💡 **PRO TIPS**

### **Content Strategy**
- **Be Specific**: Include exact technologies, frameworks, metrics
- **Use Keywords**: Add terms recruiters search for
- **Tell Stories**: Include project outcomes and challenges solved
- **Update Regularly**: Add new experiences and skills

### **SEO Optimization**
- **Custom Domain**: Use your name (e.g., `johnsmith.dev`)
- **Meta Tags**: Update in `frontend/src/app/page.tsx`
- **Structured Data**: Add JSON-LD markup for better search visibility

### **Performance**
- **Cache Responses**: Implement Redis for frequently asked questions
- **CDN**: Vercel automatically provides global CDN
- **Monitoring**: Set up uptime monitoring (UptimeRobot free tier)

---

## 🎯 **MARKETING YOUR PROFILEGPT**

### **Add to Professional Profiles**
- **LinkedIn**: Add Vercel URL to "Contact Info" → Website
- **GitHub**: Add to repository description and README
- **Resume**: Include as "Interactive Portfolio: personalgpt-projects.vercel.app"
- **Email Signature**: "Learn more: Chat with my AI → personalgpt-projects.vercel.app"

### **Social Media**
```
🤖 Just launched my AI-powered portfolio!
Recruiters can now chat with an AI version of me to learn about my experience.

Try asking about my Python skills: https://personalgpt-projects.vercel.app

#AI #Portfolio #TechJobs #Innovation
```

### **Job Applications**
```
P.S. Want to learn more about my experience? I've created an AI assistant that can answer questions about my background: https://personalgpt-projects.vercel.app

Try asking "What projects has [Your Name] worked on?" or "Tell me about their Python experience."
```

---

## 🚀 **SUCCESS METRICS TO TRACK**

### **Engagement**
- Daily/weekly visitors (Vercel Analytics)
- Questions asked (PythonAnywhere logs)
- Session duration
- Return visitors

### **Professional Impact**
- Job interview mentions
- LinkedIn profile views increase
- Recruiter inquiries
- Networking connections

### **Technical Performance**
- API response time (<500ms target)
- Uptime (>99.9% target)
- Error rate (<1% target)
- User satisfaction (add feedback widget)

---

## 🎉 **YOU'RE ALL SET!**

Your ProfileGPT is now:
- ✅ **Live and accessible** to anyone with the URL
- ✅ **Completely free** to run and maintain
- ✅ **Professional grade** with SSL, CDN, and global availability
- ✅ **Customizable** and expandable as your career grows

**Share your ProfileGPT with recruiters, add it to your LinkedIn, and watch it work for you 24/7!**

---

*💡 Need help? Create an issue in your GitHub repository or refer to the logs in Vercel/PythonAnywhere dashboards.*
