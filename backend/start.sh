#!/bin/bash
set -e

echo "=== ProfileGPT ENHANCED STARTUP $(date) ==="
echo "🚀 VERSION: Enhanced v2.0"
echo "PORT environment variable: ${PORT}"
echo "📁 Working directory: $(pwd)"
echo "📄 Main file exists: $(test -f main.py && echo 'YES' || echo 'NO')"
echo "📦 Python packages:"
pip list | grep -E "(fastapi|uvicorn|openai)" || echo "Packages not found"

# Default port to 8000 if not set
ACTUAL_PORT=${PORT:-8000}
echo "🌐 Starting uvicorn on port: ${ACTUAL_PORT}"

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port "${ACTUAL_PORT}" --log-level info --access-log