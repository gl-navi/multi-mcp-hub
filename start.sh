#!/bin/bash
set -e

echo "Starting GL MCP Hub..."

# Check environment
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in production mode with Gunicorn..."
    exec gunicorn --config gunicorn.conf.py app:app
else
    echo "Running in development mode with Uvicorn..."
    exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --reload
fi
