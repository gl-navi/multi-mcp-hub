## Running in Production and Development

This project supports both production and development modes using the `start.sh` script. The mode is controlled by the `ENVIRONMENT` environment variable.

### Production Mode
```
export ENVIRONMENT=production
export PORT=8000
./start.sh
```
This will run the server with Gunicorn on port 8000.

### Development Mode
```
export ENVIRONMENT=development
export PORT=10000
./start.sh
```
This will run the server with Uvicorn (with auto-reload) on port 10000.

You can also set these variables in your `.env` file or pass them to Docker/Docker Compose as needed.

## Usage

Use the `start.sh` script to start the server. It will automatically select the correct server and port based on your environment settings.
# GL MCP Hub

This project is a Multi-Tenant MCP (Model Context Protocol) Hub designed to support OAuth2 authentication and authorization. The goal is to provide a unified, secure interface for multiple backend services and tenants, with extensible support for different resource providers.

Currently, the project includes two server integrations (GitHub and AWS MCP servers) and is focused on testing and implementing OAuth2 flows for secure, standards-based access control. The architecture is designed to be modular and scalable, making it easy to add new tenants or resource types in the future.

Development is ongoing, with an emphasis on technical clarity and practical, real-world use cases for multi-tenant environments.
# GL MCP Hub

A FastAPI-based MCP (Model Context Protocol) hub that integrates GitHub and AWS MCP servers.

## Features

- GitHub MCP server integration
- AWS MCP server integration  
- Health check endpoint
- Production-ready with Gunicorn
- Docker support

## Development

```bash
# Run development server
uv run server.py

# Run with custom port
uv run server.py --port 3000

# Run with reload
uv run server.py --port 3000 --reload
```

## Production

```bash
# Run with Gunicorn
uv run gunicorn --config gunicorn.conf.py app:app
```
