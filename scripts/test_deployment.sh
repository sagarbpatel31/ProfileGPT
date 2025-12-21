#!/bin/bash

# ProfileGPT Deployment Test Script
echo "🧪 Testing ProfileGPT Deployment"
echo "================================"

BASE_URL="https://profile-gpt.vercel.app"

echo ""
echo "1. Testing API health..."
curl -s "$BASE_URL/api" | jq '.'

echo ""
echo "2. Testing API health endpoint..."
curl -s "$BASE_URL/api/health" | jq '.'

echo ""
echo "3. Testing ask endpoint (should work without documents)..."
curl -s -X POST "$BASE_URL/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are your Python skills?"}' | jq '.answer'

echo ""
echo "4. Testing document ingestion endpoint..."
curl -s -X POST "$BASE_URL/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Resume",
    "content": "I am Sagar Patel, a software engineer with experience in Python, JavaScript, and machine learning. I have worked on autonomous drones, IoT systems, and AI research projects.",
    "source_type": "resume"
  }' | jq '.'

echo ""
echo "5. Testing ask endpoint with uploaded document..."
sleep 2  # Give time for processing
curl -s -X POST "$BASE_URL/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me about your experience with Python"}' | jq '.answer'

echo ""
echo "6. Testing document retrieval..."
curl -s "$BASE_URL/api/documents" | jq '.'

echo ""
echo "✅ Test complete! Check the responses above for any errors."
echo "📋 Expected behavior:"
echo "   - API health should return version info"
echo "   - Ask without documents should return general response"
echo "   - Document ingestion should return success"
echo "   - Ask with documents should return personalized response"