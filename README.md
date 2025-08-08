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
