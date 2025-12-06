# ProfileGPT - Technical Architecture & File Documentation

## 🔍 **Complete System Explanation**

ProfileGPT is a **Retrieval-Augmented Generation (RAG) system** specifically designed for professional portfolios. It transforms static resumes and portfolios into interactive AI chat experiences where recruiters can ask natural language questions and receive accurate, cited answers.

---

## 🏗️ **Core Architecture**

### **High-Level Data Flow**
```
Document Upload → Text Chunking → Vector Embeddings → Database Storage
                                                             ↓
User Question → Query Processing → Semantic Search → Context Retrieval → Answer Generation → Citations
```

### **Three-Layer Architecture**

1. **Presentation Layer** (Frontend)
   - Next.js React application
   - Professional chat interface
   - Responsive design with Tailwind CSS

2. **Business Logic Layer** (Backend API)
   - FastAPI Python application
   - RAG processing engine
   - Document ingestion pipeline

3. **Data Layer** (Database)
   - SQLite for development (free)
   - PostgreSQL for production (optional)
   - Vector storage for semantic search

---

## 📁 **File-by-File Technical Documentation**

### **Backend Files (`/backend/`)**

#### **`main.py`** - API Gateway & Server
**Purpose**: Central FastAPI application serving all HTTP endpoints

**Key Responsibilities**:
- HTTP request handling and routing
- CORS configuration for frontend communication
- Request validation using Pydantic models
- Error handling and response formatting

**Critical Endpoints**:
```python
@app.get("/")                    # Health check endpoint
@app.post("/ask")                # Main RAG chat endpoint
@app.post("/ingest")             # Document upload and processing
@app.get("/skills")              # Fast skill verification
@app.get("/sources/{chunk_id}")  # Source content retrieval
```

**Why FastAPI?**
- Automatic OpenAPI documentation generation
- Built-in request validation with Pydantic
- High performance async processing
- Excellent TypeScript integration

#### **`rag_engine.py`** - Core RAG Intelligence
**Purpose**: Implements the complete RAG pipeline for question answering

**Key Components**:

1. **Document Ingestion**:
```python
def ingest_document(text: str, source_type: str) -> str:
    # 1. Clean and preprocess text
    # 2. Split into 800-token chunks with 200 token overlap
    # 3. Generate embeddings for each chunk
    # 4. Store in database with metadata
    # 5. Extract skills and create evidence mappings
```

2. **Question Processing**:
```python
def ask(question: str, tenant_id: str) -> RAGResponse:
    # 1. Generate query embedding
    # 2. Semantic search for relevant chunks
    # 3. Rank results by relevance
    # 4. Create context from top chunks
    # 5. Generate answer with mock LLM
    # 6. Create citations from sources
```

3. **Skills Extraction**:
```python
def extract_skills(text: str) -> List[Skill]:
    # 1. Use NER and keyword extraction
    # 2. Map to skill taxonomy
    # 3. Create evidence links to text chunks
    # 4. Calculate confidence scores
```

**Why This Design?**
- **Chunking Strategy**: 800 tokens balances context vs. precision
- **Mock LLM**: Allows free operation, easily replaceable with real models
- **Vector Search**: Finds semantically similar content, not just keywords
- **Citations**: Every answer traceable to source documents

#### **`database.py`** - Data Management Layer
**Purpose**: SQLite database operations and schema management

**Database Schema**:
```sql
CREATE TABLE tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    api_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    tenant_id TEXT REFERENCES tenants(id),
    title TEXT NOT NULL,
    source_type TEXT,  -- 'resume', 'portfolio', 'cover_letter'
    file_path TEXT,
    content TEXT,
    metadata TEXT,     -- JSON metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id),
    tenant_id TEXT,
    text TEXT NOT NULL,
    embedding BLOB,    -- Serialized vector
    chunk_index INTEGER,
    metadata TEXT,     -- JSON: section, page, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skills (
    id TEXT PRIMARY KEY,
    tenant_id TEXT,
    skill_name TEXT NOT NULL,
    chunk_ids TEXT,    -- JSON array of evidence chunks
    confidence REAL,   -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Operations**:
- **Multi-tenant isolation**: All data segregated by tenant_id
- **Full-text search**: Fast text search across chunks
- **Vector similarity**: Semantic search using embeddings
- **Skills lookup**: Fast skill verification with evidence

**Why SQLite?**
- Zero configuration required
- Perfect for single-user portfolios
- Fast for read-heavy workloads
- Easy to backup (single file)
- Scales to terabytes if needed

#### **`profile_scrapers.py`** - Content Extraction
**Purpose**: Extract and normalize content from various sources

**Supported Formats**:
- **PDF**: Using PyPDF2 or pdfplumber
- **DOCX**: Using python-docx
- **HTML/URLs**: Using BeautifulSoup
- **Markdown**: Direct text processing
- **Plain Text**: As-is processing

**URL Processing**:
```python
def scrape_profile_from_url(url: str) -> Dict:
    # 1. Detect platform (LinkedIn, GitHub, etc.)
    # 2. Extract relevant content sections
    # 3. Clean HTML and format text
    # 4. Return structured content with metadata
```

### **Frontend Files (`/frontend/`)**

#### **`src/app/page.tsx`** - Main Chat Interface
**Purpose**: Primary user interface for interacting with ProfileGPT

**Key Features**:
- **Real-time Chat**: WebSocket-style interface for questions/answers
- **Citation Display**: Shows sources for every answer
- **Response Modes**: Short/Detailed/STAR format options
- **Professional Design**: Clean, recruiter-friendly interface

**React Components**:
```typescript
// Main chat component with state management
function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const askQuestion = async (question: string) => {
        // API call to backend /ask endpoint
        // Handle response and update UI
        // Display citations and sources
    };
}
```

**Why Next.js?**
- Server-side rendering for better SEO
- Automatic code splitting and optimization
- Excellent developer experience
- Built-in TypeScript support

#### **`src/app/layout.tsx`** - App Layout & Configuration
**Purpose**: Global app configuration and layout wrapper

**Responsibilities**:
- HTML document structure
- Global CSS imports (Tailwind)
- Font configuration (Geist)
- Metadata for SEO
- Global error boundaries

#### **`public/widget.js`** - Embeddable Chat Widget
**Purpose**: Standalone JavaScript widget for embedding on any website

**Features**:
- **Zero Dependencies**: Pure JavaScript, works anywhere
- **Customizable**: Themes, sizing, positioning
- **Lightweight**: ~10KB minified
- **Cross-Domain**: Communicates with API via CORS

**Usage**:
```html
<script src="https://your-domain.com/widget.js"
        data-tenant="your-tenant-id"
        data-theme="light"
        data-height="500px">
</script>
```

**Implementation**:
```javascript
(function() {
    // 1. Create iframe container
    // 2. Load chat interface in iframe
    // 3. Handle cross-frame communication
    // 4. Apply custom styling and positioning
    // 5. Connect to ProfileGPT API
})();
```

#### **Configuration Files**

**`next.config.js`** - Next.js Configuration
```javascript
const nextConfig = {
    output: 'export',        // Static site generation
    trailingSlash: true,     // Compatibility with static hosting
    images: {
        unoptimized: true    // No image optimization for static export
    },
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL
    }
};
```

**`tailwind.config.ts`** - Tailwind CSS Configuration
```typescript
module.exports = {
    content: ['./src/**/*.{js,ts,jsx,tsx}'],
    theme: {
        extend: {
            colors: {
                // Custom brand colors
            },
            typography: {
                // Custom typography styles for citations
            }
        }
    }
};
```

### **Deployment Configuration**

#### **`vercel.json`** - Vercel Deployment
```json
{
    "version": 2,
    "buildCommand": "npm run build",
    "installCommand": "npm install",
    "framework": "nextjs",
    "regions": ["iad1"],
    "env": {
        "NEXT_PUBLIC_API_URL": "https://sagarbpatel31.pythonanywhere.com"
    },
    "build": {
        "env": {
            "NEXT_PUBLIC_API_URL": "https://sagarbpatel31.pythonanywhere.com"
        }
    }
}
```

#### **`netlify.toml`** - Netlify Deployment (Alternative)
```toml
[build]
  base = "frontend"
  publish = "frontend/out"
  command = "npm ci && npm run build"

[build.environment]
  NODE_VERSION = "20.9.0"
  NPM_VERSION = "10"

[context.production.environment]
  NEXT_PUBLIC_API_URL = "https://sagarbpatel31.pythonanywhere.com"
```

---

## 🔄 **Data Flow Diagrams**

### **Document Ingestion Flow**
```
Upload PDF/DOCX → Extract Text → Clean Content → Split into Chunks (800 tokens)
                                                          ↓
Store in SQLite ← Generate Embeddings ← Create Metadata ← Process Skills
```

### **Question Processing Flow**
```
User Question → Generate Query Embedding → Search Vector Database
                                                    ↓
Create Answer ← Format with Citations ← Rank Results ← Retrieve Top Chunks
```

### **Skills Verification Flow**
```
Text Input → NER Processing → Skill Extraction → Evidence Mapping → Confidence Score
                                     ↓
Database Storage ← Create Synonyms ← Validate Against Taxonomy
```

---

## 🧪 **Testing Strategy**

### **Backend Testing**
```python
# Test RAG pipeline
def test_ask_endpoint():
    response = client.post("/ask", json={"question": "What are Python skills?"})
    assert response.status_code == 200
    assert "citations" in response.json()

# Test document ingestion
def test_document_upload():
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    response = client.post("/ingest", files=files)
    assert response.status_code == 200
```

### **Frontend Testing**
```typescript
// Test chat interface
describe('Chat Interface', () => {
    test('sends question and receives answer', async () => {
        render(<ChatInterface />);
        fireEvent.change(screen.getByPlaceholderText('Ask a question...'), {
            target: { value: 'What are your skills?' }
        });
        fireEvent.click(screen.getByText('Send'));
        await waitFor(() => {
            expect(screen.getByText(/Python/)).toBeInTheDocument();
        });
    });
});
```

---

## 🔒 **Security Implementation**

### **Backend Security**
```python
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Input Validation
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    tenant_id: Optional[str] = Field(default="demo", max_length=50)
```

### **Frontend Security**
```typescript
// API URL validation
const API_URL = process.env.NEXT_PUBLIC_API_URL;
if (!API_URL || !API_URL.startsWith('https://')) {
    throw new Error('Invalid API URL configuration');
}

// Input sanitization
const sanitizeInput = (input: string) => {
    return input.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
};
```

---

## 📈 **Performance Optimizations**

### **Database Optimizations**
```sql
-- Indexes for fast queries
CREATE INDEX idx_chunks_tenant_id ON chunks(tenant_id);
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_skills_tenant_skill ON skills(tenant_id, skill_name);

-- Full-text search index
CREATE VIRTUAL TABLE chunks_fts USING fts5(text, content='chunks', content_rowid='rowid');
```

### **Frontend Optimizations**
```typescript
// Code splitting for large components
const ChatWidget = dynamic(() => import('./ChatWidget'), {
    loading: () => <div>Loading chat...</div>,
    ssr: false
});

// Memoization for expensive operations
const MemoizedCitation = React.memo(({ citation }) => {
    return <div>{citation.source}</div>;
});
```

### **API Optimizations**
```python
# Response caching for common queries
@lru_cache(maxsize=100)
def get_skill_info(skill_name: str, tenant_id: str) -> SkillInfo:
    return database.get_skill(skill_name, tenant_id)

# Async processing for multiple operations
async def process_multiple_chunks(chunks: List[str]) -> List[Embedding]:
    tasks = [create_embedding(chunk) for chunk in chunks]
    return await asyncio.gather(*tasks)
```

---

## 🚀 **Scaling Considerations**

### **Current Architecture (Single User)**
- SQLite database (up to 1TB)
- Single server instance
- Local file storage
- Mock AI models

### **Medium Scale (100+ Users)**
- PostgreSQL with pgvector
- Redis caching layer
- S3 file storage
- Real AI API integration

### **Large Scale (1000+ Users)**
- Microservices architecture
- Vector database (Pinecone/Weaviate)
- CDN for static assets
- Load balancing
- Monitoring and observability

---

## 🎯 **Design Decisions & Rationale**

### **Why SQLite for Development?**
- ✅ Zero configuration
- ✅ Perfect for single-user portfolios
- ✅ Fast for read-heavy workloads
- ✅ Easy backup (single file)
- ✅ Scales surprisingly well

### **Why Mock AI Models?**
- ✅ Zero ongoing costs
- ✅ Predictable responses for testing
- ✅ No API rate limits
- ✅ Easy to replace with real models
- ✅ Demonstrates system capabilities
- 🔄 Set `OPENAI_API_KEY` (and optionally `LLM_PROVIDER=openai`) to switch to the OpenAI-backed responder, or set `LLM_PROVIDER=hf` to run a local HuggingFace model like `google/flan-t5-base` entirely for free.

### **Why FastAPI over Flask/Django?**
- ✅ Automatic API documentation
- ✅ Built-in request validation
- ✅ Excellent async performance
- ✅ TypeScript-friendly
- ✅ Modern Python features

### **Why Next.js over React SPA?**
- ✅ Server-side rendering for SEO
- ✅ Static site generation option
- ✅ Automatic code optimization
- ✅ Built-in TypeScript support
- ✅ Excellent developer experience

---

## 🔄 **Upgrade Path**

### **Phase 1: Real AI Integration**
```python
# Replace mock models with real ones
from openai import OpenAI
from sentence_transformers import SentenceTransformer

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### **Phase 2: Production Database**
```python
# Migrate to PostgreSQL
DATABASE_URL = "postgresql://user:pass@host:5432/profilegpt"
# Add pgvector extension for vector similarity
```

### **Phase 3: Advanced Features**
- Real-time chat with WebSockets
- Advanced analytics dashboard
- Multi-language support
- Custom AI model fine-tuning

This architecture provides a solid foundation that can scale from a personal portfolio to an enterprise-grade system while maintaining the core value proposition of intelligent, cited Q&A about professional backgrounds.
