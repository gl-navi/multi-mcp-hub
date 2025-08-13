# MCP Auth Test Server

This is a minimal FastAPI server to test the Model Context Protocol (MCP) authorization flow.

## Endpoints
- `/authorize`: Simulates user login and returns an authorization code.
- `/token`: Exchanges code for an access token.
- `/resource`: Protected resource, requires Bearer token.

## Usage
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the server:
   ```sh
   uvicorn main:app --reload
   ```

## Reference
- MCP Authorization Spec: https://modelcontextprotocol.io/specification/draft/basic/authorization
