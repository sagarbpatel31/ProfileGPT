#!/bin/bash
set -e

echo "🚀 Starting ProfileGPT Clean Backend $(date)"
echo "📁 Working directory: $(pwd)"
echo "🔑 OpenAI API Key: $(test -n "$OPENAI_API_KEY" && echo "SET" || echo "NOT SET")"

ACTUAL_PORT=${PORT:-8000}
echo "🌐 Starting on port: $ACTUAL_PORT"

uvicorn main:app --host 0.0.0.0 --port $ACTUAL_PORT --log-level info