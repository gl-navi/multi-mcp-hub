

github_mcp_instructions = """
This server provides analysis tools for GitHub accounts.

GITHUB TOOLS

- get_authenticated_user():
    Returns information about the currently authenticated GitHub user (based on the configured token).

- list_user_repositories():
    Lists all repositories accessible to the authenticated user, including private ones.

- get_repository_info(owner, repo):
    Retrieves detailed metadata (description, stars, forks, etc.) for a specified repository.

- list_repo_contributors(owner, repo):
    Lists contributors to the given repository along with contribution stats.

- list_repo_branches(owner, repo):
    Lists all branches in a given GitHub repository.

- get_repo_issues(owner, repo):
    Retrieves all open issues for the specified repository.

- get_repo_pull_requests(owner, repo):
    Lists all open pull requests in the specified repository.

- create_issue(owner, repo, title, body=""):
    Creates a new issue in the specified repository with the given title and optional body.

- get_commit_history(owner, repo, per_page=30):
    Retrieves the commit history for a repository, including SHA, author, and message.

- list_repo_languages(owner, repo):
    Lists programming languages used in the repository with their respective code size (bytes).

- get_file_contents(owner, repo, path, ref="main"):
    Fetches the contents of a file from the repository at the given branch (ref).
    
- get_recent_commits(owner, repo, days=7):
    Retrieves commits from the last N days (default 7), including SHA, author, date, and message.

 """
aws_mcp_instructions = """
This server provides analysis tools for AWS and GitHub accounts.

AWS S3 TOOLS

- list_s3_buckets():
    Lists all S3 buckets in your AWS account.

- get_s3_bucket_region(bucket_name):
    Returns the AWS region where the specified S3 bucket is located.

- list_objects_in_bucket(bucket_name, max_keys=10):
    Lists up to `max_keys` objects in the given S3 bucket.

- get_s3_object_data(bucket_name, object_key):
    Retrieves the raw content of a specific object (file) from an S3 bucket.

- get_s3_bucket_size_summary(bucket_name):
    Returns an estimated count of objects and total size (in bytes) for a given S3 bucket.

- get_monthly_cost_breakdown():
    Returns a service-by-service breakdown of AWS costs for the current month.

- get_total_monthly_cost_forecast():
    Forecasts total AWS spending for the current month based on usage to date.

"""