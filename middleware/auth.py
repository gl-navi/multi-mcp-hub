import json
import logging
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from scalekit import ScalekitClient
from scalekit.common.scalekit import TokenValidationOptions
from starlette.middleware.base import BaseHTTPMiddleware

from config.app_config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()

# Initialize ScaleKit client
scalekit_client = ScalekitClient(
    settings.SCALEKIT_ENVIRONMENT_URL,
    settings.SCALEKIT_CLIENT_ID,
    settings.SCALEKIT_CLIENT_SECRET
)

# Authentication middleware
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_body = await request.body()
        # Log full request details for debugging
        logger.info(f"[DEBUG] Request method: {request.method}")
        logger.info(f"[DEBUG] Request url: {request.url}")
        logger.info(f"[DEBUG] Request headers: {dict(request.headers)}")
        logger.info(f"[DEBUG] Request body: {request_body}")
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] Request url: {request.url}")
        print(f"[DEBUG] Request headers: {dict(request.headers)}")
        print(f"[DEBUG] Request body: {request_body}")
        # Allow unauthenticated access to /.well-known/*, /health, and /info endpoints
        allowed_paths = ["/.well-known/", "/health", "/info", "/docs"]
        if any(request.url.path.startswith(path) for path in allowed_paths):
            return await call_next(request)

        try:
            # Always initialize resource_metadata_url to the base only
            resource_metadata_url = getattr(settings, 'SCALEKIT_BASE_RESOURCE_METADATA_URL', '')

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

            token = auth_header.split(" ")[1]

            print("[DEBUG] request_body:", request_body)
            logger.info(f"request_body: {request_body}")

            # Parse JSON from bytes
            try:
                request_data = json.loads(request_body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                request_data = {}
           
            # Set audience and resource_metadata dynamically based on request path
            base_audience = getattr(settings, "SCALEKIT_BASE_AUDIENCE_NAME", "")
            if "/github/mcp" in str(request.url.path):
                audience = [base_audience.rstrip("/") + "/github/mcp"]
            elif "/aws/mcp" in str(request.url.path):
                audience = [base_audience.rstrip("/") + "/aws/mcp"]
            else:
                logger.info(f"[DEBUG] No such audience for path: {request.url.path}")
                audience = [base_audience]

            validation_options = TokenValidationOptions(
                issuer=settings.SCALEKIT_ENVIRONMENT_URL,
                audience=audience,
            )

            is_tool_call = request_data.get("method") == "tools/call"

            required_scopes = []

            if is_tool_call:
                pass  # No scopes required for tool calls for now

            try:
                scalekit_client.validate_access_token(token, options=validation_options)
            except Exception as e:
                raise HTTPException(status_code=401, detail="Token validation failed")

        except HTTPException as e:
            # Set the correct resource_metadata_url for the error response
            path = str(request.url.path)
            base_metadata = getattr(settings, 'SCALEKIT_BASE_RESOURCE_METADATA_URL', '')
            if "/github/mcp" in path:
                error_metadata_url = f"{base_metadata}github/mcp"
            elif "/aws/mcp" in path:
                error_metadata_url = f"{base_metadata}aws/mcp"
            else:
                error_metadata_url = base_metadata
            return JSONResponse(
                status_code=e.status_code,
                content={"error": "unauthorized" if e.status_code == 401 else "forbidden", "error_description": e.detail},
                headers={
                    "WWW-Authenticate": f'Bearer realm="OAuth", resource_metadata="{error_metadata_url}"'
                }
            )

        return await call_next(request)