# ProfileGPT - Personalized AI Portfolio Assistant

[![Deploy](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)](https://profile-gpt.vercel.app)
[![Database](https://img.shields.io/badge/Database-Supabase-green?logo=supabase)](https://supabase.com)
[![AI](https://img.shields.io/badge/AI-OpenAI-blue?logo=openai)](https://openai.com)

**Live Demo**: [https://profile-gpt.vercel.app](https://profile-gpt.vercel.app)

ProfileGPT is a RAG-powered AI assistant that allows recruiters and collaborators to chat with your professional profile. Upload your resume, portfolio, and projects to get personalized, cited responses about your experience and skills.

## ✨ Features

- **🤖 AI-Powered Chat**: Ask questions about skills, experience, and projects
- **📄 Document Upload**: Resume, cover letters, portfolios, research papers
- **🔍 Hybrid Search**: Vector similarity + full-text search + reranking
- **📊 Citations**: All answers include source references and evidence
- **🏢 Multi-Tenant**: Each user gets their own workspace
- **⚡ Serverless**: Auto-scaling deployment on Vercel
- **🔒 Secure**: Row-level security and data isolation

## 🚀 Quick Start

### 1. Clone and Deploy

```bash
git clone https://github.com/sagarbpatel31/ProfileGPT.git
cd ProfileGPT
npx vercel deploy
```

### 2. Set Up Database

1. Create a [Supabase](https://supabase.com) project
2. Run the SQL script in `supabase_setup.sql` in your Supabase SQL editor
3. Get your project URL and service role key from Settings → API

### 3. Configure Environment Variables

```bash
npx vercel env add NEXT_PUBLIC_SUPABASE_URL
npx vercel env add SUPABASE_SERVICE_ROLE_KEY
npx vercel env add OPENAI_API_KEY
```

### 4. Deploy with Environment Variables

```bash
npx vercel --prod
```

## 🏗️ Architecture

```
User → Vercel CDN → Next.js Frontend → API Routes → Supabase
                                                   ↓
                              RAG Engine ← Vector DB + Full-text Search
                                  ↓
                             OpenAI LLM
```

### Tech Stack

- **Frontend**: Next.js 16 + TypeScript + Tailwind CSS
- **Backend**: Next.js API Routes + Python serverless functions
- **Database**: Supabase (PostgreSQL + pgvector)
- **AI**: OpenAI GPT-4o-mini
- **Deployment**: Vercel
- **Storage**: Supabase Storage

## 📁 Project Structure

```
ProfileGPT/
├── frontend/                 # Next.js application
│   ├── src/app/             # App router pages
│   ├── src/components/      # React components
│   └── public/              # Static assets
├── api/                     # Python serverless functions
│   ├── index.py            # Main API handler
│   ├── supabase_database.py# Database manager
│   └── rag_engine.py       # RAG implementation
├── lib/                     # Shared utilities
│   └── supabase.js         # Supabase client
├── supabase_setup.sql      # Database schema
└── vercel.json             # Deployment config
```

## 🔧 Development

### Prerequisites

- Node.js 20+
- Python 3.9+
- Supabase account
- OpenAI API key

### Local Setup

1. **Install dependencies**:
   ```bash
   cd frontend && npm install
   cd ../api && pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env.local
   # Fill in your API keys
   ```

3. **Start development servers**:
   ```bash
   # Frontend
   cd frontend && npm run dev

   # API (if testing locally)
   cd api && uvicorn main:app --reload
   ```

## 🧪 Testing

### Run Test Suite
```bash
./test_deployment.sh
```

### Manual Testing
```bash
# Test API health
curl https://profile-gpt.vercel.app/api

# Test Q&A functionality
curl -X POST https://profile-gpt.vercel.app/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are your Python skills?"}'
```

## 📊 Usage

### Basic Q&A (Works immediately)
- Ask about programming languages, technologies, best practices
- Get career advice and professional guidance
- Explain technical concepts

### Document-Powered Responses (After setup)
1. Upload resume/portfolio via the web interface
2. Ask personalized questions about your experience
3. Get cited responses with source references

### Example Questions
- "What programming languages do you know?"
- "Tell me about your machine learning experience"
- "What projects have you worked on with Python?"
- "Describe your experience with cloud technologies"

## 🔍 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api` | GET | Service status and version |
| `/api/ask` | POST | Ask questions (main chat endpoint) |
| `/api/ingest` | POST | Upload and process documents |
| `/api/documents` | GET | List uploaded documents |
| `/api/tenant` | POST | Create user workspace |

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role secret | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `LLM_PROVIDER` | LLM provider (openai/hf/auto) | No |
| `EMBEDDING_MODEL` | Embedding model name | No |

### Supabase Setup

The `supabase_setup.sql` file creates:
- **Tables**: tenants, documents, chunks, skills, query_logs
- **Indexes**: Vector search optimized indexes
- **Functions**: Hybrid search and similarity matching
- **Security**: Row-level security policies

## 🚨 Troubleshooting

### Common Issues

1. **"Database not configured"**: Missing Supabase environment variables
2. **"Upload error occurred"**: Check Supabase service role key
3. **Empty responses**: Verify OpenAI API key is valid
4. **Vector search fails**: Ensure pgvector extension is installed

### Debug Commands
```bash
# Check deployment logs
npx vercel logs profile-gpt.vercel.app

# Test environment variables
npx vercel env ls

# Check API status
curl https://profile-gpt.vercel.app/api
```

## 📈 Performance

- **Response Time**: ~800ms for API calls, ~3-5s for LLM responses
- **Scalability**: Serverless auto-scaling, handles concurrent users
- **Caching**: CDN caching for static content, API response caching
- **Database**: Optimized indexes for vector and text search

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit with conventional commits: `git commit -m "feat: add new feature"`
5. Push and create a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation**: Check this README and inline code comments
- **Issues**: [GitHub Issues](https://github.com/sagarbpatel31/ProfileGPT/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sagarbpatel31/ProfileGPT/discussions)

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Custom embedding models
- [ ] Integration with LinkedIn/GitHub APIs
- [ ] Real-time collaboration features
- [ ] Mobile app companion

---

**Built with ❤️ by [Sagar Patel](https://github.com/sagarbpatel31)**