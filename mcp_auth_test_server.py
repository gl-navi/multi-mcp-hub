from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import secrets

app = FastAPI(title="MCP Auth Test Server")

authorization_codes = {}
tokens = {}

@app.get("/authorize")
def authorize(response_type: str, client_id: str, redirect_uri: str, state: Optional[str] = None):
    # Simulate user login and consent
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Unsupported response_type")
    code = secrets.token_urlsafe(16)
    authorization_codes[code] = {"client_id": client_id, "redirect_uri": redirect_uri}
    redirect_url = f"{redirect_uri}?code={code}"
    if state:
        redirect_url += f"&state={state}"
    return RedirectResponse(redirect_url)

@app.post("/token")
def token(grant_type: str = "authorization_code", code: str = None, redirect_uri: str = None, client_id: str = None):
    if grant_type != "authorization_code" or code not in authorization_codes:
        raise HTTPException(status_code=400, detail="Invalid grant or code")
    auth = authorization_codes.pop(code)
    if auth["redirect_uri"] != redirect_uri or auth["client_id"] != client_id:
        raise HTTPException(status_code=400, detail="Invalid redirect_uri or client_id")
    access_token = secrets.token_urlsafe(32)
    tokens[access_token] = {"client_id": client_id}
    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_current_token(token: str = Depends(oauth2_scheme)):
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    return tokens[token]

@app.get("/resource")
def protected_resource(token_data: dict = Depends(get_current_token)):
    return {"message": "You have accessed a protected resource!", "client_id": token_data["client_id"]}
