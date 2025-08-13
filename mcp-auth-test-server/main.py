authorization_codes = {}
tokens = {}


# MCP Authorization Reference Implementation
# Implements https://modelcontextprotocol.io/specification/draft/basic/authorization
# Endpoints and responses follow the spec as closely as possible.
from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import secrets

from database import get_db, AuthCode, AccessToken, Client

app = FastAPI(title="MCP Auth Reference Server")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "MCP Authorization Server is running"}

# Pre-register a test client for demo purposes
def create_test_client():
    db = next(get_db())
    existing = db.query(Client).filter(Client.client_id == "test_client").first()
    if not existing:
        test_client = Client(
            client_id="test_client",
            client_name="Test MCP Client", 
            redirect_uris='["http://localhost:3000/callback"]'
        )
        db.add(test_client)
        db.commit()
    db.close()

create_test_client()


# [Spec §2.1] Authorization Endpoint
# GET /authorize?response_type=code&client_id=...&redirect_uri=...&state=...
@app.get("/authorize")
def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Only 'code' is supported as per spec
    if response_type != "code":
        return RedirectResponse(f"{redirect_uri}?error=unsupported_response_type" + (f"&state={state}" if state else ""), status_code=302)
    
    # Check if client exists
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        return RedirectResponse(f"{redirect_uri}?error=invalid_client" + (f"&state={state}" if state else ""), status_code=302)
    
    # In a real app, authenticate user and get consent here
    code = secrets.token_urlsafe(16)
    auth_code = AuthCode(code=code, client_id=client_id, redirect_uri=redirect_uri)
    db.add(auth_code)
    db.commit()
    
    # [Spec §2.1.2] Redirect with code and state
    redirect_url = f"{redirect_uri}?code={code}"
    if state:
        redirect_url += f"&state={state}"
    return RedirectResponse(redirect_url, status_code=302)


# [Spec §2.2] Token Endpoint
# POST /token (application/x-www-form-urlencoded)
@app.post("/token")
def token(
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    client_id: str = Form(...),
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
    
    # Mark code as used
    auth_code.used = True
    
    # Create access token
    access_token_value = secrets.token_urlsafe(32)
    access_token = AccessToken(token=access_token_value, client_id=client_id)
    db.add(access_token)
    db.commit()
    
    # [Spec §2.2.2] Return access_token and token_type
    return {"access_token": access_token_value, "token_type": "bearer"}


# [Spec §2.3] Resource Endpoint (protected)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_current_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    access_token = db.query(AccessToken).filter(
        AccessToken.token == token,
        AccessToken.expires_at > datetime.utcnow()
    ).first()
    if not access_token:
        raise HTTPException(status_code=401, detail="invalid_token")
    return {"client_id": access_token.client_id}

@app.get("/resource")
def protected_resource(token_data: dict = Depends(get_current_token)):
    return {"message": "You have accessed a protected resource!", "client_id": token_data["client_id"]}
