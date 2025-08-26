#!/bin/bash
set -e

echo "Starting GL MCP Hub..."

# Check environment
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in production mode with Gunicorn..."
    echo "🚀 Starting GL MCP Hub on 0.0.0.0:${PORT:-8000}"
    echo "📝 Environment: ${ENVIRONMENT}"
    echo "🐛 Debug mode: ${DEBUG}"
    echo "🔄 Reload: false"
    echo "🏥 Health check: http://0.0.0.0:${PORT:-8000}/health"
    exec gunicorn --config gunicorn.conf.py app:app
else
    echo "Running in development mode with Uvicorn..."
    echo "🚀 Starting GL MCP Hub on 0.0.0.0:${PORT:-8000}"
    echo "📝 Environment: ${ENVIRONMENT}"
    echo "🐛 Debug mode: ${DEBUG}"
    echo "🔄 Reload: true"
    echo "🏥 Health check: http://0.0.0.0:${PORT:-8000}/health"
    exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --reload
fi
