import boto3
import json
import os
from functools import lru_cache

# Test counter
call_count = 0


# 	Secure: You can load secrets from AWS, not hardcoded in code.
# 	Efficient: @lru_cache() ensures the token is fetched only once.
# 	Portable: Can fall back to GITHUB_TOKEN env var for local/dev use.
#   Caching the token with @lru_cache() is a good practice as AWS Secrets Manager charges per retrieval

@lru_cache()
def get_github_token(
        secret_name: str = "prod/gl_mcp_server_github_token_06042026",
        region: str = "ap-northeast-1"
) -> str:
    """
    Lazily fetch and cache a GitHub token using AWS Secrets Manager.
    Falls back to environment variable GITHUB_TOKEN if present.

    Caching is handled using @lru_cache to ensure the secret is only fetched once
    during the application lifecycle, making it efficient and secure.

    Args:
        secret_name (str): The name of the secret in AWS Secrets Manager.
        region (str): AWS region where the secret is stored.

    Returns:
        str: The GitHub token.

    Raises:
        RuntimeError: If the secret cannot be fetched from AWS.
    """
    global call_count
    call_count += 1  # For test verification > counts how many times this is actually called around $0.05 per 10,000 calls

    env_token = os.getenv("GITHUB_TOKEN")
    if env_token:
        return env_token

    client = boto3.client("secretsmanager", region_name=region)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = response.get("SecretString")
        if secret and not secret.startswith("{"):
            return secret
        return json.loads(secret).get("token", "")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve GitHub token: {str(e)}")