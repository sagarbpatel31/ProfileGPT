#!/bin/bash
set -e

echo "=== STARTUP SCRIPT ==="
echo "PORT environment variable: ${PORT}"
echo "All environment variables:"
printenv | sort

# Default port to 8000 if not set
ACTUAL_PORT=${PORT:-8000}
echo "Starting uvicorn on port: ${ACTUAL_PORT}"

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port "${ACTUAL_PORT}" --log-level info --access-log