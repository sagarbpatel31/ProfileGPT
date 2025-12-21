"""
ProfileGPT Vercel Serverless API Handler
Integrated with Supabase for persistent storage
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import time
from urllib.parse import urlparse, parse_qs

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase_database import SupabaseDatabaseManager, Document, Chunk
    from rag_engine import RAGEngine
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback imports
    SupabaseDatabaseManager = None
    RAGEngine = None

import openai
from openai import OpenAI

class handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Initialize components
        self.openai_client = None
        self.db_manager = None
        self.rag_engine = None

        try:
            if os.getenv("OPENAI_API_KEY"):
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            if SupabaseDatabaseManager and os.getenv("NEXT_PUBLIC_SUPABASE_URL"):
                self.db_manager = SupabaseDatabaseManager()
                if RAGEngine:
                    self.rag_engine = RAGEngine(self.db_manager)
        except Exception as e:
            print(f"Initialization error: {e}")

        super().__init__(*args, **kwargs)

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path == "/api" or path == "/api/":
            self.handle_root()
        elif path == "/api/health":
            self.handle_health()
        elif path == "/api/documents":
            self.handle_get_documents(query_params)
        elif path.startswith("/api/sources/"):
            chunk_id = path.split("/")[-1]
            self.handle_get_source(chunk_id)
        elif path == "/api/insights":
            self.handle_get_insights(query_params)
        else:
            self.send_json_response({"error": "Not found"}, 404)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/api/ask":
            self.handle_ask()
        elif path == "/api/ingest":
            self.handle_ingest()
        elif path == "/api/tenant":
            self.handle_create_tenant()
        elif path == "/api/context":
            self.handle_get_context()
        else:
            self.send_json_response({"error": "Not found"}, 404)

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def handle_root(self):
        """Root endpoint with service info"""
        self.send_json_response({
            "service": "ProfileGPT",
            "version": "2.1-Supabase",
            "status": "running",
            "features": {
                "rag_engine": self.rag_engine is not None,
                "database": self.db_manager is not None,
                "openai": self.openai_client is not None,
                "supabase": os.getenv("NEXT_PUBLIC_SUPABASE_URL") is not None
            }
        })

    def handle_health(self):
        """Health check endpoint"""
        health_status = "healthy"
        components = {
            "database": "unknown",
            "llm": "unknown",
            "embeddings": "unknown"
        }

        try:
            if self.db_manager:
                # Test database connection
                stats = self.db_manager.get_tenant_stats(self.db_manager.default_tenant_id)
                components["database"] = "healthy"

            if self.openai_client:
                components["llm"] = "healthy"

            if self.rag_engine:
                components["embeddings"] = "healthy"

        except Exception as e:
            health_status = "degraded"
            components["error"] = str(e)

        self.send_json_response({
            "status": health_status,
            "components": components,
            "timestamp": time.time()
        })

    def handle_get_documents(self, query_params):
        """Get documents for a tenant"""
        if not self.db_manager:
            self.send_json_response({
                "error": "Database not configured. Please set up Supabase."
            }, 500)
            return

        tenant_id = query_params.get("tenant_id", [self.db_manager.default_tenant_id])[0]

        try:
            documents = self.db_manager.get_tenant_documents(tenant_id)
            doc_list = []

            for doc in documents:
                doc_list.append({
                    "id": doc.id,
                    "title": doc.title,
                    "source_type": doc.source_type,
                    "url": doc.url,
                    "status": doc.status,
                    "created_at": doc.created_at
                })

            self.send_json_response({
                "documents": doc_list,
                "count": len(doc_list),
                "tenant_id": tenant_id
            })

        except Exception as e:
            self.send_json_response({
                "error": f"Failed to retrieve documents: {str(e)}"
            }, 500)

    def handle_ask(self):
        """Main RAG query endpoint"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self.send_json_response({"error": "No data provided"}, 400)
                return

            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            question = data.get("question", "").strip()
            tenant_id = data.get("tenant_id", self.db_manager.default_tenant_id if self.db_manager else "demo-tenant")
            mode = data.get("mode", "detailed")

            if not question:
                self.send_json_response({"error": "Question is required"}, 400)
                return

            # Use RAG engine if available
            if self.rag_engine:
                try:
                    response = self.rag_engine.ask(question, tenant_id, mode)
                    self.send_json_response({
                        "answer": response.answer,
                        "citations": response.citations,
                        "sources": response.sources,
                        "latency_ms": response.latency_ms,
                        "mode": response.mode,
                        "tenant_id": tenant_id
                    })
                    return
                except Exception as e:
                    print(f"RAG engine error: {e}")
                    # Fall back to direct LLM

            # Fallback to direct LLM response
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a professional portfolio assistant. Provide helpful responses about professional skills and experience.

                            Keep responses concise and professional. Format using markdown where appropriate.

                            Note: For personalized responses based on uploaded documents, the full RAG system should be configured."""
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ],
                    max_tokens=500,
                    temperature=0.2
                )

                answer = response.choices[0].message.content
                self.send_json_response({
                    "answer": answer,
                    "citations": [],
                    "sources": [],
                    "mode": mode,
                    "note": "Direct LLM response - upload documents for RAG-powered answers"
                })
            else:
                self.send_json_response({
                    "answer": "I'm a professional portfolio assistant, but I need proper configuration (OpenAI API key and/or document upload) to provide responses.",
                    "citations": [],
                    "sources": [],
                    "mode": mode
                })

        except json.JSONDecodeError:
            self.send_json_response({"error": "Invalid JSON"}, 400)
        except Exception as e:
            self.send_json_response({"error": f"Server error: {str(e)}"}, 500)

    def handle_ingest(self):
        """Document ingestion endpoint"""
        if not self.rag_engine:
            self.send_json_response({
                "error": "RAG engine not configured. Please set up Supabase and dependencies."
            }, 500)
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            title = data.get("title", "Untitled Document")
            content = data.get("content", "")
            source_type = data.get("source_type", "misc")
            tenant_id = data.get("tenant_id", self.db_manager.default_tenant_id)
            url = data.get("url")

            if not content.strip():
                self.send_json_response({"error": "Content is required"}, 400)
                return

            # Ingest the document
            doc_id = self.rag_engine.ingest_document(
                tenant_id=tenant_id,
                source_type=source_type,
                title=title,
                content=content,
                url=url
            )

            # Update document status to completed
            self.db_manager.update_document_status(doc_id, "completed")

            self.send_json_response({
                "document_id": doc_id,
                "status": "completed",
                "message": "Document ingested successfully"
            })

        except json.JSONDecodeError:
            self.send_json_response({"error": "Invalid JSON"}, 400)
        except Exception as e:
            self.send_json_response({"error": f"Ingestion failed: {str(e)}"}, 500)

    def handle_create_tenant(self):
        """Create a new tenant"""
        if not self.db_manager:
            self.send_json_response({
                "error": "Database not configured"
            }, 500)
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            name = data.get("name", "New Tenant")
            tenant_id = self.db_manager.ensure_tenant()

            self.send_json_response({
                "tenant_id": tenant_id,
                "name": name,
                "message": "Tenant created successfully"
            })

        except Exception as e:
            self.send_json_response({"error": f"Failed to create tenant: {str(e)}"}, 500)

    def handle_get_context(self):
        """Get context for a question without generating answer"""
        if not self.rag_engine:
            self.send_json_response({
                "error": "RAG engine not configured"
            }, 500)
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            question = data.get("question", "").strip()
            tenant_id = data.get("tenant_id", self.db_manager.default_tenant_id)
            top_k = data.get("top_k", 5)

            if not question:
                self.send_json_response({"error": "Question is required"}, 400)
                return

            context = self.rag_engine.get_context(question, tenant_id, top_k)

            self.send_json_response({
                "context": context.context,
                "citations": context.citations,
                "sources": context.sources,
                "latency_ms": context.latency_ms
            })

        except Exception as e:
            self.send_json_response({"error": f"Context retrieval failed: {str(e)}"}, 500)

    def handle_get_source(self, chunk_id):
        """Get source content for a chunk"""
        if not self.db_manager:
            self.send_json_response({"error": "Database not configured"}, 500)
            return

        try:
            chunk = self.db_manager.get_chunk_by_id(chunk_id)
            if not chunk:
                self.send_json_response({"error": "Source not found"}, 404)
                return

            self.send_json_response({
                "chunk_id": chunk.id,
                "title": chunk.title,
                "section": chunk.section,
                "source_type": chunk.source_type,
                "text": chunk.text,
                "url": chunk.url,
                "tags": chunk.tags
            })

        except Exception as e:
            self.send_json_response({"error": f"Failed to get source: {str(e)}"}, 500)

    def handle_get_insights(self, query_params):
        """Get profile insights and topics"""
        if not self.rag_engine:
            self.send_json_response({
                "error": "RAG engine not configured"
            }, 500)
            return

        tenant_id = query_params.get("tenant_id", [self.db_manager.default_tenant_id])[0]

        try:
            insights = self.rag_engine.generate_profile_insights(tenant_id)
            self.send_json_response(insights)

        except Exception as e:
            self.send_json_response({
                "error": f"Failed to generate insights: {str(e)}"
            }, 500)