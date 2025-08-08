import requests
from typing import List, Dict, Union
from datetime import datetime, timedelta, timezone
import base64
from mcp.server.fastmcp import FastMCP
from utils.tools_utils import get_github_token  # Handles env + AWS Secrets fallback
from constants import GITHUB_API_URL

mcp = FastMCP(name="github_tools", stateless_http=True)


def get_headers() -> Dict[str, str]:
    """Returns HTTP headers required for GitHub API requests."""
    return {
        "Authorization": f"Bearer {get_github_token()}",
        "Accept": "application/vnd.github.v3+json"
    }


@mcp.tool(description="Get the authenticated GitHub user's profile data")
def get_authenticated_user() -> Union[str, dict]:
    try:
        response = requests.get(f"{GITHUB_API_URL}/user", headers=get_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="List the authenticated user's repositories")
def list_user_repositories() -> Union[List[str], str]:
    try:
        response = requests.get(f"{GITHUB_API_URL}/user/repos", headers=get_headers())
        response.raise_for_status()
        return [repo["full_name"] for repo in response.json()]
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="Get metadata about a specific GitHub repository")
def get_repository_info(owner: str, repo: str) -> Union[dict, str]:
    try:
        response = requests.get(f"{GITHUB_API_URL}/repos/{owner}/{repo}", headers=get_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="List contributors to a GitHub repository")
def list_repo_contributors(owner: str, repo: str) -> Union[List[str], str]:
    try:
        response = requests.get(f"{GITHUB_API_URL}/repos/{owner}/{repo}/contributors", headers=get_headers())
        response.raise_for_status()
        return [contrib["login"] for contrib in response.json()]
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="List branches of a GitHub repository")
def list_repo_branches(owner: str, repo: str) -> Union[List[str], str]:
    try:
        response = requests.get(f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches", headers=get_headers())
        response.raise_for_status()
        return [branch["name"] for branch in response.json()]
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="List open issues in a GitHub repository")
def get_repo_issues(owner: str, repo: str, state: str = "open") -> Union[List[str], str]:
    try:
        params = {"state": state}
        response = requests.get(f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues", headers=get_headers(), params=params)
        response.raise_for_status()
        # Filter out pull requests
        return [issue["title"] for issue in response.json() if "pull_request" not in issue]
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="List pull requests of a GitHub repository")
def get_repo_pull_requests(owner: str, repo: str, state: str = "open") -> Union[List[dict], str]:
    try:
        params = {"state": state}
        response = requests.get(f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls", headers=get_headers(), params=params)
        response.raise_for_status()
        return [{"title": pr["title"], "user": pr["user"]["login"], "state": pr["state"]} for pr in response.json()]
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="Create a new issue in a GitHub repository")
def create_issue(owner: str, repo: str, title: str, body: str = "") -> Union[dict, str]:
    try:
        payload = {"title": title, "body": body}
        response = requests.post(f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues", headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="Get commit history for a GitHub repository")
def get_commit_history(owner: str, repo: str, per_page: int = 30) -> Union[List[dict], str]:
    try:
        params = {"per_page": per_page}
        response = requests.get(f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits", headers=get_headers(), params=params)
        response.raise_for_status()
        return [
            {"sha": commit["sha"], "author": commit["commit"]["author"]["name"], "message": commit["commit"]["message"]}
            for commit in response.json()
        ]
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="List programming languages used in a GitHub repository")
def list_repo_languages(owner: str, repo: str) -> Union[dict, str]:
    try:
        response = requests.get(f"{GITHUB_API_URL}/repos/{owner}/{repo}/languages", headers=get_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="Get file contents from a GitHub repository")
def get_file_contents(owner: str, repo: str, path: str, ref: str = "main") -> Union[str, str]:
    try:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref}
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        content = response.json()["content"]
        return base64.b64decode(content).decode("utf-8")
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="Retrieve commits from the last N days for a GitHub repository")
def get_recent_commits(owner: str, repo: str, days: int = 7) -> Union[List[dict], str]:
    try:
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        params = {"since": since_date.isoformat()}
        response = requests.get(
            f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits",
            headers=get_headers(),
            params=params
        )
        response.raise_for_status()
        return [
            {
                "sha": commit["sha"],
                "author": commit["commit"]["author"]["name"],
                "date": commit["commit"]["author"]["date"],
                "message": commit["commit"]["message"]
            }
            for commit in response.json()
        ]
    except Exception as e:
        return f"Error: {str(e)}"


github_tools = list(mcp._tool_manager._tools.values())
