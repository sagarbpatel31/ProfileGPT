#!/usr/bin/env python3
"""
Test script for ProfileGPT clean backend
"""

import requests
import json
import time
import tempfile
import os

def test_clean_backend(base_url):
    """Test all endpoints of the clean backend"""

    print(f"🧪 Testing ProfileGPT Clean Backend: {base_url}")
    print("=" * 50)

    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root: {data.get('service')} v{data.get('version')}")
            print(f"   OpenAI: {data.get('openai_available')}")
        else:
            print(f"❌ Root: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root: {e}")
        return False

    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health: OK")
        else:
            print(f"❌ Health: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Health: {e}")

    # Test 3: Create tenant
    tenant_data = {
        "name": "Test User",
        "email": "test@clean.example.com",
        "profession": "Software Engineer",
        "bio": "Testing clean backend"
    }

    try:
        response = requests.post(f"{base_url}/tenant", json=tenant_data)
        if response.status_code == 200:
            tenant_info = response.json()
            tenant_id = tenant_info["tenant_id"]
            print(f"✅ Tenant: Created {tenant_id}")
        else:
            print(f"❌ Tenant: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tenant: {e}")
        return False

    # Test 4: Upload document
    test_resume = """
John Doe
Software Engineer
Email: john@example.com

EXPERIENCE
Senior Developer | TechCorp | 2020-Present
• Built scalable web applications using Python and React
• Led team of 5 developers on microservices project
• Improved system performance by 40%

SKILLS
• Python, JavaScript, React, FastAPI
• AWS, Docker, Kubernetes
• Team Leadership, Agile Development
    """

    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_resume)
            temp_file = f.name

        # Upload file
        with open(temp_file, 'rb') as file:
            files = {'file': ('test_resume.txt', file, 'text/plain')}
            data = {
                'source_type': 'resume',
                'tenant_id': tenant_id,
                'title': 'Test Resume'
            }

            response = requests.post(f"{base_url}/ingest", files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload: {result['filename']} → {result['chunk_count']} chunks")
            else:
                print(f"❌ Upload: HTTP {response.status_code} - {response.text}")

        # Clean up temp file
        os.unlink(temp_file)

    except Exception as e:
        print(f"❌ Upload: {e}")

    # Test 5: Get documents
    try:
        response = requests.get(f"{base_url}/documents/{tenant_id}")
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ Documents: Found {docs['total_count']} documents")
        else:
            print(f"❌ Documents: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Documents: {e}")

    # Test 6: Ask question
    question_data = {
        "question": "What programming languages do you know?",
        "tenant_id": tenant_id,
        "mode": "detailed"
    }

    try:
        response = requests.post(f"{base_url}/ask", json=question_data)
        if response.status_code == 200:
            result = response.json()
            answer = result["answer"]
            print(f"✅ Q&A: Got answer ({len(answer)} chars)")
            print(f"   Context: {result['context_used']} chunks")
            print(f"   Answer: {answer[:100]}...")
        else:
            print(f"❌ Q&A: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Q&A: {e}")

    print("\n🎉 Clean backend testing completed!")
    return True

if __name__ == "__main__":
    # Test with different URLs
    test_urls = [
        "http://localhost:8000",  # Local development
        "https://profilegpt-production.up.railway.app"  # Production
    ]

    for url in test_urls:
        try:
            print(f"\n📍 Testing: {url}")
            test_clean_backend(url)
            print()
        except Exception as e:
            print(f"❌ Failed to test {url}: {e}")