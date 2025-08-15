authorization_codes = {}
tokens = {}


# MCP Authorization Reference Implementation
# Implements https://modelcontextprotocol.io/specification/draft/basic/authorization
# Endpoints and responses follow the spec as closely as possible.
from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
import os

# [Spec 2.3] Resource Endpoint (protected)
from fastapi import HTTPException, Header
from typing import Optional as OptionalType

from database import get_db, AuthCode, AccessToken, Client

# Configuration - use environment variables for deployment flexibility
LOCAL_BASE_URL = "http://127.0.0.1:8000"
REMOTE_BASE_URL = os.getenv("REMOTE_BASE_URL", LOCAL_BASE_URL)  # Use local as default
BASE_URL = REMOTE_BASE_URL if os.getenv("ENVIRONMENT") == "production" else LOCAL_BASE_URL

CALLBACK_URL = os.getenv("CALLBACK_URL", "http://localhost:3000/callback")

app = FastAPI(title="MCP Auth Reference Server")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "MCP Authorization Server is running"}

# [Spec §2.3.1] Resource Server Metadata - MCP servers MUST implement this
@app.get("/.well-known/oauth-protected-resource")
def resource_server_metadata():
    return {
        "resource": BASE_URL,
        "authorization_servers": [BASE_URL]
    }

# [Spec §2.3.2] Authorization Server Metadata - Required for client discovery
@app.get("/.well-known/oauth-authorization-server")
def authorization_server_metadata():
    return {
        "issuer": BASE_URL,
        "authorization_endpoint": f"{BASE_URL}/authorize",
        "token_endpoint": f"{BASE_URL}/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],  # PKCE support
        "scopes_supported": ["read", "write"],
        "subject_types_supported": ["public"]
    }


# [Spec 2.1] Authorization Endpoint with PKCE support
# GET /authorize?response_type=code&client_id=...&redirect_uri=...&state=...&code_challenge=...&code_challenge_method=...

from fastapi import Form
from starlette.requests import Request as StarletteRequest

@app.api_route("/authorize", methods=["GET", "POST"])
async def authorize(request: StarletteRequest,
    response_type: str = None,
    client_id: str = None,
    redirect_uri: str = None,
    state: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
    resource: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Only 'code' is supported as per spec
    if response_type != "code":
        return RedirectResponse(f"{redirect_uri}?error=unsupported_response_type" + (f"&state={state}" if state else ""), status_code=302)

    # Check if client exists
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        return RedirectResponse(f"{redirect_uri}?error=invalid_client" + (f"&state={state}" if state else ""), status_code=302)

    if request.method == "GET":
        # Show consent screen
        return templates.TemplateResponse("consent.html", {
            "request": request,
            "client_name": client.client_name,
            "resource": resource,
            "response_type": response_type,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method
        })
    else:
        form = await request.form()
        action = form.get("action")
        if action == "deny":
            # User denied consent
            redirect_url = f"{redirect_uri}?error=access_denied"
            if state:
                redirect_url += f"&state={state}"
            return RedirectResponse(redirect_url, status_code=302)

        # User approved consent
        # Validate PKCE parameters if provided
        if code_challenge:
            if not code_challenge_method:
                code_challenge_method = "plain"  # Default to plain if not specified
            if code_challenge_method not in ["S256", "plain"]:
                return RedirectResponse(f"{redirect_uri}?error=invalid_request&error_description=invalid_code_challenge_method" + (f"&state={state}" if state else ""), status_code=302)
            if code_challenge_method == "S256" and (len(code_challenge) < 43 or len(code_challenge) > 128):
                return RedirectResponse(f"{redirect_uri}?error=invalid_request&error_description=invalid_code_challenge" + (f"&state={state}" if state else ""), status_code=302)

        code = secrets.token_urlsafe(16)
        auth_code = AuthCode(
            code=code,
            client_id=client_id,
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            resource=resource
        )
        db.add(auth_code)
        db.commit()

        redirect_url = f"{redirect_uri}?code={code}"
        if state:
            redirect_url += f"&state={state}"
        return RedirectResponse(redirect_url, status_code=302)


# [Spec 2.2] Token Endpoint with PKCE support
# POST /token (application/x-www-form-urlencoded)
@app.post("/token")
def token(
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    client_id: str = Form(...),
    code_verifier: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Only 'authorization_code' is supported
    if grant_type != "authorization_code":
        return JSONResponse(status_code=400, content={"error": "unsupported_grant_type"})
    
    # Find and validate the auth code
    auth_code = db.query(AuthCode).filter(
        AuthCode.code == code,
        AuthCode.used == False,
        AuthCode.expires_at > datetime.utcnow()
    ).first()
    
    if not auth_code:
        return JSONResponse(status_code=400, content={"error": "invalid_grant"})
    
    if auth_code.redirect_uri != redirect_uri or auth_code.client_id != client_id:
        return JSONResponse(status_code=400, content={"error": "invalid_request"})
    
    # PKCE validation if code_challenge was provided during authorization
    if auth_code.code_challenge:
        if not code_verifier:
            return JSONResponse(status_code=400, content={"error": "invalid_request", "error_description": "code_verifier required"})
        
        # Validate code_verifier against code_challenge
        if not validate_pkce(code_verifier, auth_code.code_challenge, auth_code.code_challenge_method):
            return JSONResponse(status_code=400, content={"error": "invalid_grant", "error_description": "code_verifier validation failed"})
    
    # Mark code as used
    auth_code.used = True
    
    # Create access token
    access_token_value = secrets.token_urlsafe(32)
    access_token = AccessToken(token=access_token_value, client_id=client_id, resource=auth_code.resource)
    db.add(access_token)
    db.commit()
    
    # [Spec §2.2.2] Return access_token and token_type
    # Optionally include resource in token response if present
    response = {"access_token": access_token_value, "token_type": "bearer"}
    if auth_code.resource:
        response["resource"] = auth_code.resource
    return response


def validate_pkce(code_verifier: str, code_challenge: str, code_challenge_method: str) -> bool:
    """Validate PKCE code_verifier against code_challenge"""
    import hashlib
    import base64
    
    if code_challenge_method == "plain":
        return code_verifier == code_challenge
    elif code_challenge_method == "S256":
        # Create SHA256 hash of code_verifier
        verifier_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        # Base64 URL-safe encode without padding
        verifier_challenge = base64.urlsafe_b64encode(verifier_hash).rstrip(b'=').decode('utf-8')
        return verifier_challenge == code_challenge
    else:
        return False


# [Spec 2.3] Resource Endpoint (protected)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_current_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    access_token = db.query(AccessToken).filter(
        AccessToken.token == token,
        AccessToken.expires_at > datetime.utcnow()
    ).first()
    if not access_token:
        # MCP spec requires WWW-Authenticate header with resource server metadata URL
        raise HTTPException(
            status_code=401, 
            detail="invalid_token",
            headers={"WWW-Authenticate": 'Bearer realm="mcp", resource_server_metadata_url="http://127.0.0.1:8000/.well-known/oauth-protected-resource"'}
        )
    return {"client_id": access_token.client_id}

@app.get("/resource")
def protected_resource(authorization: OptionalType[str] = Header(None), db: Session = Depends(get_db)):
    # Check if Authorization header is present
    if not authorization:
        # No token provided - return 401 with WWW-Authenticate header pointing to metadata
        raise HTTPException(
            status_code=401,
            detail="Authorization required",
            headers={"WWW-Authenticate": f'Bearer realm="mcp", resource_server_metadata_url="{BASE_URL}/.well-known/oauth-protected-resource"'}
        )
    
    # Extract token from "Bearer TOKEN" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format",
            headers={"WWW-Authenticate": 'Bearer realm="mcp"'}
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    # Validate token
    access_token = db.query(AccessToken).filter(
        AccessToken.token == token,
        AccessToken.expires_at > datetime.utcnow()
    ).first()
    
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": 'Bearer realm="mcp"'}
        )
    
    return {"message": "You have accessed a protected resource!", "client_id": access_token.client_id}


# [Step 7] Dynamic Client Registration Endpoint
# POST /register (application/json)
@app.post("/register")
def register_client(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Dynamic client registration endpoint (RFC 7591)
    Allows clients to register themselves with the authorization server
    """
    # Extract client information from request
    client_name = request.get("client_name", f"Client-{secrets.token_hex(4)}")
    redirect_uris = request.get("redirect_uris", [])
    grant_types = request.get("grant_types", ["authorization_code"])
    response_types = request.get("response_types", ["code"])
    scope = request.get("scope", "read write")
    
    # Validate required fields
    if not redirect_uris:
        return JSONResponse(
            status_code=400, 
            content={
                "error": "invalid_redirect_uri",
                "error_description": "At least one redirect_uri is required"
            }
        )
    
    # Validate grant types
    supported_grant_types = ["authorization_code"]
    for grant_type in grant_types:
        if grant_type not in supported_grant_types:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_client_metadata",
                    "error_description": f"Unsupported grant_type: {grant_type}"
                }
            )
    
    # Generate client credentials
    client_id = f"client_{secrets.token_urlsafe(16)}"
    client_secret = secrets.token_urlsafe(32)
    
    # Create client in database
    new_client = Client(
        client_id=client_id,
        client_secret=client_secret,
        client_name=client_name,
        redirect_uri=redirect_uris[0]  # Store the first redirect URI
    )
    
    try:
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "error": "server_error",
                "error_description": "Failed to register client in DB"
            }
        )
    
    # Return client registration response (RFC 7591)
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "client_name": client_name,
        "client_id_issued_at": int(datetime.utcnow().timestamp()),
        "redirect_uris": redirect_uris,
        "grant_types": grant_types,
        "response_types": response_types,
        "scope": scope,
        "token_endpoint_auth_method": "client_secret_post"
    }


# Helper function to validate Bearer token
def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Validate Bearer token and return client info"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": f'Bearer resource_metadata="{BASE_URL}/.well-known/oauth-protected-resource"'}
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    # Validate token
    access_token = db.query(AccessToken).filter(
        AccessToken.token == token,
        AccessToken.expires_at > datetime.utcnow()
    ).first()
    
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": f'Bearer resource_metadata="{BASE_URL}/.well-known/oauth-protected-resource"'}
        )
    
    return access_token.client_id


# MCP Tool Endpoints - Step 10: Access protected resources with token

@app.get("/simple/mcp/info")
def get_mcp_info(client_id: str = Depends(get_current_user)):
    """Get MCP server information - requires authentication"""
    import requests
    try:
        # Forward request to simple MCP server
        response = requests.get("http://127.0.0.1:8001/info")
        if response.status_code == 200:
            data = response.json()
            data["authenticated_client"] = client_id
            return data
        else:
            raise HTTPException(status_code=response.status_code, detail="MCP server error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="MCP server unavailable")


@app.post("/simple/mcp/tools/call")
def call_mcp_tool(
    request: dict,
    client_id: str = Depends(get_current_user)
):
    """Call an MCP tool - requires authentication"""
    import requests
    try:
        # Add client info to the request
        request["client_id"] = client_id
        
        # Forward request to simple MCP server
        response = requests.post(
            "http://127.0.0.1:8001/mcp/tools/call",
            json=request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="MCP tool error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="MCP server unavailable")


@app.get("/simple/mcp/tools/list")
def list_mcp_tools(client_id: str = Depends(get_current_user)):
    """List available MCP tools - requires authentication"""
    import requests
    try:
        # Forward request to simple MCP server
        response = requests.get("http://127.0.0.1:8001/mcp/tools/list")
        if response.status_code == 200:
            data = response.json()
            data["authenticated_client"] = client_id
            return data
        else:
            raise HTTPException(status_code=response.status_code, detail="MCP server error")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="MCP server unavailable")


# Test endpoint to trigger authorization flow
@app.get("/simple/mcp/test")
def test_mcp_access():
    """Test endpoint that returns 401 to trigger authorization flow"""
    raise HTTPException(
        status_code=401,
        detail="Authentication required",
        headers={"WWW-Authenticate": f'Bearer resource_metadata="{BASE_URL}/.well-known/oauth-protected-resource"'}
    )
