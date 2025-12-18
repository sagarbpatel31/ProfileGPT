#!/usr/bin/env python3
"""
Unit tests for ProfileGPT backend functionality
"""

import pytest
import asyncio
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

# Import our main app and functions
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import (
    app, extract_text_from_pdf, extract_text_from_docx,
    chunk_text, find_relevant_chunks, documents_store,
    chunks_store, tenant_store
)

client = TestClient(app)

class TestDocumentProcessing:
    """Test document processing functions"""

    def test_chunk_text_basic(self):
        """Test basic text chunking"""
        text = "This is a test document. " * 100  # Create long text
        chunks = chunk_text(text, chunk_size=50, overlap=10)

        assert len(chunks) > 1, "Should create multiple chunks"
        assert all(len(chunk) > 0 for chunk in chunks), "All chunks should have content"

    def test_chunk_text_short(self):
        """Test chunking with short text"""
        text = "Short text"
        chunks = chunk_text(text, chunk_size=800, overlap=200)

        assert len(chunks) == 1, "Short text should create only one chunk"
        assert chunks[0] == text, "Chunk content should match original"

    def test_chunk_text_empty(self):
        """Test chunking with empty text"""
        chunks = chunk_text("")
        assert chunks == [], "Empty text should return empty list"

    def test_find_relevant_chunks_basic(self):
        """Test basic chunk retrieval"""
        # Setup test data
        tenant_id = "test_tenant"
        chunks_store[tenant_id] = [
            {
                "id": "chunk1",
                "text": "I am a software engineer with Python experience",
                "title": "Resume"
            },
            {
                "id": "chunk2",
                "text": "I worked on machine learning projects",
                "title": "Resume"
            },
            {
                "id": "chunk3",
                "text": "My hobby is cooking and photography",
                "title": "Personal"
            }
        ]

        # Test relevant search
        results = find_relevant_chunks("software engineering", tenant_id)
        assert len(results) > 0, "Should find relevant chunks"
        assert results[0]["id"] == "chunk1", "Should rank most relevant chunk first"

        # Clean up
        del chunks_store[tenant_id]

    def test_find_relevant_chunks_no_results(self):
        """Test chunk retrieval with no matches"""
        tenant_id = "test_tenant_empty"
        chunks_store[tenant_id] = []

        results = find_relevant_chunks("nonexistent topic", tenant_id)
        assert results == [], "Should return empty list for no matches"

        # Clean up
        del chunks_store[tenant_id]

class TestAPIEndpoints:
    """Test FastAPI endpoints"""

    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Hello" in data

    def test_create_tenant_success(self):
        """Test successful tenant creation"""
        tenant_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpass123",
            "profession": "Software Engineer",
            "bio": "Test bio"
        }

        response = client.post("/tenant", json=tenant_data)
        assert response.status_code == 200

        data = response.json()
        assert "tenant_id" in data
        assert data["name"] == tenant_data["name"]
        assert data["email"] == tenant_data["email"]
        assert "api_key" in data

        # Clean up
        if data["tenant_id"] in tenant_store:
            del tenant_store[data["tenant_id"]]

    def test_create_tenant_missing_data(self):
        """Test tenant creation with missing required data"""
        tenant_data = {
            "name": "",  # Missing name
            "email": "test@example.com"
        }

        response = client.post("/tenant", json=tenant_data)
        assert response.status_code == 400

    def test_ask_question_no_tenant(self):
        """Test asking question with non-existent tenant"""
        qa_data = {
            "question": "What is your experience?",
            "tenant_id": "nonexistent_tenant"
        }

        # Should still work but with no context
        response = client.post("/ask", json=qa_data)
        assert response.status_code == 200

        data = response.json()
        assert "answer" in data
        assert "citations" in data

    @patch('main.client.chat.completions.create')
    def test_ask_question_with_context(self, mock_openai):
        """Test asking question with existing tenant and context"""

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "I am a software engineer with 5 years of experience in Python."
        mock_openai.return_value = mock_response

        # Setup test tenant and data
        tenant_id = "test_tenant_qa"
        tenant_store[tenant_id] = {
            "name": "Test User",
            "email": "test@example.com"
        }

        chunks_store[tenant_id] = [
            {
                "id": "chunk1",
                "text": "I have 5 years of experience in Python development",
                "title": "Resume",
                "source_type": "resume"
            }
        ]

        qa_data = {
            "question": "How many years of experience do you have?",
            "tenant_id": tenant_id,
            "mode": "short"
        }

        response = client.post("/ask", json=qa_data)
        assert response.status_code == 200

        data = response.json()
        assert "answer" in data
        assert len(data["citations"]) > 0
        assert data["mode"] == "short"

        # Clean up
        del tenant_store[tenant_id]
        del chunks_store[tenant_id]

    def test_get_documents_nonexistent_tenant(self):
        """Test getting documents for non-existent tenant"""
        response = client.get("/documents/nonexistent_tenant")
        assert response.status_code == 404

    def test_get_documents_empty(self):
        """Test getting documents for tenant with no documents"""
        tenant_id = "test_tenant_empty"
        tenant_store[tenant_id] = {"name": "Test User"}

        response = client.get(f"/documents/{tenant_id}")
        assert response.status_code == 200

        data = response.json()
        assert "documents" in data
        assert data["total_count"] == 0

        # Clean up
        del tenant_store[tenant_id]

class TestFileUpload:
    """Test file upload functionality"""

    def test_upload_text_file(self):
        """Test uploading a text file"""
        # Create test tenant
        tenant_data = {
            "name": "File Test User",
            "email": "filetest@example.com",
            "password": "testpass123"
        }

        tenant_response = client.post("/tenant", json=tenant_data)
        assert tenant_response.status_code == 200
        tenant_id = tenant_response.json()["tenant_id"]

        # Create test file
        test_content = "This is a test resume. I am a software engineer with Python experience. I have worked on web applications and APIs."

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name

        try:
            # Upload file
            with open(temp_file_path, 'rb') as file:
                files = {"file": ("test_resume.txt", file, "text/plain")}
                data = {
                    "source_type": "resume",
                    "tenant_id": tenant_id,
                    "title": "Test Resume"
                }

                response = client.post("/ingest", files=files, data=data)
                assert response.status_code == 200

                result = response.json()
                assert "document_id" in result
                assert "chunk_count" in result
                assert result["status"] == "completed"

        finally:
            # Clean up
            os.unlink(temp_file_path)
            if tenant_id in tenant_store:
                del tenant_store[tenant_id]
            if tenant_id in documents_store:
                del documents_store[tenant_id]
            if tenant_id in chunks_store:
                del chunks_store[tenant_id]

    def test_upload_unsupported_file(self):
        """Test uploading unsupported file type"""
        # Create test tenant
        tenant_data = {
            "name": "File Test User 2",
            "email": "filetest2@example.com"
        }

        tenant_response = client.post("/tenant", json=tenant_data)
        tenant_id = tenant_response.json()["tenant_id"]

        # Create binary file that can't be decoded
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            f.write(b'\x00\x01\x02\x03\x04\x05')  # Binary data
            temp_file_path = f.name

        try:
            with open(temp_file_path, 'rb') as file:
                files = {"file": ("test_binary.bin", file, "application/octet-stream")}
                data = {
                    "source_type": "misc",
                    "tenant_id": tenant_id
                }

                response = client.post("/ingest", files=files, data=data)
                assert response.status_code == 400

        finally:
            # Clean up
            os.unlink(temp_file_path)
            if tenant_id in tenant_store:
                del tenant_store[tenant_id]

class TestDataValidation:
    """Test data validation and edge cases"""

    def test_ask_empty_question(self):
        """Test asking empty question"""
        qa_data = {
            "question": "",
            "tenant_id": "test_tenant"
        }

        response = client.post("/ask", json=qa_data)
        assert response.status_code == 400

    def test_ask_different_modes(self):
        """Test different response modes"""
        # Setup test data
        tenant_id = "test_modes_tenant"
        tenant_store[tenant_id] = {"name": "Test User"}
        chunks_store[tenant_id] = [
            {
                "id": "chunk1",
                "text": "I managed a team of 5 developers to build a web application",
                "title": "Experience",
                "source_type": "resume"
            }
        ]

        modes = ["short", "detailed", "star"]

        with patch('main.client.chat.completions.create') as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "I have team management experience."
            mock_openai.return_value = mock_response

            for mode in modes:
                qa_data = {
                    "question": "Do you have management experience?",
                    "tenant_id": tenant_id,
                    "mode": mode
                }

                response = client.post("/ask", json=qa_data)
                assert response.status_code == 200

                data = response.json()
                assert data["mode"] == mode

        # Clean up
        del tenant_store[tenant_id]
        del chunks_store[tenant_id]

def run_unit_tests():
    """Run all unit tests"""
    print("🔬 Running ProfileGPT Unit Tests")
    print("=" * 40)

    # Test document processing
    doc_tests = TestDocumentProcessing()
    print("Testing document processing...")

    try:
        doc_tests.test_chunk_text_basic()
        print("✅ Text chunking - basic")
    except Exception as e:
        print(f"❌ Text chunking - basic: {e}")

    try:
        doc_tests.test_chunk_text_short()
        print("✅ Text chunking - short text")
    except Exception as e:
        print(f"❌ Text chunking - short text: {e}")

    try:
        doc_tests.test_chunk_text_empty()
        print("✅ Text chunking - empty text")
    except Exception as e:
        print(f"❌ Text chunking - empty text: {e}")

    try:
        doc_tests.test_find_relevant_chunks_basic()
        print("✅ Chunk retrieval - basic")
    except Exception as e:
        print(f"❌ Chunk retrieval - basic: {e}")

    # Test API endpoints
    api_tests = TestAPIEndpoints()
    print("\nTesting API endpoints...")

    try:
        api_tests.test_health_check()
        print("✅ Health check")
    except Exception as e:
        print(f"❌ Health check: {e}")

    try:
        api_tests.test_root_endpoint()
        print("✅ Root endpoint")
    except Exception as e:
        print(f"❌ Root endpoint: {e}")

    try:
        api_tests.test_create_tenant_success()
        print("✅ Create tenant - success")
    except Exception as e:
        print(f"❌ Create tenant - success: {e}")

    try:
        api_tests.test_create_tenant_missing_data()
        print("✅ Create tenant - validation")
    except Exception as e:
        print(f"❌ Create tenant - validation: {e}")

    # Test file upload
    file_tests = TestFileUpload()
    print("\nTesting file upload...")

    try:
        file_tests.test_upload_text_file()
        print("✅ Upload text file")
    except Exception as e:
        print(f"❌ Upload text file: {e}")

    print("\n🏁 Unit tests completed!")

if __name__ == "__main__":
    run_unit_tests()