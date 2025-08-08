"""Production server entry point."""
import argparse
import uvicorn

from app import app
from config import settings

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="GL MCP Hub Server")
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=settings.PORT,
        help=f"Port to run the server on (default: {settings.PORT})"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=settings.HOST,
        help=f"Host to bind to (default: {settings.HOST})"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.DEBUG,
        help="Enable auto-reload (default: based on DEBUG setting)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    print(f"🚀 Starting GL MCP Hub on {args.host}:{args.port}")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"🐛 Debug mode: {settings.DEBUG}")
    print(f"🔄 Reload: {args.reload}")
    print(f"🏥 Health check: http://{args.host}:{args.port}/health")
    
    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        access_log=not settings.is_production,
        log_level="info" if not settings.DEBUG else "debug"
    )
