import contextlib
from fastapi import FastAPI
import os

from aws_mcp_server import create_gl_aws_mcp_server
from github_mcp_server import create_gl_github_mcp_server

github_mcp = create_gl_github_mcp_server()
aws_mcp = create_gl_aws_mcp_server()

# Create a combined lifespan to manage both session managers
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(github_mcp.session_manager.run())
        await stack.enter_async_context(aws_mcp.session_manager.run())
        yield


app = FastAPI(lifespan=lifespan)
app.mount("/github", github_mcp.streamable_http_app())
app.mount("/aws", aws_mcp.streamable_http_app())

PORT = os.environ.get("PORT", 10000)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
