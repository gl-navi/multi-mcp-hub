#!/bin/bash
# This script sets the PORT environment variable based on ENVIRONMENT.
# For production, PORT=8000. For development, PORT=10000.
set -e

echo "Starting GL MCP Hub..."

# Check environment
if [ "$ENVIRONMENT" = "production" ]; then
    export PORT=8000
    echo "Running in production mode with Gunicorn..."
    echo "🚀 Starting GL MCP Hub on 0.0.0.0:8000"
    echo "📝 Environment: ${ENVIRONMENT}"
    echo "🐛 Debug mode: ${DEBUG}"
    echo "🔄 Reload: false"
    echo "🏥 Health check: http://0.0.0.0:8000/health"
    exec gunicorn --config gunicorn.conf.py app:app
else
    export PORT=10000
    echo "Running in development mode with Uvicorn..."
    echo "🚀 Starting GL MCP Hub on 0.0.0.0:10000"
    echo "📝 Environment: ${ENVIRONMENT}"
    echo "🐛 Debug mode: ${DEBUG}"
    echo "🔄 Reload: true"
    echo "🏥 Health check: http://0.0.0.0:10000/health"
    exec uvicorn app:app --host 0.0.0.0 --port 10000 --reload
fi
